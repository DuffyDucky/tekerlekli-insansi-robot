# Taban modulu gorselleri (FreeCAD GUI icinde calisir): FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>
# taban_montaj.py'den SONRA. Dosyaya renk/gorunurluk yazip kaydeder; baglam icin iskelet (STEP) ve kabuk eteği (kabuk STEP'inden
# y < 300 katilari) eklenir (kaydedilmez): izometrik, ust (kabuk + katlar gizli), yan, alt, patlatilmis, elektronik kati, guc paneli,
# aku, teker grubu, sonar, kablo yolu; sonra ana montaj (robot-montaj.FCStd) acilip taban eklenerek tam robot onizlemesi. Log %TEMP%'te.
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
LOG = os.path.join(tempfile.gettempdir(), "taban_gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.62, 0.65, 0.70), "celik": (0.50, 0.52, 0.56), "siyah": (0.13, 0.13, 0.14),
        "pirinc": (0.86, 0.66, 0.22), "ahsap": (0.85, 0.70, 0.48), "motor": (0.35, 0.37, 0.40), "lastik": (0.10, 0.10, 0.11),
        "aku": (0.20, 0.42, 0.75), "petg": (0.96, 0.55, 0.13), "naylon": (0.95, 0.95, 0.90), "pcb_k": (0.70, 0.12, 0.12),
        "pcb_m": (0.10, 0.30, 0.65), "pcb_y": (0.10, 0.45, 0.20), "koyu": (0.22, 0.22, 0.24), "kirmizi": (0.85, 0.10, 0.10),
        "k_kirmizi": (0.95, 0.05, 0.05), "k_siyah": (0.05, 0.05, 0.05), "k_turuncu": (1.0, 0.50, 0.0), "k_sari": (0.95, 0.85, 0.05),
        "k_mavi": (0.10, 0.45, 1.0), "k_yesil": (0.05, 0.75, 0.20), "k_mor": (0.60, 0.20, 0.80), "k_beyaz": (0.92, 0.92, 0.92),
        "gri": (0.6, 0.6, 0.6)}


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


doc = App.openDocument(os.path.join(HERE, "taban-montaj.FCStd"))


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
    v = gd.activeView()
    Gui.updateGui()
    doc.save()           # renk ve gorunurluk dosyaya

    def gor(liste, deger):
        for o in liste:
            gd.getObject(o.Name).Visibility = deger

    def bas(*on):
        return [o for o in par if any(o.Label.startswith(k) for k in on)]
    ref = [o for o in par if o.Tur == "Referans"]
    katlar = bas("Elektronik kati (on)", "Guc paneli (arka kat)")

    # --- baglam (kaydedilmez): iskelet (STEP), kabuk eteği (kabuk STEP'inden y < 300 katilari)
    isk = Part.read(os.path.join(UST, "iskelet", "iskelet-montaj.step"))
    o_isk = doc.addObject("Part::Feature", "Baglam_iskelet")
    o_isk.Shape = isk
    gd.getObject(o_isk.Name).ShapeColor = RENK["alu"]
    kb = Part.read(os.path.join(UST, "kabuk", "kabuk-montaj.step"))
    etek = [s for s in kb.Solids if s.BoundBox.YMax < 300.0]
    o_et = doc.addObject("Part::Feature", "Baglam_etek")
    o_et.Shape = Part.makeCompound(etek)
    gd.getObject(o_et.Name).ShapeColor = (0.90, 0.91, 0.93)
    gd.getObject(o_et.Name).Transparency = 70
    # iskeletin yalniz sase + direk alt bolumu (y < 420)
    o_isk.Shape = Part.makeCompound([s for s in isk.Solids if s.BoundBox.YMin < 420.0]).common(Part.makeBox(800, 420, 800, V(-400, 0, -400)))
    Gui.updateGui()
    log("baglam etek kati", len(etek))

    # 1) genel gorunumler
    kamera(v, (0.9, 0.55, 1.0), 640, (0, 150, 0))
    kaydet(v, "taban-izometrik.png", 1300, 1000)
    gd.getObject(o_et.Name).Visibility = False
    kamera(v, (0.9, 0.55, 1.0), 600, (0, 130, 0))
    kaydet(v, "taban-izometrik-eteksiz.png", 1300, 1000)
    gor(katlar, False)
    kamera(v, (0, 1, 0), 600, (0, 120, 0))
    kaydet(v, "taban-ust.png", 1000, 1150)
    gor(katlar, True)
    gd.getObject(o_et.Name).Visibility = True
    kamera(v, (1, 0, 0), 330, (0, 150, 0))
    kaydet(v, "taban-yan.png", 1300, 800)
    kamera(v, (0, 0, 1), 330, (0, 150, 0))
    kaydet(v, "taban-on.png", 1300, 800)
    gd.getObject(o_et.Name).Visibility = False
    kamera(v, (0.35, -1, 0.25), 620, (0, 80, 0))
    kaydet(v, "taban-alt.png", 1100, 1100)

    # 2) elektronik kati + guc paneli yakin plan (etek gizli, iskelet direk ustu kesik)
    kamera(v, (0.55, 0.85, 0.75), 330, (0, 190, 80))
    kaydet(v, "taban-elektronik-kati.png", 1200, 1000)
    kamera(v, (-0.55, 0.85, -0.75), 330, (0, 190, -150))
    kaydet(v, "taban-guc-paneli.png", 1200, 1000)

    # 3) aku + kayis + takoz (katlar gizli), teker grubu yakin plan
    gor(katlar, False)
    gor(bas("Sigorta kutusu", "Role", "Ana sigorta", "Civata M4x16 (sigorta", "Civata M4x16 (role", "Pul M4 (sigorta", "Pul M4 (role",
            "Somun M4"), False)
    kamera(v, (-0.8, 0.7, -0.9), 330, (0, 130, -120))
    kaydet(v, "taban-aku-yakin.png", 1200, 1000)
    gor(katlar, True)
    gor(bas("Sigorta kutusu", "Role", "Ana sigorta", "Civata M4x16 (sigorta", "Civata M4x16 (role", "Pul M4 (sigorta", "Pul M4 (role",
            "Somun M4"), True)
    kamera(v, (1.0, -0.15, 0.55), 260, (150, 70, 185))
    kaydet(v, "taban-teker-yakin.png", 1200, 1000)
    gd.getObject(o_isk.Name).Transparency = 60
    gor(bas("Teker 125 x 58 (on sag)"), False)
    kamera(v, (1.0, -0.35, 0.35), 200, (120, 75, 185))
    kaydet(v, "taban-motor-braket-yakin.png", 1200, 1000)
    gor(bas("Teker 125 x 58 (on sag)"), True)
    gd.getObject(o_isk.Name).Transparency = 0
    # sonar yakin plan (etek yari saydam)
    gd.getObject(o_et.Name).Visibility = True
    kamera(v, (0.45, 0.25, 1.0), 260, (0, 115, 250))
    kaydet(v, "taban-sonar-yakin.png", 1300, 900)
    gd.getObject(o_et.Name).Visibility = False

    # 4) kablo yolu: Referans gorunur, katlar yari saydam
    gor(ref, True)
    for o in katlar:
        gd.getObject(o.Name).Transparency = 70
    kamera(v, (0.8, 0.75, 0.9), 640, (0, 170, 0))
    kaydet(v, "taban-kablo-yolu.png", 1300, 1000)
    gd.getObject(o_isk.Name).Visibility = False
    o_isk2 = doc.addObject("Part::Feature", "Baglam_iskelet_tam")
    o_isk2.Shape = isk
    gd.getObject(o_isk2.Name).ShapeColor = RENK["alu"]
    gd.getObject(o_isk2.Name).Transparency = 50
    kamera(v, (-0.9, 0.35, -0.8), 1250, (0, 560, 0))
    kaydet(v, "taban-kablo-yolu-direk.png", 900, 1400)
    doc.removeObject(o_isk2.Name)
    gd.getObject(o_isk.Name).Visibility = True
    gor(ref, False)
    for o in katlar:
        gd.getObject(o.Name).Transparency = 0

    # 6) tam robot onizleme: ana montaj + taban (sekiller patlatma sifirlandiktan sonra alinir)
    for o in par:
        o.Placement = App.Placement()
    Gui.updateGui()
    gd.getObject(o_isk.Name).Visibility = False
    gd.getObject(o_et.Name).Visibility = False
    # 5) patlatilmis
    for o in par:
        o.Placement = App.Placement(o.Patlat, App.Rotation())
    kamera(v, (0.9, 0.6, 1.0), 1000, (0, 200, 0))
    kaydet(v, "taban-patlatilmis.png", 1300, 1200)
    for o in par:
        o.Placement = App.Placement()

    sekiller = [(o.Shape.copy(), gd.getObject(o.Name).ShapeColor) for o in par if o.Tur != "Referans"]
    App.closeDocument(doc.Name)          # yerlesim ve ek nesneler kaydedilmez
    rd = App.openDocument(os.path.join(UST, "montaj", "robot-montaj.FCStd"))
    rg = Gui.getDocument(rd.Name)
    for o in rd.Objects:
        try:
            if o.TypeId in ("App::Part", "Part::Feature", "Assembly::AssemblyObject"):
                rg.getObject(o.Name).Visibility = True
            elif o.TypeId in ("App::FeaturePython", "Assembly::JointGroup") or "Joint" in o.TypeId:
                rg.getObject(o.Name).Visibility = False
        except Exception:
            pass
    renkli = {}
    for sh, c in sekiller:
        renkli.setdefault(tuple(round(x, 3) for x in c[:3]), []).append(sh)
    for k, (c, shs) in enumerate(renkli.items()):
        o = rd.addObject("Part::Feature", "Taban_%02d" % k)
        o.Shape = Part.makeCompound(shs)
        rg.getObject(o.Name).ShapeColor = c
    rv = rg.activeView()
    Gui.updateGui()
    kamera(rv, (0.9, 0.35, 1.0), 1400, (0, 640, 0))
    kaydet(rv, "robot-tam-izometrik.png", 1000, 1400)
    kamera(rv, (1, 0, 0), 1380, (0, 640, 0))
    kaydet(rv, "robot-tam-yan.png", 900, 1400)
    kamera(rv, (-0.9, 0.35, -1.0), 1400, (0, 640, 0))
    kaydet(rv, "robot-tam-arka.png", 1000, 1400)
    App.closeDocument(rd.Name)           # ana montaja dokunulmaz (kaydedilmez)
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
