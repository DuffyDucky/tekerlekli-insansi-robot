# Kafa modulu gorselleri, Lale 1,58 m (10,1 in QLED kafa; FreeCAD GUI icinde calisir):
#   FC_SCRIPT=<bu dosya> freecad.exe %USERPROFILE%\.robot-cad\run_fc.py
# kafa_montaj.py'den SONRA. kafa-montaj.FCStd'nin GECICI KOPYASINI acar (depodaki dosya degismez, kaydedilmez); renkler
# parcanin Renk ozelliginden. Baglam icin traversin orta bolumu ve kabuk ust kapagi halkasi (R62 delikli, sema) eklenir.
# Gorseller: izometrik, on (yuz), yan, arka, boyun mekanizmasi yakin (on / arka), pan ekseni kesiti (+ yakin), tilt ekseni
# kesiti, kafa ici yerlesim ve kablo/fis zarflari (kafa_parcalar.ZARF), pan/tilt pozlari (arayuz.KAFA araliginda), patlatilmis.
# F1a P1.6 (08.11.2026): 125 cm kafa adlari (tek parca "Yuz kabugu (on)", "Kablo demeti (gosterim)", "Vizor") ve kamera
# merkezleri 158 kafasina gore yenilendi; doc.save() kaldirildi. Log %TEMP%\kafa_gorsel.log.
import os, sys, json, shutil, traceback, tempfile
sys.dont_write_bytecode = True
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
KABUK_ON = ("Yuz kabugu (on)", "Arka kafa kabugu")                 # sag + sol yarilar (1,58 m kafada dikey bolunmus)
YUZ_ON = ("Yuz ekrani", "Kamera Raspberry", "Ekran tirnagi", "Tirnak civatasi", "Kamera vidasi", "Kopuk bant (tirnak",
          "Isil gomme somun M3 (tirnak", "Kabuk civatasi", "Isil gomme somun M3 (kafa")
BOYUN_GORUNUR = ("Kafa iskeleti", "Tilt horn", "625ZZ", "Yanak-horn", "Pim ")   # boyun yakin planda kafa grubundan kalanlar
POZ = ((45, 0, (0.6, 0.35, 1.0)), (-60, 10, (0.6, 0.35, 1.0)), (0, 13, (1, 0.1, 0.25)), (0, -13, (1, 0.1, 0.25)), (90, 0, (0.3, 0.6, 1.0)))


def log(*a):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


KOPYA = os.path.join(tempfile.gettempdir(), "kafa-montaj-gorsel-kopya.FCStd")
shutil.copyfile(os.path.join(HERE, "kafa-montaj.FCStd"), KOPYA)
doc = App.openDocument(KOPYA)
AN = json.load(open(os.path.join(HERE, "kafa-analiz.json"), encoding="utf-8"))


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
    v = gd.activeView()
    v.setAnimationEnabled(False)
    v.setCameraType("Orthographic")
    for o in doc.Objects:
        if o.TypeId in ("App::Part", "Part::Feature", "Assembly::AssemblyObject"):
            gd.getObject(o.Name).Visibility = True
        if o.TypeId == "Assembly::JointGroup":
            gd.getObject(o.Name).Visibility = False
    par = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    for o in par:
        gd.getObject(o.Name).ShapeColor = RENK.get(getattr(o, "Renk", "gri"), RENK["gri"])
        if getattr(o, "Tur", "") == "Referans":
            gd.getObject(o.Name).Visibility = False
    grp = {o.Name: o for o in doc.Objects if o.TypeId == "App::Part"}
    kafa_par = set(o.Name for o in grp["Kafa"].Group if o.TypeId == "Part::Feature")
    log("parca", len(par), "kafa grubu", len(kafa_par), "gruplar", sorted(grp))
    Gui.updateGui()

    def sec(onekler):
        return [o for o in par if o.Label.startswith(tuple(onekler))]

    def gor(ls, ac):
        for o in ls:
            gd.getObject(o.Name).Visibility = ac

    kabuklar = sec(KABUK_ON)
    log("kabuk", [o.Label for o in kabuklar])
    if len(kabuklar) != 4:
        raise RuntimeError("kabuk yarilari bulunamadi: %s" % [o.Label for o in kabuklar])

    # --- baglam (kaydedilmez): traversin orta bolumu (sigma, yerel y -40...0) + kabuk ust kapagi halkasi (sema, kafa-analiz r62)
    ek = []
    tr = OL.sigma_x(-110.0, 110.0)
    tr.translate(V(0, -20.0, 0))
    o = doc.addObject("Part::Feature", "Baglam_traverse")
    o.Shape = tr
    gd.getObject(o.Name).ShapeColor = (0.70, 0.72, 0.76)
    ek.append(o)
    ky0, ky1 = AN["r62"]["kapak_y_yerel"]
    kap = Part.makeCylinder(150.0, ky1 - ky0, V(0, ky0, 0), V(0, 1, 0)).cut(
        Part.makeCylinder(AN["r62"]["aciklik_r"], ky1 - ky0 + 2, V(0, ky0 - 1, 0), V(0, 1, 0)))
    o = doc.addObject("Part::Feature", "Baglam_kapak")
    o.Shape = kap
    gd.getObject(o.Name).ShapeColor = (0.90, 0.91, 0.93)
    gd.getObject(o.Name).Transparency = 55
    ek.append(o)
    Gui.updateGui()

    YT, ZT = KP.YT, KP.ZT
    M = (0, 135, 10)                                   # modul ortasi (traverse ustu ... kafa tepesi)

    # 1) genel gorunumler (ev pozu)
    kamera(v, (0.9, 0.5, 1.0), 430, M)
    kaydet(v, "kafa-izometrik.png", 1100, 1200)
    kamera(v, (0, 0, 1), 400, (0, 130, 0))
    kaydet(v, "kafa-on.png", 1100, 1150)
    kamera(v, (1, 0, 0), 400, (0, 130, 0))
    kaydet(v, "kafa-yan.png", 1100, 1150)
    kamera(v, (-0.7, 0.35, -1.0), 430, M)
    kaydet(v, "kafa-arka.png", 1100, 1200)

    # 2) boyun mekanizmasi yakin plan: kafa grubundan yalniz iskelet (yari saydam), tilt horn'u, 625ZZ ve pim kalir
    gizli = [o for o in par if o.Name in kafa_par and not o.Label.startswith(BOYUN_GORUNUR)]
    gor(gizli, False)
    isk = sec(("Kafa iskeleti",))[0]
    gd.getObject(isk.Name).Transparency = 60
    kamera(v, (0.85, 0.45, 1.0), 300, (0, 115, 10))
    kaydet(v, "kafa-boyun-yakin.png", 1200, 1200)
    kamera(v, (-0.85, 0.35, -0.8), 300, (0, 115, 10))
    kaydet(v, "kafa-boyun-yakin-arka.png", 1200, 1200)
    gd.getObject(isk.Name).Transparency = 0
    gor(gizli, True)

    # 3) kafa ici yerlesim: kabuklar saydam, yer ayirma zarflari (fis, kablo yolu, fan yeri) kirmizi yari saydam
    zek = []
    for k, z_ in enumerate(KP.ZARF):
        o = doc.addObject("Part::Feature", "Zarf_%02d" % k)
        o.Shape = z_["shape"]
        gd.getObject(o.Name).ShapeColor = RENK["kablo"]
        gd.getObject(o.Name).Transparency = 45
        zek.append(o)
    for o in kabuklar:
        gd.getObject(o.Name).Transparency = 80
    gor(sec(("Yuz ekrani",)), False)
    kamera(v, (-0.9, 0.45, -0.7), 330, (0, YT + 10, ZT - 10))
    kaydet(v, "kafa-kablo-yolu.png", 1200, 1100)
    kamera(v, (0, 1, 0.0001), 300, (0, YT, ZT - 10))
    kaydet(v, "kafa-yerlesim-ust.png", 1200, 1100)
    gor(sec(("Yuz ekrani",)), True)
    for o in zek:
        doc.removeObject(o.Name)
    for o in kabuklar:
        gd.getObject(o.Name).Transparency = 0

    # 4) kesitler: (a) pan ekseni, x <= 0 yarisi +X'ten; (b) tilt ekseni, z <= ZT yarisi +Z'den
    for ad, kutu, eye, merkez, h in (
            ("kafa-kesit-pan.png", Part.makeBox(400, 600, 400, V(-400, -100, -200)), (1, 0, 0), (0, 135, 0), 400),
            ("kafa-kesit-pan-yakin.png", Part.makeBox(400, 600, 400, V(-400, -100, -200)), (1, 0, 0), (0, 60, 0), 150),
            ("kafa-kesit-tilt.png", Part.makeBox(400, 600, 400, V(-200, -100, ZT - 400)), (0, 0, 1), (0, 150, 0), 360)):
        gizle, yeni = [], []
        for o in par + ek:
            if not gd.getObject(o.Name).Visibility:
                continue
            gd.getObject(o.Name).Visibility = False
            gizle.append(o)
            try:
                s_ = o.Shape.copy()
                s_.Placement = o.getGlobalPlacement()
                c = s_.common(kutu)
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

    # 5) pan / tilt pozlari (grup yerlesimi dogrudan; recompute yok). Tilt arayuz.KAFA araliginda (+-13)
    for psi, th, eye in POZ:
        grp["Pan"].Placement = KP.grup_yer("Pan", psi, th)
        grp["Kafa"].Placement = KP.grup_yer("Kafa", psi, th)
        kamera(v, eye, 430, M)
        kaydet(v, "kafa-poz-pan%+03d-tilt%+03d.png" % (psi, th), 1000, 1100)
    grp["Pan"].Placement = App.Placement()
    grp["Kafa"].Placement = App.Placement()

    # 6) patlatilmis: yalniz kafa modulu parcalari (Patlat ozelligi kadar kaydirilmis)
    for o in ek:
        gd.getObject(o.Name).Visibility = False
    for o in par:                        # kendi yerlesimi korunur (STEP'ten gelen parcalarin Placement'i birim degil)
        o.Placement = App.Placement(o.Patlat, App.Rotation()).multiply(o.Placement)
    Gui.updateGui()
    v.viewIsometric()
    v.fitAll()
    bb = App.BoundBox()
    for o in par:
        if gd.getObject(o.Name).Visibility:
            s_ = o.Shape.copy()
            s_.Placement = o.getGlobalPlacement()
            bb.add(s_.BoundBox)
    kamera(v, (0.9, 0.45, 1.0), 1.15 * max(bb.YLength, 0.8 * bb.XLength), (bb.Center.x, bb.Center.y, bb.Center.z))
    kaydet(v, "kafa-patlatilmis.png", 1100, 1500)
    App.closeDocument(doc.Name)          # kopya; yerlesim ve ek nesneler kaydedilmez
    try:
        os.remove(KOPYA)                 # yalniz bu betigin TEMP'e yazdigi kopya
    except Exception:
        pass
    log("BITTI")
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
