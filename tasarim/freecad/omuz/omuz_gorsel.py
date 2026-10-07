# Omuz montaji: renkler, gorunumler, patlatilmis gorunum, hareket kareleri (FreeCAD GUI icinde calisir)
# freecad.exe <ascii baslatici> ile; FC_SCRIPT=<bu dosya>
import os, math
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gorsel")
os.makedirs(os.path.join(OUT, "kare"), exist_ok=True)
XR = 185.0
RENK = {"alu": (0.78, 0.80, 0.83), "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "siyah": (0.13, 0.13, 0.14),
        "celik": (0.50, 0.52, 0.56), "pirinc": (0.86, 0.66, 0.22), "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6)}

doc = App.openDocument(os.path.join(HERE, "omuz-montaj.FCStd"))


def Pp(phi):
    return App.Placement(V(0, 0, 0), App.Rotation(V(-1, 0, 0), phi), V(0, 0, 0))


def Pr(th):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th), V(XR, 0, 0))


def poz(phi, th):
    doc.getObject("Gobek").Placement = Pp(phi)
    doc.getObject("Kol").Placement = Pp(phi).multiply(Pr(th))


def kamera(v, eye, h, merkez):
    """Ortografik kamera: eye yonunden bakar, Y yukari, merkez noktasina odaklanir, h gorunen yukseklik (mm)."""
    z = V(*eye).normalize()
    x = V(0, 1, 0).cross(z).normalize()
    y = z.cross(x)
    v.setCameraOrientation(App.Rotation(x, y, z, "ZYX"))
    v.fitAll()
    cam = v.getCameraNode()
    pos = V(*merkez) + z * cam.focalDistance.getValue()
    cam.position.setValue(pos.x, pos.y, pos.z)
    cam.height.setValue(h)


def go():
    gd = Gui.getDocument(doc.Name)
    # betikle (GUI'siz) kaydedilen dosyada montaj ve gruplar gizli gelir; eklemlerin gorunum nesnesi de yoktur
    import JointObject
    for o in doc.Objects:
        if o.TypeId in ("Assembly::AssemblyObject", "App::Part", "Part::Feature"):
            gd.getObject(o.Name).Visibility = True
        if o.TypeId == "App::FeaturePython" and hasattr(o, "Proxy"):
            if isinstance(o.Proxy, JointObject.GroundedJoint):
                JointObject.ViewProviderGroundedJoint(o.ViewObject).attach(o.ViewObject)
            elif isinstance(o.Proxy, JointObject.Joint):
                JointObject.ViewProviderJoint(o.ViewObject).attach(o.ViewObject)
            o.ViewObject.Visibility = False
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in feats:
        vo = gd.getObject(o.Name)
        vo.ShapeColor = RENK.get(o.Renk, RENK["gri"])
        if o.Renk == "kabuk":
            vo.Transparency = 88
    v = gd.activeView()
    v.setAxisCross(False) if hasattr(v, "setAxisCross") else None
    Gui.updateGui()
    kabuk = [o for o in feats if o.Tur == "Referans"]

    # 1) genel gorunum (kabuk saydam)
    poz(0, 0)
    kamera(v, (0.75, 0.45, 1.0), 340, (120, -40, 0))
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, "omuz-genel.png"), 1400, 1000, "White")
    # yakindan, kabuksuz
    for o in kabuk:
        gd.getObject(o.Name).Visibility = False
    kamera(v, (0.8, 0.35, 1.0), 190, (150, -15, 0))
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, "omuz-yakin.png"), 1400, 1000, "White")
    # arkadan (mafsal civatasi tarafi)
    kamera(v, (0.8, 0.3, -1.0), 190, (160, -15, 0))
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, "omuz-arka.png"), 1400, 1000, "White")

    # 2) patlatilmis gorunum
    # not: doc.recompute() montaj cozucusunu calistirir ve gruplari eklemlere gore geri ceker; burada cagrilmaz
    for o in feats:
        o.Placement = App.Placement(o.Patlat, App.Rotation())
    kamera(v, (0.7, 0.45, 1.2), 500, (285, -75, 10))
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, "omuz-patlatilmis.png"), 1800, 1200, "White")
    for o in feats:
        o.Placement = App.Placement()

    # 3) hareket kareleri (kabuk saydam gorunur)
    for o in kabuk:
        gd.getObject(o.Name).Visibility = True
    seq = []
    seq += [(p, 0) for p in range(0, 121, 8)] + [(p, 0) for p in range(120, -41, -8)] + [(p, 0) for p in range(-40, 1, 8)]
    seq += [(0, t) for t in range(0, 121, 8)] + [(0, t) for t in range(120, -1, -8)]
    seq += [(p, int(p * 0.75)) for p in range(0, 121, 8)] + [(p, int(p * 0.75)) for p in range(120, -1, -8)]
    kamera(v, (0.55, 0.3, 1.0), 430, (175, -55, 35))
    for k, (phi, th) in enumerate(seq):
        poz(phi, th)
        Gui.updateGui()
        v.saveImage(os.path.join(OUT, "kare", "k%03d.png" % k), 720, 540, "White")
    with open(os.path.join(OUT, "kare", "pozlar.txt"), "w") as f:
        for phi, th in seq:
            f.write("%d %d\n" % (phi, th))

    poz(0, 0)
    kamera(v, (0.75, 0.45, 1.0), 340, (120, -40, 0))
    doc.save()
    App.closeDocument(doc.Name)
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, go)
