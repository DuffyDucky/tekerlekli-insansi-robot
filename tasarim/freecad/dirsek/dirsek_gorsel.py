# Dirsek modulu gorselleri (FreeCAD GUI icinde calisir): FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>
# dirsek_montaj.py'den SONRA. Dosyaya renk/gorunurluk yazip kaydeder; sonra baglam icin sag omuzu (omuz_parcalar, ayni
# yerel koordinat) ekleyip gorunumleri alir: izometrik, on, yan, patlatilmis, dirsek eklemi yakin plan + eksen kesiti,
# dirsek acisi pozlari (0 / 45 / 90 / 105), bilek pozu. Ek nesneler ve pozlar kaydedilmez. Gecici log %TEMP%'te.
import os, sys, traceback, tempfile
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore
from pivy import coin  # noqa  getCameraNode icin

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
OUT = os.path.join(HERE, "gorsel")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(tempfile.gettempdir(), "dirsek_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "celik": (0.50, 0.52, 0.56), "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13),
        "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22), "kabuk": (0.90, 0.91, 0.93), "gri": (0.6, 0.6, 0.6)}


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


doc = App.openDocument(os.path.join(HERE, "dirsek-montaj.FCStd"))


def kamera(v, eye, h, merkez):
    """Ortografik kamera: eye yonunden bakar, Y yukari, merkez noktasina odaklanir, h gorunen yukseklik (mm)."""
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
    for p in (HERE, UST, os.path.join(UST, "omuz")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import dirsek_parcalar as DP
    import omuz_parcalar as O
    gd = Gui.getDocument(doc.Name)
    for o in doc.Objects:
        if o.TypeId in ("App::Part", "Part::Feature", "Assembly::AssemblyObject"):
            gd.getObject(o.Name).Visibility = True
    par = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in par:
        gd.getObject(o.Name).ShapeColor = RENK.get(o.Renk, RENK["gri"])
    grp = {o.Name: o for o in doc.Objects if o.TypeId == "App::Part"}
    v = gd.activeView()
    Gui.updateGui()
    doc.save()           # renk ve gorunurluk dosyaya

    # --- baglam: sag omuz (ayni yerel koordinat; kaydedilmez). Kol grubu (ust kol tupu + catal) tam renk, gerisi saydam
    omz = []
    for k, p in enumerate(O.P):
        if p["tur"] == "Referans":
            continue
        o = doc.addObject("Part::Feature", "Omuz_%03d" % k)
        o.Shape = p["shape"]
        vo = gd.getObject(o.Name)
        vo.ShapeColor = RENK.get(p["renk"], RENK["gri"])
        if p["grup"] != "Kol":
            vo.Transparency = 55
        omz.append((o, p["grup"]))
    Gui.updateGui()

    # 1) genel gorunumler (ev pozu)
    kamera(v, (0.9, 0.45, 1.0), 400, (172, -175, 0))
    kaydet(v, "dirsek-izometrik.png", 1000, 1300)
    kamera(v, (0, 0, 1), 400, (150, -150, 0))
    kaydet(v, "dirsek-on.png", 900, 1250)
    kamera(v, (1, 0, 0), 400, (190, -150, 0))
    kaydet(v, "dirsek-yan.png", 900, 1250)
    kamera(v, (-0.6, 0.25, -1.0), 260, (190, -215, 0))
    kaydet(v, "dirsek-arka.png", 1100, 1300)

    # 2) dirsek eklemi yakin plan: catal yari saydam (rulman, pim, servo ve horn gorunur)
    catal = next(o for o in par if o.Label == "Dirsek catali")
    onkol = next(o for o in par if o.Label == "On kol govdesi")
    gd.getObject(catal.Name).Transparency = 65
    for o, g in omz:
        gd.getObject(o.Name).Visibility = False
    kamera(v, (0.75, 0.35, 1.0), 120, (190, -170, 0))
    kaydet(v, "dirsek-eklem-yakin.png", 1200, 1000)
    kamera(v, (-0.8, 0.3, 0.9), 120, (180, -170, 0))
    kaydet(v, "dirsek-eklem-yakin-ic.png", 1200, 1000)
    gd.getObject(catal.Name).Transparency = 0

    # 3) eksen kesiti: z <= dirsek ekseni yarisi, +Z'den bakis (catal, 625ZZ, pim, yanak, servo, horn, bilek)
    import Part
    kutu = Part.makeBox(600, 600, 300, V(-100, -500, DP.ZE - 300))
    gizle, ek = [], []
    for o in par + [x for x, _ in omz if _ == "Kol"]:
        bb = o.Shape.BoundBox
        gd.getObject(o.Name).Visibility = False
        gizle.append(o)
        if bb.ZMin >= DP.ZE:
            continue
        try:
            c = o.Shape.common(kutu)
        except Exception:
            continue
        if c.Volume > 1e-3:
            n = doc.addObject("Part::Feature", "Kesit_%s" % o.Name)
            n.Shape = c
            gd.getObject(n.Name).ShapeColor = gd.getObject(o.Name).ShapeColor
            ek.append(n)
    kamera(v, (0, 0, 1), 205, (190, -190, 0))
    kaydet(v, "dirsek-kesit.png", 1000, 1300)
    kamera(v, (0, 0, 1), 95, (190, -165, 0))
    kaydet(v, "dirsek-kesit-eklem.png", 1200, 1000)
    for n in ek:
        doc.removeObject(n.Name)
    for o in gizle:
        gd.getObject(o.Name).Visibility = True
    for o, g in omz:
        gd.getObject(o.Name).Visibility = True

    # 4) dirsek acisi pozlari (yan bakis, omuz ev pozunda) + bilek pozu
    for al in (0, 45, 90, 105):
        grp["OnKol"].Placement = DP.Pe(al)
        grp["El"].Placement = DP.Pe(al)
        kamera(v, (1, 0.12, 0.25), 400, (190, -150, 45))
        kaydet(v, "dirsek-poz-%03d.png" % al, 900, 1000)
    grp["OnKol"].Placement = DP.Pe(90)
    grp["El"].Placement = DP.Pe(90).multiply(DP.Pb(90))
    kamera(v, (0.8, 0.5, 1.0), 330, (190, -160, 60))
    kaydet(v, "dirsek-poz-090-bilek90.png", 1000, 1000)
    grp["OnKol"].Placement = App.Placement()
    grp["El"].Placement = App.Placement()

    # 5) patlatilmis: yalniz dirsek parcalari
    for o, g in omz:
        gd.getObject(o.Name).Visibility = False
    for o in par:
        o.Placement = App.Placement(o.Patlat, App.Rotation())
    kamera(v, (0.9, 0.45, 1.0), 430, (185, -260, -10))
    kaydet(v, "dirsek-patlatilmis.png", 1100, 1400)
    App.closeDocument(doc.Name)          # yerlesim ve ek nesneler kaydedilmez
    Gui.getMainWindow().close()


def guvenli():
    try:
        go()
    except Exception:
        log(traceback.format_exc())
        try:
            App.closeDocument(doc.Name)
        except Exception:
            pass
        Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
