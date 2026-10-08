# Kafa modulu gorselleri (FreeCAD GUI icinde calisir): FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>
# kafa_montaj.py'den SONRA. Dosyaya renk/gorunurluk yazip kaydeder; sonra baglam icin traversin ust bolumu ve kabuk ust
# kapagi halkasi (R62 delikli, sema) eklenir: izometrik, on (yuz), yan, arka, patlatilmis, boyun mekanizmasi yakin plan,
# pan ekseni kesiti, tilt ekseni kesiti, kablo yolu, pan/tilt pozlari. Ek nesneler ve pozlar kaydedilmez. Log %TEMP%'te.
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
LOG = os.path.join(tempfile.gettempdir(), "kafa_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "celik": (0.50, 0.52, 0.56), "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13),
        "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22), "kabuk": (0.90, 0.91, 0.93), "gri": (0.6, 0.6, 0.6),
        "vizor": (0.05, 0.06, 0.08), "pcb": (0.10, 0.45, 0.20), "kablo": (0.85, 0.15, 0.15)}


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


doc = App.openDocument(os.path.join(HERE, "kafa-montaj.FCStd"))


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
    for p in (HERE, UST):
        if p not in sys.path:
            sys.path.insert(0, p)
    import kafa_parcalar as KP
    import ortak_lib as OL
    import Part
    gd = Gui.getDocument(doc.Name)
    for o in doc.Objects:
        if o.TypeId in ("App::Part", "Part::Feature", "Assembly::AssemblyObject"):
            gd.getObject(o.Name).Visibility = True
    par = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in par:
        gd.getObject(o.Name).ShapeColor = RENK.get(o.Renk, RENK["gri"])
        if o.Tur == "Referans":
            gd.getObject(o.Name).Visibility = False
    grp = {o.Name: o for o in doc.Objects if o.TypeId == "App::Part"}
    v = gd.activeView()
    Gui.updateGui()
    doc.save()           # renk ve gorunurluk dosyaya

    def bul(ad):
        return next(o for o in par if o.Label == ad)
    kabuklar = [bul("Yuz kabugu (on)"), bul("Arka kafa kabugu")]
    kablo = bul("Kablo demeti (gosterim)")

    # --- baglam (kaydedilmez): traversin orta bolumu (sigma, yerel y -40...0) + kabuk ust kapagi halkasi (sema)
    ek = []
    tr = OL.sigma_x(-110.0, 110.0)
    tr.translate(V(0, -20.0, 0))
    o = doc.addObject("Part::Feature", "Baglam_traverse")
    o.Shape = tr
    gd.getObject(o.Name).ShapeColor = (0.70, 0.72, 0.76)
    ek.append(o)
    y0 = 975.0
    kap = Part.makeCylinder(150.0, 3.0, V(0, 982.0 - y0, 0), V(0, 1, 0)).cut(Part.makeCylinder(62.0, 5.0, V(0, 980.0 - y0, 0), V(0, 1, 0)))
    o = doc.addObject("Part::Feature", "Baglam_kapak")
    o.Shape = kap
    gd.getObject(o.Name).ShapeColor = (0.90, 0.91, 0.93)
    gd.getObject(o.Name).Transparency = 55
    ek.append(o)
    Gui.updateGui()

    # 1) genel gorunumler (ev pozu)
    kamera(v, (0.9, 0.5, 1.0), 360, (0, 140, 10))
    kaydet(v, "kafa-izometrik.png", 1100, 1200)
    kamera(v, (0, 0, 1), 340, (0, 140, 0))
    kaydet(v, "kafa-on.png", 1000, 1150)
    kamera(v, (1, 0, 0), 340, (0, 140, 10))
    kaydet(v, "kafa-yan.png", 1000, 1150)
    kamera(v, (-0.7, 0.35, -1.0), 360, (0, 140, 10))
    kaydet(v, "kafa-arka.png", 1100, 1200)

    # 2) boyun mekanizmasi yakin plan: kabuk, LCD, vizor, kamera gizli; kafa iskeleti yari saydam
    gizli = kabuklar + [bul("Yuz ekrani Waveshare 7in HDMI LCD (C)"), bul("Vizor (siyah akrilik)"),
                        bul("Kamera Raspberry Pi Camera Module 3")] + [o for o in par if o.Label in ("Kabuk civatasi M3x8 ISO 7380",
                        "LCD civatasi M3x6 ISO 7380", "Kamera vidasi M2x8 PT", "Isil gomme somun M3 (LCD boss)")]
    for o in gizli:
        gd.getObject(o.Name).Visibility = False
    isk = bul("Kafa iskeleti")
    gd.getObject(isk.Name).Transparency = 60
    kamera(v, (0.85, 0.45, 1.0), 230, (0, 105, 10))
    kaydet(v, "kafa-boyun-yakin.png", 1200, 1200)
    kamera(v, (-0.85, 0.35, -0.8), 230, (0, 105, 10))
    kaydet(v, "kafa-boyun-yakin-arka.png", 1200, 1200)
    gd.getObject(isk.Name).Transparency = 0

    # 3) kablo yolu: kabuklar saydam, kablo demeti gorunur
    for o in gizli:
        gd.getObject(o.Name).Visibility = True
    for o in kabuklar:
        gd.getObject(o.Name).Transparency = 75
    gd.getObject(kablo.Name).Visibility = True
    kamera(v, (-0.9, 0.35, 0.7), 340, (0, 120, 0))
    kaydet(v, "kafa-kablo-yolu.png", 1100, 1250)
    gd.getObject(kablo.Name).Visibility = False
    for o in kabuklar:
        gd.getObject(o.Name).Transparency = 0

    # 4) kesitler: (a) pan ekseni, x <= 0 yarisi +X'ten; (b) tilt ekseni, z <= ZT yarisi +Z'den
    for ad, kutu, eye, merkez, h in (
            ("kafa-kesit-pan.png", Part.makeBox(400, 500, 400, V(-400, -100, -200)), (1, 0, 0), (0, 130, 10), 330),
            ("kafa-kesit-pan-yakin.png", Part.makeBox(400, 500, 400, V(-400, -100, -200)), (1, 0, 0), (0, 70, 0), 140),
            ("kafa-kesit-tilt.png", Part.makeBox(400, 500, 400, V(-200, -100, KP.ZT - 400)), (0, 0, 1), (0, 120, 0), 260)):
        gizle, yeni = [], []
        for o in par + ek:
            if not gd.getObject(o.Name).Visibility:
                continue
            gd.getObject(o.Name).Visibility = False
            gizle.append(o)
            try:
                c = o.Shape.common(kutu)
            except Exception:
                continue
            if c.Volume > 1e-3:
                n = doc.addObject("Part::Feature", "Kesit_%s" % o.Name)
                n.Shape = c
                gd.getObject(n.Name).ShapeColor = gd.getObject(o.Name).ShapeColor
                yeni.append(n)
        kamera(v, eye, h, merkez)
        kaydet(v, ad, 1100, 1250 if h > 200 else 1100)
        for n in yeni:
            doc.removeObject(n.Name)
        for o in gizle:
            gd.getObject(o.Name).Visibility = True

    # 5) pan / tilt pozlari (grup yerlesimi dogrudan; recompute yok)
    for psi, th, eye in ((45, 0, (0.6, 0.35, 1.0)), (-60, 20, (0.6, 0.35, 1.0)), (0, 30, (1, 0.1, 0.25)), (0, -25, (1, 0.1, 0.25)),
                         (90, 0, (0.3, 0.6, 1.0))):
        grp["Pan"].Placement = KP.grup_yer("Pan", psi, th)
        grp["Kafa"].Placement = KP.grup_yer("Kafa", psi, th)
        kamera(v, eye, 360, (0, 140, 10))
        kaydet(v, "kafa-poz-pan%+03d-tilt%+03d.png" % (psi, th), 1000, 1100)
    grp["Pan"].Placement = App.Placement()
    grp["Kafa"].Placement = App.Placement()

    # 6) patlatilmis: yalniz kafa parcalari
    for o in ek:
        gd.getObject(o.Name).Visibility = False
    for o in par:
        o.Placement = App.Placement(o.Patlat, App.Rotation())
    kamera(v, (0.9, 0.45, 1.0), 560, (0, 200, 30))
    kaydet(v, "kafa-patlatilmis.png", 1100, 1500)
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
