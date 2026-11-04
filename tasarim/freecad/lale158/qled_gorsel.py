# Lale 1,58 m - QLED kafa + gogus cercevesi gorselleri (FreeCAD GUI): kafa on, yan kesit (x 0, x 85), kafa arkasi acik (kart / kablo zarflari), gogus cerceve yakin + kesit, tam robot on + uc ceyrek.
# FC_SCRIPT=<bu dosya> freecad.exe run_fc.py   kafa_montaj, kabuk_montaj, ana_montaj'dan sonra. Dosya kaydedilmez. Zarflar kafa/kafa-zarf.brep (kafa_montaj yazar). Log %TEMP%\qled_gorsel.log.
import os, sys, tempfile, traceback, json
import FreeCAD as App
import FreeCADGui as Gui
import Part
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
LOG = os.path.join(tempfile.gettempdir(), "qled_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22), "siyah": (0.13, 0.13, 0.14),
        "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22), "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6), "pcb": (0.15, 0.45, 0.25)}
Z_RENK = {"HDMI": (0.85, 0.15, 0.15), "Touch": (0.15, 0.35, 0.9), "Power": (0.95, 0.75, 0.05), "Kablo": (0.6, 0.3, 0.8), "Tabla": (0.6, 0.3, 0.8), "Hub": (0.15, 0.6, 0.9), "Fan": (0.1, 0.75, 0.75)}


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
    par = []
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
            par.append(o)
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

    def sec(*on):
        return [o for o in par if o.Label.startswith(on)]

    def gizle(ls):
        for o in ls:
            gd.getObject(o.Name).Visibility = False

    def goster(ls):
        for o in ls:
            gd.getObject(o.Name).Visibility = True

    Y0 = A.KAFA["taban_y"]
    ZT = A.KAFA["tilt_nokta"][2]
    yb = Y0 + A.KAFA["kafa_alt_y"]
    yk = yb + 107.5                     # kafa kabugu ortasi
    # ---- tam robot
    kamera(v, (0, 0, 1), 1700, (0, 790, 0)); kaydet(v, "qc-robot-on.png", 1000, 1500)
    kamera(v, (0.7, 0.4, 1.0), 1800, (0, 790, 0)); kaydet(v, "qc-robot-uc-ceyrek.png", 1100, 1500)
    # ---- kafa on
    kamera(v, (0, 0, 1), 300, (0, yk, 0)); kaydet(v, "qled-kafa-on.png", 1200, 1100)
    kamera(v, (0.75, 0.25, 0.9), 400, (0, yk, ZT)); kaydet(v, "qled-kafa-uc-ceyrek.png", 1200, 1100)
    # ---- zarflar
    js = json.load(open(os.path.join(UST, "kafa", "kafa-analiz.json"), encoding="utf-8"))["qled"]["zarf"]
    br = Part.read(os.path.join(UST, "kafa", "kafa-zarf.brep"))
    zo = []
    for z_, s_ in zip(js, br.Solids):
        s2 = s_.copy()
        s2.translate(V(0, Y0, 0))
        o = doc.addObject("Part::Feature", "Zarf%d" % len(zo))
        o.Shape = s2
        vo = gd.getObject(o.Name)
        vo.ShapeColor = Z_RENK.get(z_["ad"].split()[0], (0.6, 0.3, 0.8))
        vo.Transparency = 45
        zo.append(o)
    Gui.updateGui()
    # ---- kafa arkasi acik (arka kabuk gizli): kart, kablo zarflari, Pi, tabla, hub, SY8205, fan yeri
    ark = sec("Arka kafa kabugu") + [o for o in par if o.Label.startswith(("Kabuk civatasi", "Isil gomme somun M3 (kafa")) and "arka" in o.Label]
    gizle(ark)
    Gui.updateGui()
    kamera(v, (-0.25, 0.3, -1.0), 330, (0, yk, ZT)); kaydet(v, "qled-kafa-arka-acik.png", 1300, 1100)
    # ---- ekran arkasi: iskelet, Pi, tabla ustu ve boyun da gizli
    icler = [o for o in par if o.Label.startswith(("Kafa iskeleti", "Raspberry", "Burc M2,5", "Vida M2,5", "Tabla civatasi", "5 V cevirici", "MAX98357A", "SY8205", "TVS P6KE", "USB Hub", "USB ses", "PAM8403", "Kopuk bant (5", "Kopuk bant (MAX", "Kopuk bant (SY", "Kopuk bant (TVS", "Kopuk bant (USB", "Kopuk bant (PAM", "Tilt horn", "625ZZ", "Yanak-horn"))]
    pan = [o for o in par if o.Label.startswith(("Egme catali", "Tilt servosu", "Boyun yukseltme", "Boyun mili", "Saplama", "Pul M3 (saplama", "Somun M3 DIN 985 (saplama", "Pim ", "Isil gomme somun M5", "Isil gomme somun M3 (mil", "Servo yuvasi", "Rulman yuvasi", "Pan ", "6808", "Boyun plakasi"))]
    gizle(icler + pan)
    Gui.updateGui()
    kamera(v, (0, 0.05, -1.0), 300, (0, yk, ZT)); kaydet(v, "qled-kafa-ekran-arkasi.png", 1300, 1100)
    goster(icler + pan + ark)
    Gui.updateGui()
    # ---- kesitler
    sg = v.getSceneGraph()

    def kesit(nx, d):
        cp = coin.SoClipPlane()
        cp.plane.setValue(coin.SbPlane(coin.SbVec3f(nx, 0, 0), d))
        sg.insertChild(cp, 0)
        Gui.updateGui()
        return cp

    gizle(zo)
    cp = kesit(-1, 0.5)
    kamera(v, (1, 0, 0), 290, (0, yk, ZT - 15)); kaydet(v, "qled-kafa-kesit-x0.png", 1200, 1200)
    sg.removeChild(cp)
    cp = kesit(-1, -A.KAFA["ekran"]["tirnak"]["x"])
    kamera(v, (1, 0, 0), 290, (0, yk, ZT - 15)); kaydet(v, "qled-kafa-kesit-x85-tirnak.png", 1200, 1200)
    kamera(v, (1, 0, 0), 60, (0, yk - 13.9 + 79.0, ZT + 40)); kaydet(v, "qled-tirnak-yakin.png", 1000, 1000)
    sg.removeChild(cp)
    # ---- gogus cercevesi
    yc = A.GOGUS_EKRAN_Y
    zc = A.gogus_z(yc)
    kamera(v, (0, 0.26, 0.97), 330, (0, yc, zc)); kaydet(v, "cerceve-on.png", 1300, 1000)
    c15, s15 = 0.9659, 0.2588
    kx, ky = 125.0, 80.0
    kamera(v, (0, 0.26, 0.97), 70, (kx, yc + ky * c15, zc - ky * s15)); kaydet(v, "cerceve-kose-yakin.png", 1000, 1000)
    kamera(v, (0.5, 0.35, 0.9), 110, (kx, yc + ky * c15, zc - ky * s15)); kaydet(v, "cerceve-kose-uc-ceyrek.png", 1000, 1000)
    cp = kesit(-1, -120.0)                 # x = 120: civata + flans; kasa + takoz disinda
    kamera(v, (1, 0, 0), 260, (0, yc, zc - 30)); kaydet(v, "cerceve-kesit-x120.png", 1100, 1100)
    kamera(v, (1, 0, 0), 40, (0, yc + 96 * c15, zc - 96 * s15 - 5)); kaydet(v, "cerceve-kesit-x120-yakin.png", 1000, 1000)
    sg.removeChild(cp)
    cp = kesit(-1, -138.0)                 # x = 138: kose takozu kesiti
    kamera(v, (1, 0, 0), 40, (0, yc + 90 * c15, zc - 90 * s15 - 5)); kaydet(v, "cerceve-kesit-x138-takoz.png", 1000, 1000)
    sg.removeChild(cp)
    cp = kesit(-1, 0.5)
    kamera(v, (1, 0, 0), 420, (0, yc, zc - 60)); kaydet(v, "cerceve-kesit-x0-tasiyici.png", 1100, 1100)
    sg.removeChild(cp)
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
