# Iskelet montaji: renkler, gorunumler, baglanti yakin planlari, patlatilmis gorunum, omuzlarla birlikte gorunum
# (FreeCAD GUI icinde calisir): FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>
import os, sys
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore
from pivy import coin  # noqa  getCameraNode icin SWIG sarmalayicisini yukler

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
OUT = os.path.join(HERE, "gorsel")
os.makedirs(OUT, exist_ok=True)
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22),
        "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22),
        "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6)}

doc = App.openDocument(os.path.join(HERE, "iskelet-montaj.FCStd"))


def kamera(v, eye, h, merkez):
    """Ortografik kamera: eye yonunden bakar, Y yukari, merkez noktasina odaklanir, h gorunen yukseklik (mm)."""
    z = V(*eye).normalize()
    up = V(0, 1, 0) if abs(z.y) < 0.99 else V(0, 0, -1)
    x = up.cross(z).normalize()
    y = z.cross(x)
    # setCameraOrientation animasyonlu: yon bir sonraki kareye kayiyordu. Yon dogrudan kamera dugumune yazilir.
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


def go():
    gd = Gui.getDocument(doc.Name)
    for o in doc.Objects:
        if o.TypeId in ("App::Part", "Part::Feature"):
            gd.getObject(o.Name).Visibility = True
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in feats:
        gd.getObject(o.Name).ShapeColor = RENK.get(o.Renk, RENK["gri"])
    v = gd.activeView()
    Gui.updateGui()

    # 1) genel gorunumler
    # dikey (portre) goruntude kamera yuksekligi genislige gore olceklenir; h degerleri buna gore secildi
    kamera(v, (0.85, 0.55, 1.0), 800, (0, 500, 0))
    kaydet(v, "iskelet-izometrik.png", 1000, 1300)
    kamera(v, (0, 0, 1), 600, (0, 520, 0))
    kaydet(v, "iskelet-on.png", 800, 1300)
    kamera(v, (1, 0, 0), 600, (0, 520, 0))
    kaydet(v, "iskelet-yan.png", 800, 1300)

    # 2) baglanti yakin planlari (sigma yari saydam)
    sig = [o for o in feats if o.Kod.startswith("Sigma")]
    kamera(v, (0.75, 0.55, 1.0), 120, (38, 160, 0))
    kaydet(v, "detay-direk-ray.png", 1000, 800)
    kamera(v, (0.75, -0.45, 1.0), 120, (38, 915, 0))
    kaydet(v, "detay-direk-travers.png", 1000, 800)
    for o in sig:
        gd.getObject(o.Name).Transparency = 70
    kamera(v, (-0.45, 0.75, 0.6), 95, (88, 114.5, 12))
    kaydet(v, "detay-sase-ic-kose.png", 1000, 800)
    kamera(v, (0.55, 0.45, 1.0), 95, (42, 128, 0))
    kaydet(v, "detay-direk-ray-kesit.png", 1000, 800)
    for o in sig:
        gd.getObject(o.Name).Transparency = 0

    # 3) patlatilmis gorunum (recompute cagrilmaz)
    for o in feats:
        o.Placement = App.Placement(o.Patlat, App.Rotation())
    kamera(v, (0.85, 0.55, 1.0), 1050, (0, 600, 0))
    kaydet(v, "iskelet-patlatilmis.png", 1100, 1400)
    kamera(v, (0.8, 0.6, 1.0), 380, (60, 190, 0))
    kaydet(v, "iskelet-patlatilmis-taban.png", 1300, 1000)
    for o in feats:
        o.Placement = App.Placement()
    kamera(v, (0.85, 0.55, 1.0), 1080, (0, 520, 0))
    Gui.updateGui()
    doc.save()

    # 4) iskelet + sag omuz + aynali sol omuz (arayuz.MODULLER yerlesimiyle)
    for p in (UST, os.path.join(UST, "omuz")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import arayuz as A
    import omuz_parcalar as O
    for (ad, (konum, ayna)) in (("sag", A.modul_konum("omuz_sag")), ("sol", A.modul_konum("omuz_sol"))):
        for k, p in enumerate(O.P):
            if p["ad"].startswith("Omuz traversi") or p["tur"] == "Referans":
                continue
            s = p["shape"].mirror(V(0, 0, 0), V(1, 0, 0)) if ayna else p["shape"].copy()
            m = App.Matrix()
            m.move(V(*konum))
            s.transformShape(m, True)
            o = doc.addObject("Part::Feature", "Omuz_%s_%03d" % (ad, k))
            o.Shape = s
            gd.getObject(o.Name).ShapeColor = RENK.get(p["renk"], RENK["gri"])
    kamera(v, (0.6, 0.35, 1.0), 1150, (0, 560, 0))
    kaydet(v, "iskelet-omuzlar.png", 1300, 1300)
    kamera(v, (0, 0, 1), 420, (0, 880, 0))
    kaydet(v, "iskelet-omuzlar-on.png", 1300, 800)
    App.closeDocument(doc.Name)     # omuz parcalari dosyaya kaydedilmez
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, go)
