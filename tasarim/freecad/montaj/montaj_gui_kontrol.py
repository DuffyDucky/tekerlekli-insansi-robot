# Ana montaj: GUI'de taze acilis kontrolu (FreeCAD GUI icinde calisir; montaj_gorsel.py'den SONRA).
# FC_SCRIPT=<bu dosya> freecad.exe <ascii baslatici>   -> gui-kontrol.json, gorsel/montaj-gui-*.png (dosya kaydedilmez)
# Hicbir duzeltme yapmadan acar ve olcer: eklemlerin gorunum nesnesi ve gorunurlugu, agacta ve 3B'de secilebilirlik,
# montajin etkinlestirilmesi (cift tik karsiligi), fareyle surukleme (Qt fare olaylari) ve surukleme sonrasi eklem acilari.
import os, sys, json, math, tempfile, traceback
import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets
from pivy import coin  # noqa

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gorsel")
LOG = os.path.join(tempfile.gettempdir(), "robot-montaj-kare", "montaj_gui_kontrol.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)
open(LOG, "w").close()
R = dict(acilis={}, eklemler={}, secim={}, pick={}, etkin={}, surukleme=[], hatalar=[])


def log(*a):
    with open(LOG, "a") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


doc = App.openDocument(os.path.join(HERE, "robot-montaj.FCStd"))


def bekle(ms=50):
    t = QtCore.QElapsedTimer()
    t.start()
    while t.elapsed() < ms:
        QtWidgets.QApplication.processEvents()


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


def rot_aci(r):
    x, y, z, w = r.Q
    return math.degrees(2 * math.atan2(math.sqrt(x * x + y * y + z * z), abs(w)))


def eklem_aci(j):
    F = App.Placement(j.Placement1)
    rel = j.Reference1[0].Placement.multiply(F).inverse().multiply(j.Reference2[0].Placement.multiply(F))
    a = math.degrees(rel.Rotation.Angle) * (1 if rel.Rotation.Axis.z >= 0 else -1)
    a = math.fmod(a, 360.0)
    a = a - 360 if a > 180 else (a + 360 if a <= -180 else a)
    egik = math.degrees(math.acos(max(-1.0, min(1.0, abs(rel.Rotation.Axis.z))))) if rot_aci(rel.Rotation) > 1e-6 else 0.0
    return round(a, 3), round(rel.Base.Length, 6), round(egik, 6)


def go():
    gd = Gui.getDocument(doc.Name)
    mw = Gui.getMainWindow()
    mw.showMaximized()
    bekle(500)
    v = gd.activeView()
    asm = doc.getObject("Assembly")
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    eklemler = [o for o in doc.Objects if hasattr(o, "JointType") or o.Name.startswith("Sabit_")]
    sim = doc.getObject("Kollari_oynat")
    R["acilis"] = dict(
        parca=len(feats), parca_gorunur=sum(1 for o in feats if gd.getObject(o.Name).Visibility and o.Visibility),
        montaj_gorunur=bool(gd.getObject("Assembly").Visibility),
        grup_gorunur=sum(1 for o in asm.Group if o.TypeId == "App::Part" and gd.getObject(o.Name).Visibility),
        simulasyon=bool(sim), simulasyon_proxy=type(sim.ViewObject.Proxy).__name__ if sim and sim.ViewObject.Proxy else None,
        hareket=[m.Label for m in sim.Group] if sim else [])
    for j in eklemler:
        vo = j.ViewObject
        px = vo.Proxy if vo else None
        isaret = None
        if px is not None and hasattr(px, "switch_JCS1"):
            isaret = int(px.switch_JCS1.whichChild.getValue())      # -3 = SO_SWITCH_ALL (cizili)
        R["eklemler"][j.Name] = dict(etiket=j.Label, tip=getattr(j, "JointType", "Grounded"),
                                     vp=type(px).__name__ if px is not None else None,
                                     gorunur=bool(vo.Visibility) if vo else False, isaret_switch=isaret)
    log("acilis", R["acilis"])
    log("eklemler", R["eklemler"])

    # --- agac/secim: her eklem secim listesine girebiliyor mu
    for j in eklemler:
        Gui.Selection.clearSelection()
        Gui.Selection.addSelection(doc.Name, j.Name)
        bekle(20)
        R["secim"][j.Name] = any(s.Name == j.Name for s in Gui.Selection.getSelection())
    Gui.Selection.clearSelection()

    # --- montaji etkinlestir (agacta cift tik karsiligi)
    try:
        import UtilsAssembly
        gd.setEdit(asm)
        bekle(800)
        aa = UtilsAssembly.activeAssembly()
        R["etkin"] = dict(aktif_montaj=aa.Name if aa else None, duzenleme=type(gd.getInEdit()).__name__ if gd.getInEdit() else None)
    except Exception:
        R["hatalar"].append(traceback.format_exc())
    log("etkin", R["etkin"])

    kamera(v, (0.75, 0.4, 1.0), 470, (0, 905, 60))
    bekle(300)
    Gui.updateGui()

    # --- 3B secim: eklem isaretinin ekran noktasinda neye tiklanir
    for j in eklemler:
        if getattr(j, "JointType", None) != "Revolute":
            continue
        p = App.Placement(j.Placement1).Base
        xy = v.getPointOnViewport(p)
        info = v.getObjectInfo((int(xy[0]), int(xy[1])))
        R["pick"][j.Name] = dict(ekran=[int(xy[0]), int(xy[1])], nesne=info.get("Object") if info else None,
                                 alt=info.get("Component") if info else None)
    log("pick", R["pick"])

    # --- ekran goruntusu: eklemler gorunur, sag yana acma eklemi secili, montaj etkin
    Gui.Selection.addSelection(doc.Name, "OmuzSag_Yana")
    bekle(300)
    v.saveImage(os.path.join(OUT, "montaj-gui-eklemler.png"), 1400, 1000, "White")
    try:
        # model agaci: Robot > Eklemler ve simulasyon acik (3B gorunumun pencere goruntusu bozuk ciktigi icin yalniz agac)
        ACIK = ("robot-montaj", "Robot", "Eklemler", "Simulations", "Kollari_oynat")
        for t in mw.findChildren(QtWidgets.QTreeWidget):
            if not t.isVisible():
                continue
            t.collapseAll()
            it = QtWidgets.QTreeWidgetItemIterator(t)
            while it.value():
                x = it.value()
                if x.text(0) in ACIK:
                    x.setExpanded(True)
                it += 1
            dock = t.parent()
            while dock is not None and not isinstance(dock, QtWidgets.QDockWidget):
                dock = dock.parent()
            if dock is not None:
                dock.setMinimumWidth(430)
            t.setMinimumHeight(620)
            t.setStyleSheet("QTreeView{background:#ffffff;color:#111111} QTreeView::item{color:#111111}")
            bekle(400)
            t.grab().save(os.path.join(OUT, "montaj-gui-agac.png"))
            break
    except Exception:
        R["hatalar"].append(traceback.format_exc())
    Gui.Selection.clearSelection()

    # --- fareyle surukleme denemesi (Qt fare olaylari 3B gorunumun viewport'una)
    try:
        surukle(v, gd, asm)
    except Exception:
        R["hatalar"].append(traceback.format_exc())
        log(traceback.format_exc())

    json.dump(R, open(os.path.join(HERE, "gui-kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("bitti")
    try:
        gd.resetEdit()
    except Exception:
        pass
    App.closeDocument(doc.Name)
    mw.close()


def viewport_bul(v):
    gv = v.graphicsView()
    return gv, gv.viewport()


def olay(w, tip, pt, buton, butonlar):
    ev = QtGui.QMouseEvent(tip, QtCore.QPointF(pt), QtCore.QPointF(w.mapToGlobal(pt)), buton, butonlar,
                           QtCore.Qt.NoModifier)
    QtWidgets.QApplication.sendEvent(w, ev)


def surukle(v, gd, asm):
    gv, vp = viewport_bul(v)
    dpr = vp.devicePixelRatioF()
    log("viewport", vp.width(), vp.height(), "dpr", dpr, type(vp).__name__)
    ISO = ((0.75, 0.4, 1.0), 470, (0, 905, 60))
    YAN, YAN_SOL = ((1, 0, 0), 470, (0, 905, 0)), ((-1, 0, 0), 470, (0, 905, 0))
    # gobek grubunda tutulacak nokta: yan gorunumde gobegin ust ucuna yakin, gobek grubuna isabet eden ilk aday
    kamera(v, *YAN)
    Gui.updateGui()
    bekle(300)
    GOBEK = None
    gob = [o.Name for o in doc.getObject("OmuzSag_Gobek").OutListRecursive]
    for yy in (995.0, 990.0, 985.0, 980.0, 975.0):
        for zz in (0.0, -10.0, 5.0, -20.0):
            xy = v.getPointOnViewport(V(260.0, yy, zz))
            inf = v.getObjectInfo((int(xy[0]), int(xy[1])))
            if inf and inf.get("Object") in gob:
                GOBEK = (float(inf["x"]), float(inf["y"]), float(inf["z"]))
                break
        if GOBEK:
            break
    log("gobek noktasi", GOBEK)
    # (aciklama, taraf, tutulan nokta: ust kol tupunun yuzu (global), gorunum, fare yolu (px, ara noktalar))
    # Yan gorunum +X'ten: ekranda sol = ileri (+Z); -X'ten: ekranda sag = ileri.
    DENEME = [
        ("yana acma, disari", "Sag", (185.0, 860.0, 27.0), ISO, [(160, -40)]),
        ("yana acma, daha disari", "Sag", (185.0, 860.0, 27.0), ISO, [(420, -260)]),
        ("yana acma, cok disari (sinir 120)", "Sag", (185.0, 860.0, 27.0), ISO, [(900, -700)]),
        ("yana acma, iceri (sinir 0)", "Sag", (185.0, 860.0, 27.0), ISO, [(-260, 40)]),
        ("yana acma, disari", "Sol", (-185.0, 860.0, 27.0), ISO, [(-160, 40)]),
        ("one kaldirma, kol tupundan (yan gorunum)", "Sag", (213.0, 860.0, 0.0), YAN, [(-150, -20)]),
        ("one kaldirma, gobekten (yan gorunum)", "Sag", GOBEK, YAN, [(-60, -20), (-120, 60)]),
        ("one kaldirma, gobekten cok (sinir 135)", "Sag", GOBEK, YAN, [(-60, -20), (-120, 60), (-60, 160), (60, 200), (160, 160)]),
        ("arkaya, gobekten (sinir -45)", "Sag", GOBEK, YAN, [(60, -20), (140, 60), (160, 160)]),
        ("one kaldirma, gobekten (yan gorunum)", "Sol", (-GOBEK[0], GOBEK[1], GOBEK[2]), YAN_SOL, [(60, -20), (120, 60)]),
    ]
    L, N = QtCore.Qt.LeftButton, QtCore.Qt.NoButton
    for deneme, (acik, taraf, hedef, gor, yol) in enumerate(DENEME):
        jY, jO = doc.getObject("Omuz%s_Yana" % taraf), doc.getObject("Omuz%s_OneArka" % taraf)
        kol = doc.getObject("Omuz%s_Kol" % taraf)
        for g in [o for o in asm.Group if o.TypeId == "App::Part"]:
            g.Placement = App.Placement()
        kamera(v, *gor)
        Gui.updateGui()
        bekle(300)
        Hd = vp.height() * dpr
        xy = v.getPointOnViewport(V(*hedef))
        info = v.getObjectInfo((int(xy[0]), int(xy[1])))
        p0 = QtCore.QPoint(int(xy[0] / dpr), int((Hd - xy[1]) / dpr))
        for k in range(3):
            olay(vp, QtCore.QEvent.MouseMove, p0 + QtCore.QPoint(k, 0), N, N)
            bekle(60)
        olay(vp, QtCore.QEvent.MouseMove, p0, N, N)
        bekle(150)
        pre = Gui.Selection.getPreselection()
        pre_ad = pre.ObjectName if pre and hasattr(pre, "ObjectName") else str(pre)
        olay(vp, QtCore.QEvent.MouseButtonPress, p0, L, L)
        bekle(100)
        izY, izO = [], []
        onceki = (0, 0)
        for (dx, dy) in yol:
            n = max(1, int(math.hypot(dx - onceki[0], dy - onceki[1]) / 8))
            for k in range(1, n + 1):
                x = onceki[0] + (dx - onceki[0]) * k / n
                y = onceki[1] + (dy - onceki[1]) * k / n
                olay(vp, QtCore.QEvent.MouseMove, p0 + QtCore.QPoint(int(x), int(y)), N, L)
                bekle(30)
                izY.append(eklem_aci(jY)[0])
                izO.append(eklem_aci(jO)[0])
            onceki = (dx, dy)
        olay(vp, QtCore.QEvent.MouseButtonRelease, p0 + QtCore.QPoint(*onceki), L, N)
        bekle(300)
        Gui.updateGui()
        sonra = dict(yana=eklem_aci(jY), one_arka=eklem_aci(jO))
        hareket = rot_aci(kol.Placement.Rotation) > 1e-3 or kol.Placement.Base.Length > 1e-3
        kayit = dict(deneme=deneme + 1, aciklama=acik, kol=taraf.lower(), hedef=list(hedef), ekran_qt=[p0.x(), p0.y()], yol_px=yol,
                     tiklanan=info.get("Object") if info else None, on_secim=pre_ad, sonra=sonra, kol_hareket_etti=hareket,
                     yol_boyunca=dict(yana=[min(izY), max(izY)], one_arka=[min(izO), max(izO)]),
                     sinir=dict(yana=[float(jY.AngleMin), float(jY.AngleMax)], one_arka=[float(jO.AngleMin), float(jO.AngleMax)]))
        R["surukleme"].append(kayit)
        log("surukleme", deneme + 1, taraf, acik, "-> son", sonra, "yol boyunca", kayit["yol_boyunca"], "tik", kayit["tiklanan"])
        if deneme == 0 and hareket:
            v.saveImage(os.path.join(OUT, "montaj-gui-surukleme.png"), 1400, 1000, "White")
    for g in [o for o in asm.Group if o.TypeId == "App::Part"]:
        g.Placement = App.Placement()


def guvenli():
    try:
        go()
    except Exception:
        log(traceback.format_exc())
        R["hatalar"].append(traceback.format_exc())
        json.dump(R, open(os.path.join(HERE, "gui-kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
