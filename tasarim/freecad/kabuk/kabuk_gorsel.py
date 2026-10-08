# Kabuk modulu gorselleri (FreeCAD GUI icinde calisir): FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>
# kabuk_montaj.py'den SONRA. Dosyaya renk/gorunurluk yazip kaydeder; sonra iskelet + iki omuzu (arayuz.MODULLER
# yerlesimiyle) ekleyip gorunumleri alir: izometrik, on, yan, arka (kapak acik), kesit (x = 0), patlatilmis (her baski
# parcasi ayri renk), Nextion yuvasi yakin plan, iskelete baglanti yakin planlari. Ek nesneler kaydedilmez.
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
LOG = os.path.join(tempfile.gettempdir(), "kabuk_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22),
        "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22),
        "kabuk": (0.90, 0.91, 0.93), "gri": (0.6, 0.6, 0.6)}
# baski parcalari icin ayirt edici renkler (patlatilmis gorunum)
PALET = {"k01": (0.89, 0.35, 0.29), "k02": (0.95, 0.61, 0.25), "k03": (0.96, 0.82, 0.30), "k04": (0.55, 0.77, 0.33),
         "k05": (0.25, 0.66, 0.47), "k06": (0.22, 0.67, 0.73), "k07": (0.27, 0.51, 0.82), "k08": (0.47, 0.40, 0.80),
         "k09": (0.71, 0.40, 0.78), "k10": (0.87, 0.42, 0.62), "k11": (0.62, 0.45, 0.33), "k12": (0.45, 0.62, 0.62),
         "k13": (0.80, 0.55, 0.45), "k14": (0.55, 0.60, 0.25), "k15": (0.35, 0.45, 0.60), "k16": (0.70, 0.70, 0.40)}


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


doc = App.openDocument(os.path.join(HERE, "kabuk-montaj.FCStd"))


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


def kaydet(v, ad, w=1400, h=1000):
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, ad), w, h, "White")
    log("gorsel", ad)


def go():
    gd = Gui.getDocument(doc.Name)
    for o in doc.Objects:
        if o.TypeId in ("App::Part", "Part::Feature"):
            gd.getObject(o.Name).Visibility = True
    kab = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in kab:
        gd.getObject(o.Name).ShapeColor = RENK.get(o.Renk, RENK["gri"])
    v = gd.activeView()
    Gui.updateGui()
    doc.save()           # renk ve gorunurluk dosyaya

    # --- iskelet + iki omuz (kaydedilmez)
    for p in (UST, os.path.join(UST, "omuz"), os.path.join(UST, "iskelet")):
        if p not in sys.path:
            sys.path.insert(0, p)
    import arayuz as A
    import iskelet_parcalar as I
    import omuz_parcalar as O
    dis = []
    for k, p in enumerate(I.P):
        o = doc.addObject("Part::Feature", "Isk_%03d" % k)
        o.Shape = p["shape"]
        gd.getObject(o.Name).ShapeColor = RENK.get(p["renk"], RENK["gri"])
        dis.append(o)
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
            dis.append(o)
    Gui.updateGui()

    # 1) genel gorunumler
    kamera(v, (0.85, 0.5, 1.0), 1200, (0, 560, 0))
    kaydet(v, "kabuk-izometrik.png", 1000, 1300)
    kamera(v, (0, 0, 1), 1150, (0, 560, 0))
    kaydet(v, "kabuk-on.png", 900, 1300)
    kamera(v, (1, 0, 0), 1150, (0, 560, 0))
    kaydet(v, "kabuk-yan.png", 900, 1300)

    # 2) arka: servis kapagi acik (disari cekilmis)
    kapak = next(o for o in kab if o.Label == "Arka servis kapagi")
    kapak_vida = [o for o in kab if "arka kapak" in o.Label and o.Label.startswith("Bindirme")]
    for o in [kapak] + kapak_vida:
        o.Placement = App.Placement(V(0, 0, -140), App.Rotation())
    kamera(v, (-0.45, 0.25, -1.0), 760, (0, 600, -60))
    kaydet(v, "kabuk-arka-kapak-acik.png", 1100, 1300)
    for o in [kapak] + kapak_vida:
        o.Placement = App.Placement()

    # 3) kesit x = 0 (sol yari): parcalarin x <= 0 kismi, +X'ten bakis
    import Part
    kesit_kutu = Part.makeBox(4000, 4000, 4000, V(-4000, -2000, -2000))
    tum = kab + dis
    gizle = []
    eklenen = []
    for o in tum:
        bb = o.Shape.BoundBox
        if bb.XMin >= -1e-6:
            gd.getObject(o.Name).Visibility = False
            gizle.append(o)
            continue
        if bb.XMax <= 0:
            continue
        try:
            c = o.Shape.common(kesit_kutu)
        except Exception:
            continue
        gd.getObject(o.Name).Visibility = False
        gizle.append(o)
        if c.Volume > 1e-3:
            n = doc.addObject("Part::Feature", "Kesit_%s" % o.Name)
            n.Shape = c
            gd.getObject(n.Name).ShapeColor = gd.getObject(o.Name).ShapeColor
            eklenen.append(n)
    kamera(v, (1, 0, 0), 1150, (0, 560, 0))
    kaydet(v, "kabuk-kesit.png", 900, 1300)
    kamera(v, (1, 0.05, 0.12), 330, (0, 830, 30))
    kaydet(v, "kabuk-kesit-gogus.png", 1200, 1000)
    for n in eklenen:
        doc.removeObject(n.Name)
    for o in gizle:
        gd.getObject(o.Name).Visibility = True

    # 4) Nextion yuvasi: on yakin plan + icten (gogus parcalarinin on yarisi, arkadan bakis)
    kamera(v, (0.25, 0.25, 1.0), 380, (0, 820, 90))
    kaydet(v, "kabuk-nextion-on.png", 1300, 1000)
    gogus = [o for o in kab if o.Label.startswith("Gogus bandi") or o.Label.startswith("Omuz bandi")]
    ekran_ilgili = [o for o in kab if "ekran" in o.Label.lower() or o.Label.startswith("Nextion")]
    on_kutu = Part.makeBox(4000, 4000, 4000, V(-2000, -2000, 35))
    for o in tum:
        gd.getObject(o.Name).Visibility = False
    eklenen = []
    for o in gogus:
        n = doc.addObject("Part::Feature", "On_%s" % o.Name)
        n.Shape = o.Shape.common(on_kutu)
        gd.getObject(n.Name).ShapeColor = PALET.get(o.BaskiRenk, RENK["kabuk"])
        eklenen.append(n)
    for o in ekran_ilgili:
        gd.getObject(o.Name).Visibility = True
    kamera(v, (0.35, 0.3, -1.0), 360, (0, 815, 70))
    kaydet(v, "kabuk-nextion-ic.png", 1300, 1000)
    for n in eklenen:
        doc.removeObject(n.Name)
    for o in tum:
        gd.getObject(o.Name).Visibility = True

    # 5) iskelete baglanti yakin planlari (kabuk yari saydam)
    baski = [o for o in kab if o.Tur == "Baski"]
    for o in baski:
        gd.getObject(o.Name).Transparency = 72
    kamera(v, (0.9, 0.45, 0.75), 190, (85, 805, 0))
    kaydet(v, "kabuk-baglanti-govde.png", 1200, 900)
    kamera(v, (0.8, 0.6, 0.9), 150, (165, 128, 175))
    kaydet(v, "kabuk-baglanti-etek.png", 1200, 900)
    kamera(v, (0.75, 0.35, 1.0), 260, (120, 920, 30))
    kaydet(v, "kabuk-omuz-duvari.png", 1200, 900)
    for o in baski:
        gd.getObject(o.Name).Transparency = 0

    # 6) patlatilmis: yalniz kabuk parcalari, her baski parcasi ayri renk
    for o in dis:
        gd.getObject(o.Name).Visibility = False
    for o in kab:
        o.Placement = App.Placement(o.Patlat, App.Rotation())
        if o.Tur == "Baski":
            gd.getObject(o.Name).ShapeColor = PALET.get(o.BaskiRenk, RENK["kabuk"])
    kamera(v, (0.85, 0.5, 1.0), 1450, (0, 560, 0))
    kaydet(v, "kabuk-patlatilmis.png", 1200, 1400)
    kamera(v, (0, 0, 1), 1400, (0, 560, 0))
    kaydet(v, "kabuk-patlatilmis-on.png", 1100, 1400)
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
