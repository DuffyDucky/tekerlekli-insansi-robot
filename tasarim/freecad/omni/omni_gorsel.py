# On omni teker + gobek adaptoru gorselleri (FreeCAD GUI icinde): FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>
# omni_kontrol.py'den SONRA (omni-montaj.FCStd'yi acar, kaydetmez). Gruplar (Lale.Grup): Kose (on iki kose: donen grup + motor + braket),
# Baglam (sag on ceyrek + arka sag kose), Etek / Iskelet (STEP'ten yakin katilar), Kesit (aks duzleminde kesik sag on kose). Log %TEMP%.
import os, sys, traceback, tempfile
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore
from pivy import coin  # noqa

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gorsel")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(tempfile.gettempdir(), "omni_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.62, 0.65, 0.70), "celik": (0.50, 0.52, 0.56), "siyah": (0.13, 0.13, 0.14),
        "pirinc": (0.86, 0.66, 0.22), "ahsap": (0.85, 0.70, 0.48), "motor": (0.35, 0.37, 0.40), "lastik": (0.10, 0.10, 0.11),
        "aku": (0.20, 0.42, 0.75), "petg": (0.96, 0.55, 0.13), "naylon": (0.95, 0.95, 0.90), "pcb_k": (0.70, 0.12, 0.12),
        "pcb_m": (0.10, 0.30, 0.65), "pcb_y": (0.10, 0.45, 0.20), "koyu": (0.22, 0.22, 0.24), "kirmizi": (0.85, 0.10, 0.10),
        "gri": (0.6, 0.6, 0.6), "etek": (0.90, 0.91, 0.93)}
OMNI_GOVDE = (0.72, 0.74, 0.78)     # aluminyum govde (makaralar ayni katida: tek renk, gosterim)


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


doc = App.openDocument(os.path.join(HERE, "omni-montaj.FCStd"))


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


def kaydet(v, ad, w=1200, h=1000):
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, ad), w, h, "White")
    log("gorsel", ad)


def go():
    gd = Gui.getDocument(doc.Name)
    par = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in par:
        g = gd.getObject(o.Name)
        g.ShapeColor = RENK.get(o.Renk, RENK["gri"])
        if o.Label.startswith("Omni teker") or o.Label.startswith("Kesit: Omni teker"):
            g.ShapeColor = (0.16, 0.16, 0.17)
        g.Visibility = o.Grup != "Kesit"
        if o.Grup == "Etek":
            g.Transparency = 65
    v = gd.activeView()
    Gui.updateGui()

    def sec(f):
        return [o for o in par if f(o)]

    def gor(liste, d):
        for o in liste:
            gd.getObject(o.Name).Visibility = d

    etek = sec(lambda o: o.Grup == "Etek")
    isk = sec(lambda o: o.Grup == "Iskelet")
    kesit = sec(lambda o: o.Grup == "Kesit")
    sag_on = sec(lambda o: o.Grup == "Kose" and "on sag" in o.Label)
    sol_on = sec(lambda o: o.Grup == "Kose" and "on sol" in o.Label)
    baglam = sec(lambda o: o.Grup == "Baglam")
    arka = sec(lambda o: o.Grup == "Baglam" and "arka sag" in o.Label)

    # 1) sag on kose, izometrik (etek yari saydam)
    kamera(v, (0.9, 0.5, 1.0), 330, (185, 80, 170))
    kaydet(v, "omni-izometrik.png", 1300, 1000)
    # 2) on gorunus: on aks (iki omni), etek yari saydam
    gor(arka, False)
    kamera(v, (0, 0, 1), 300, (0, 85, 185))
    kaydet(v, "omni-on.png", 1500, 820)
    # 3) yan gorunus: on omni + arka lastik (etek gizli)
    gor(arka, True)
    gor(etek, False)
    kamera(v, (1, 0, 0), 280, (200, 75, 0))
    kaydet(v, "omni-yan.png", 1500, 700)
    gor(etek, True)
    # 4) kesit: aks duzlemi (z = 185), sag on kose; onden bakis
    gor(sag_on, False)
    gor(arka, False)
    gor(kesit, True)
    gor(etek, False)
    gor(isk, False)
    for o in baglam:
        gd.getObject(o.Name).Transparency = 75
    kamera(v, (0, 0, 1), 120, (198, 62.5, 185))
    kaydet(v, "omni-kesit.png", 1400, 1000)
    kamera(v, (0.35, 0.25, 1.0), 140, (198, 62.5, 185))
    kaydet(v, "omni-kesit-ceyrek.png", 1300, 1000)
    gor(kesit, False)
    gor(sag_on, True)
    gor(arka, True)
    for o in baglam:
        gd.getObject(o.Name).Transparency = 0
    # 5) teker dis yuzu (M3 civatalar, M4 eksenel vida gobek deliginde, fici makaralar)
    gor(baglam, False)
    gor(sol_on, False)
    kamera(v, (1.0, 0.35, 0.45), 165, (205, 62.5, 185))
    kaydet(v, "omni-teker-dis.png", 1200, 1000)
    # 6) teker gizli: adaptor + kaplin + motor + braket (motor tarafindan ve disaridan)
    tek = sec(lambda o: o.Label.startswith("Omni teker") and "on sag" in o.Label)
    m3 = sec(lambda o: o.Grup == "Kose" and "on sag" in o.Label and ("Civata M3x35" in o.Label or "Pul M3" in o.Label))
    gor(tek + m3, False)
    kamera(v, (1.0, 0.45, 0.6), 110, (192, 62.5, 185))
    kaydet(v, "omni-adaptor-dis.png", 1200, 1000)
    kamera(v, (-0.25, 0.35, 1.0), 110, (185, 62.5, 185))
    kaydet(v, "omni-adaptor-motor.png", 1200, 1000)
    gor(tek + m3, True)
    # 7) patlatilmis (sag on kose)
    for o in sag_on:
        o.Placement = App.Placement(o.Patlat * 0.8, App.Rotation())
    gor(etek + isk, False)
    kamera(v, (0.75, 0.45, 1.0), 270, (285, 45, 205))
    kaydet(v, "omni-patlatilmis.png", 1500, 1000)
    for o in sag_on:
        o.Placement = App.Placement()
    App.closeDocument(doc.Name)          # kaydedilmez
    Gui.getMainWindow().close()


def guvenli():
    try:
        go()
    except Exception:
        log(traceback.format_exc())
        for d in list(App.listDocuments().values()):
            try:
                App.closeDocument(d.Name)
            except Exception:
                pass
        Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
