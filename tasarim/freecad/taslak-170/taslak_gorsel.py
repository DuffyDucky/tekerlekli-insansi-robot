# Lale 1,70 m taslak: GUI kurulumu + gorseller (FreeCAD GUI icinde calisir; taslak_montaj.py'den SONRA)
#   FC_SCRIPT=<bu dosya> "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecad.exe" C:/Users/Victus/.robot-cad/run_fc.py
# 1) taslak-170.FCStd: gizli gelen montaj/gruplar/parcalar gorunur, renkler, eklem gorunum nesneleri; dosya GUI'den kaydedilir.
# 2) %TEMP%/taslak170-gorsel.FCStd (renk bazinda bilesik, yeni + eski 125 cm): onden, yandan, izometrik, kafa yakin, sag kol yakin,
#    karsilastirma, dirsek catali (catal-5-7.png ya da catal-5-7-8.png) -> gorsel/
import os, sys, math, tempfile, traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore
from pivy import coin  # noqa

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gorsel")
os.makedirs(OUT, exist_ok=True)
GORSEL_DOC = os.path.join(tempfile.gettempdir(), "taslak170-gorsel.FCStd")
LOG = os.path.join(tempfile.gettempdir(), "taslak170-gorsel.log")
open(LOG, "w").close()
RENK = {"alu": (0.78, 0.80, 0.83), "alu2": (0.55, 0.60, 0.68), "celik": (0.50, 0.52, 0.56), "celik2": (0.86, 0.66, 0.22),
        "siyah": (0.13, 0.13, 0.14), "petg": (0.96, 0.55, 0.13), "petg2": (0.18, 0.52, 0.86), "pirinc": (0.86, 0.66, 0.22),
        "kabuk": (0.85, 0.87, 0.90), "gri": (0.6, 0.6, 0.6), "pcb": (0.10, 0.45, 0.25), "pcb_k": (0.10, 0.45, 0.25),
        "pcb_m": (0.15, 0.30, 0.60), "ahsap": (0.80, 0.65, 0.45), "aku": (0.25, 0.30, 0.35), "kirmizi": (0.85, 0.15, 0.12),
        "koyu": (0.25, 0.25, 0.28), "lastik": (0.10, 0.10, 0.10), "motor": (0.62, 0.64, 0.68), "naylon": (0.92, 0.92, 0.88),
        "vizor": (0.05, 0.05, 0.07), "kablo": (0.9, 0.3, 0.2)}


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


def kaydet(v, ad, w=1400, h=1000):
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, ad), w, h, "White")
    log("gorsel", ad)


def montaj_dosyasi():
    import JointObject
    doc = App.openDocument(os.path.join(HERE, "taslak-170.FCStd"))
    gd = Gui.getDocument(doc.Name)
    for o in doc.Objects:
        if o.TypeId in ("Assembly::AssemblyObject", "App::Part", "Part::Feature"):
            gd.getObject(o.Name).Visibility = True
        if o.TypeId == "Part::Feature":
            gd.getObject(o.Name).ShapeColor = RENK.get(getattr(o, "Renk", "gri"), RENK["gri"])
    n = 0
    for o in doc.Objects:
        if o.TypeId == "App::FeaturePython" and hasattr(o, "Proxy"):
            if isinstance(o.Proxy, JointObject.GroundedJoint):
                JointObject.ViewProviderGroundedJoint(o.ViewObject).attach(o.ViewObject)
            elif isinstance(o.Proxy, JointObject.Joint):
                JointObject.ViewProviderJoint(o.ViewObject).attach(o.ViewObject)
                o.ViewObject.Proxy.redrawJointPlacements(o)
                n += 1
            o.ViewObject.Visibility = True
    Gui.updateGui()
    doc.save()
    log("montaj dosyasi kaydedildi, eklem gorunumu", n)
    App.closeDocument(doc.Name)


def gorseller():
    doc = App.openDocument(GORSEL_DOC)
    gd = Gui.getDocument(doc.Name)
    Gui.activateView("Gui::View3DInventor", True)
    v = Gui.activeDocument().activeView()
    v.setCameraType("Orthographic")
    for o in doc.Objects:
        vo = gd.getObject(o.Name)
        vo.ShapeColor = RENK.get(o.Renk, RENK["gri"])
        vo.Visibility = True
        if o.Renk in ("celik", "pirinc"):
            vo.LineWidth = 1.0
    yeni = [o for o in doc.Objects if o.Takim == "Yeni"]
    eski = [o for o in doc.Objects if o.Takim == "Eski"]
    kesit = [o for o in doc.Objects if o.Takim == "Kesit"]

    def goster(liste):
        for o in doc.Objects:
            gd.getObject(o.Name).Visibility = o in liste

    goster(yeni)
    kamera(v, (0, 0, 1), 1850, (0, 850, 0))
    kaydet(v, "taslak-on.png", 1100, 1400)
    kamera(v, (1, 0, 0), 1850, (0, 850, 0))
    kaydet(v, "taslak-yan.png", 1100, 1400)
    kamera(v, (0.8, 0.45, 1.0), 1900, (0, 860, 0))
    kaydet(v, "taslak-izometrik.png", 1100, 1400)
    kamera(v, (0.75, 0.35, 1.0), 520, (0, 1560, 20))
    kaydet(v, "taslak-kafa.png", 1200, 1000)
    kamera(v, (-0.9, 0.25, -0.6), 520, (0, 1560, -20))
    kaydet(v, "taslak-kafa-arka.png", 1200, 1000)
    kamera(v, (1.0, 0.15, 0.35), 620, (190, 1195, 0))
    kaydet(v, "taslak-kol.png", 1000, 1200)
    kamera(v, (0.9, 0.2, 0.5), 700, (0, 720, 0))
    kaydet(v, "taslak-govde-uzatma.png", 1200, 1000)
    goster(kesit)
    kamera(v, (0.55, 0.15, 1.0), 1250, (0, 860, 0))
    kaydet(v, "taslak-govde-kesit.png", 1100, 1400)
    goster(yeni + eski)
    kamera(v, (0, 0, 1), 1900, (-450, 850, 0))
    kaydet(v, "karsilastirma-125-170-on.png", 1600, 1250)
    kamera(v, (0.35, 0.2, 1.0), 1950, (-450, 860, 0))
    kaydet(v, "karsilastirma-125-170-izo.png", 1600, 1250)
    catal_karsilastirma(doc, gd, v, goster)
    App.closeDocument(doc.Name)


def catal_karsilastirma(doc, gd, v, goster):
    """Dirsek catali dis kolu karsilastirmasi (sag kol; catal kirmizi, horn civatalari gri, cevre yari saydam), ayni kadraj:
    yalniz Catal5 + Catal7 -> gorsel/catal-5-7.png (2 x 2: satir once / sonra, sutun onden / izometrik; 24 Ekim kaydi);
    3+ takim (8 mm karari: Catal5, Catal7, Catal8) -> gorsel/catal-5-7-8.png (sutun = kalinlik, satir = onden / izometrik).
    Basliklar nesnelerin Baslik ozelliginden ("kalinlik|civata")."""
    from PySide import QtGui
    takim = {}
    for o in doc.Objects:
        t = getattr(o, "Takim", "")
        if t.startswith("Catal") and t != "CatalCevre":
            takim.setdefault(t, []).append(o)
    cev = [o for o in doc.Objects if getattr(o, "Takim", "") == "CatalCevre"]
    sira = sorted(takim, key=lambda t: float(t[5:]))
    if len(sira) < 2 or not cev:
        log("catal karsilastirma nesneleri yok")
        return
    for o in cev:
        gd.getObject(o.Name).Transparency = 72
    for t in sira:
        for o in takim[t]:
            vo = gd.getObject(o.Name)
            vo.ShapeColor = (0.86, 0.12, 0.10) if o.Renk == "kirmizi" else RENK["celik"]
            vo.LineWidth = 2.0
    W, H = 900, 820
    gorus = (("önden", (0, 0, 1), 250, (205, 1200, 0)), ("izometrik", (1.0, 0.42, 0.85), 250, (205, 1200, 0)))
    karo = {}
    for etiket in sira:
        goster(cev + takim[etiket])
        for ad, eye, h, mer in gorus:
            kamera(v, eye, h, mer)
            Gui.updateGui()
            yol = os.path.join(tempfile.gettempdir(), "catal-%s-%s.png" % (etiket, "on" if ad == "önden" else "izo"))
            v.saveImage(yol, W, H, "White")
            karo[(etiket, ad)] = yol

    def bilgi(etiket):
        b = next((getattr(o, "Baslik", "") for o in takim[etiket] if getattr(o, "Baslik", "")), "")
        return b.split("|") if "|" in b else (etiket[5:], "")

    baslik = 56
    f = QtGui.QFont("Segoe UI", 20)
    f.setBold(True)
    if len(sira) == 2:                       # 24 Ekim duzeni (catal-5-7.png)
        img = QtGui.QImage(2 * W, 2 * (H + baslik), QtGui.QImage.Format_RGB32)
        img.fill(QtGui.QColor(255, 255, 255))
        pt = QtGui.QPainter(img)
        pt.setFont(f)
        t1, c1 = bilgi(sira[1])
        yazilar = ((sira[0], "Önce: dış kol %s mm" % bilgi(sira[0])[0]),
                   (sira[1], "Sonra: dış kol %s mm (dışa +%g mm, horn cıvatası %s)" % (t1, float(t1) - float(bilgi(sira[0])[0]), c1)))
        for r, (etiket, yazi) in enumerate(yazilar):
            for c, (ad, _, _, _) in enumerate(gorus):
                x0, y0 = c * W, r * (H + baslik)
                pt.drawImage(x0, y0 + baslik, QtGui.QImage(karo[(etiket, ad)]))
                pt.setPen(QtGui.QColor(30, 30, 30))
                pt.drawText(x0 + 18, y0 + 38, "%s  -  %s" % (yazi, ad))
        pt.setPen(QtGui.QPen(QtGui.QColor(180, 180, 180), 2))
        pt.drawLine(W, 0, W, img.height())
        pt.drawLine(0, H + baslik, img.width(), H + baslik)
        dosya = "catal-%s.png" % "-".join(t[5:] for t in sira)
    else:                                    # sutun = kalinlik, satir = gorus (catal-5-7-8.png)
        n = len(sira)
        img = QtGui.QImage(n * W, 2 * (H + baslik), QtGui.QImage.Format_RGB32)
        img.fill(QtGui.QColor(255, 255, 255))
        pt = QtGui.QPainter(img)
        pt.setFont(f)
        for c, etiket in enumerate(sira):
            t_, civ = bilgi(etiket)
            for r, (ad, _, _, _) in enumerate(gorus):
                x0, y0 = c * W, r * (H + baslik)
                pt.drawImage(x0, y0 + baslik, QtGui.QImage(karo[(etiket, ad)]))
                pt.setPen(QtGui.QColor(30, 30, 30))
                pt.drawText(x0 + 18, y0 + 38, "Dış kol %s mm, %s  -  %s" % (t_, civ, ad))
        pt.setPen(QtGui.QPen(QtGui.QColor(180, 180, 180), 2))
        for c in range(1, n):
            pt.drawLine(c * W, 0, c * W, img.height())
        pt.drawLine(0, H + baslik, img.width(), H + baslik)
        dosya = "catal-%s.png" % "-".join(t[5:] for t in sira)
    pt.end()
    img.save(os.path.join(OUT, dosya))
    for yol in karo.values():
        try:
            os.remove(yol)
        except OSError:
            pass
    for o in cev:
        gd.getObject(o.Name).Transparency = 0
    log("gorsel", dosya)


def guvenli():
    try:
        montaj_dosyasi()
    except Exception:
        log(traceback.format_exc())
    try:
        gorseller()
    except Exception:
        log(traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
