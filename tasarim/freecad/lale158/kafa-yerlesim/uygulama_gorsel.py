# -*- coding: utf-8 -*-
# Lale 1,58 m - secim B + R1: son modelin gorselleri (FreeCAD GUI). Dosya KAYDEDILMEZ; yalniz gorsel/SON-*.png yazilir.
# Secenek gorsellerinden farki: parcalar eklenmez, son modelin kendi parcalari boyanir. Yalniz kablo yollari gosterim icin tup olarak eklenir.
# FC_SCRIPT=<bu dosya> FC_MONTAJ=<robot-montaj.FCStd KOPYASI> FC_LOG=<log> freecad.exe run_fc.py
import os, sys, json, tempfile, traceback
sys.dont_write_bytecode = True
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore, QtGui
from pivy import coin

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
for p_ in (LALE, UST):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import arayuz as A
import kablo_yolu_ekran as KY

OUT = os.path.join(HERE, "gorsel")
LOG = os.environ.get("FC_LOG") or os.path.join(tempfile.gettempdir(), "uygulama_gorsel.log")
open(LOG, "w").close()
OLC = json.load(open(os.path.join(HERE, "uygulama-olcum.json"), encoding="utf-8"))
W, H = 1600, 1100
K, SU = A.KAFA, A.SES_USB
Y0 = K["taban_y"]
YT, ZT = K["tilt_nokta"][1], K["tilt_nokta"][2]
YU = K["denge"]["dy"] + K["govde_y"][1]
ZB = K["denge"]["zb"]
D_ = SU["dizi"]
Y_IC_UST = YU - 2.5
Y_PCB = Y_IC_UST - D_["gap_jak"] - D_["jak_ust"]

R = dict(dizi=(0.90, 0.08, 0.10), hop=(0.55, 0.10, 0.80), hub=(0.05, 0.40, 0.95), ses=(0.05, 0.70, 0.25), pam=(1.00, 0.50, 0.00), kopuk=(0.95, 0.85, 0.10),
         sy=(0.95, 0.10, 0.70), fan=(0.0, 0.8, 0.85), pi=(0.45, 0.62, 0.48), kabuk=(0.80, 0.82, 0.86), gri=(0.72, 0.72, 0.74), usb=(0.05, 0.60, 0.95), usb_d=(0.85, 0.05, 0.05),
         usb_s=(0.05, 0.60, 0.25), hopk=(0.55, 0.10, 0.80), jak=(0.85, 0.65, 0.05), guc=(0.9, 0.3, 0.0), kapak=(0.45, 0.72, 0.85), kap=(0.75, 0.35, 0.75))


def bas_g(x, y, z):
    return (x, Y0 + YT + y, ZT + z)


def fv(x, n=1):
    return (("%." + str(n) + "f") % x).replace(".", ",")


def qc(c):
    return QtGui.QColor(int(c[0] * 255), int(c[1] * 255), int(c[2] * 255))


def log(*a):
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(" ".join(str(x) for x in a) + "\n")


class Kam:
    pass


def kamera(v, eye, h, merkez):
    z = V(*eye)
    z.normalize()
    up = V(0, 1, 0) if abs(z.y) < 0.99 else V(0, 0, -1)
    x = up.cross(z)
    x.normalize()
    y = z.cross(x)
    q = App.Rotation(x, y, z, "ZYX").Q
    cam = v.getCameraNode()
    cam.orientation.setValue(coin.SbRotation(q[0], q[1], q[2], q[3]))
    v.fitAll()
    pos = V(*merkez) + z * cam.focalDistance.getValue()
    cam.position.setValue(pos.x, pos.y, pos.z)
    cam.height.setValue(h)
    k = Kam()
    k.x, k.y, k.M, k.h = x, y, V(*merkez), h
    return k


def proj(k, p):
    d = V(*p) - k.M
    s = H / k.h
    return (W / 2.0 + d.dot(k.x) * s, H / 2.0 - d.dot(k.y) * s)


def etiketle(yol, k, baslik, etk, cizgi=(), alt=""):
    """etk: [(metin, nokta_g, renk)] kenar boslugunda kutu + kilavuz cizgi. cizgi: [(p1, p2, metin, renk)]."""
    im = QtGui.QImage(yol)
    pa = QtGui.QPainter(im)
    pa.setRenderHint(QtGui.QPainter.Antialiasing, True)
    f = QtGui.QFont("Segoe UI")
    f.setPixelSize(21)
    f.setBold(True)
    pa.setFont(f)
    fm = QtGui.QFontMetrics(f)
    sol, sag = [], []
    for t, p, c in etk:
        px, py = proj(k, p)
        (sol if px < W / 2 else sag).append((py, px, t, c))

    def yerles(ls, kenar):
        ls.sort()
        n = len(ls)
        adim = 46.0
        ys = [max(90.0 + i * adim, q[0] - 14) for i, q in enumerate(ls)]
        alt_s = H - 110.0
        for i in range(n - 1, -1, -1):
            ys[i] = min(ys[i], alt_s - (n - 1 - i) * adim)
        for i in range(1, n):
            ys[i] = max(ys[i], ys[i - 1] + adim)
        for (py, px, t, c), yk in zip(ls, ys):
            w = fm.horizontalAdvance(t) + 16 if hasattr(fm, "horizontalAdvance") else fm.width(t) + 16
            x0 = 12 if kenar == "sol" else W - w - 12
            ucx = x0 + w if kenar == "sol" else x0
            pa.setPen(QtGui.QPen(qc(c), 2.2))
            pa.drawLine(QtCore.QPointF(ucx, yk + 15), QtCore.QPointF(px, py))
            pa.setBrush(QtGui.QBrush(qc(c)))
            pa.drawEllipse(QtCore.QPointF(px, py), 5, 5)
            pa.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 235)))
            pa.drawRoundedRect(QtCore.QRectF(x0, yk, w, 31), 5, 5)
            pa.setPen(QtGui.QPen(QtGui.QColor(25, 25, 25)))
            pa.drawText(QtCore.QRectF(x0, yk, w, 31), QtCore.Qt.AlignCenter, t)

    yerles(sol, "sol")
    yerles(sag, "sag")
    for p1, p2, t, c in cizgi:
        a, b = proj(k, p1), proj(k, p2)
        pa.setPen(QtGui.QPen(qc(c), 3.0, QtCore.Qt.DashLine))
        pa.drawLine(QtCore.QPointF(*a), QtCore.QPointF(*b))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        w = (fm.horizontalAdvance(t) if hasattr(fm, "horizontalAdvance") else fm.width(t)) + 16
        pa.setPen(QtGui.QPen(qc(c), 2))
        pa.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 240)))
        pa.drawRoundedRect(QtCore.QRectF(mx - w / 2, my - 16, w, 32), 5, 5)
        pa.setPen(QtGui.QPen(QtGui.QColor(20, 20, 20)))
        pa.drawText(QtCore.QRectF(mx - w / 2, my - 16, w, 32), QtCore.Qt.AlignCenter, t)
    pa.setPen(QtCore.Qt.NoPen)
    pa.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255, 245)))
    pa.drawRect(QtCore.QRectF(0, 0, W, 56))
    if alt:
        pa.drawRect(QtCore.QRectF(0, H - 62, W, 62))
    f2 = QtGui.QFont("Segoe UI")
    f2.setPixelSize(30)
    f2.setBold(True)
    pa.setFont(f2)
    pa.setPen(QtGui.QPen(QtGui.QColor(15, 15, 15)))
    pa.drawText(QtCore.QRectF(0, 8, W, 44), QtCore.Qt.AlignCenter, baslik)
    if alt:
        f3 = QtGui.QFont("Segoe UI")
        f3.setPixelSize(20)
        pa.setFont(f3)
        pa.setPen(QtGui.QPen(QtGui.QColor(70, 70, 70)))
        pa.drawText(QtCore.QRectF(20, H - 60, W - 40, 58), int(QtCore.Qt.AlignCenter) | int(QtCore.Qt.TextWordWrap), alt)
    pa.end()
    im.save(yol)


def tup(yol, r):
    t = None
    for a_, b_ in zip(yol[:-1], yol[1:]):
        a_, b_ = V(*a_), V(*b_)
        if (b_ - a_).Length < 1e-6:
            continue
        c = Part.makeCylinder(r, (b_ - a_).Length, a_, b_ - a_).fuse(Part.makeSphere(r, b_))
        t = c if t is None else t.fuse(c)
    return t


BOYA = (("ReSpeaker", "dizi"), ("Dizi vidasi", "kopuk"), ("USB ses", "ses"), ("PAM8403", "pam"), ("Hoparlor 40", "hop"), ("Hoparlor kabi", "kap"), ("USB Hub", "hub"), ("Kopuk bant (USB Hub", "kopuk"), ("SY8205", "sy"))
KABLO_RENK = (("Hub", "usb"), ("ESP32", "usb"), ("USB dokunmatik", "usb"), ("Dizi", "usb_d"), ("Ses karti", "usb_s"), ("3,5", "jak"), ("Hoparlor", "hopk"), ("PAM 5 V", "guc"))


def go():
    doc = App.openDocument(os.environ["FC_MONTAJ"])
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
            ref = getattr(o, "Tur", "") == "Referans"
            vo.Visibility = not ref
            if not ref:
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
    sg = v.getSceneGraph()
    ge = {}
    for o in par:
        s_ = o.Shape.copy()
        s_.Placement = o.getGlobalPlacement()
        ge[o.Name] = s_.BoundBox

    def boya(o, c, t):
        vo = gd.getObject(o.Name)
        try:
            vo.ShapeColor = c
            vo.Transparency = t
        except Exception:
            pass

    for o in par:
        lb = o.Label
        if lb.startswith(("Yuz kabugu", "Arka kafa kabugu")) or "abuk" in lb or "bandi" in lb or "kapagi" in lb or "Etek" in lb:
            boya(o, R["kabuk"], 82)
        elif lb.startswith(("Raspberry", "Active Cooler")):
            boya(o, R["pi"], 25)
        else:
            renk = [r_ for b_, r_ in BOYA if lb.startswith(b_)]
            if renk:
                boya(o, R[renk[0]], 0)
            else:
                boya(o, R["gri"], 55)

    def ekle(ad, sh, renk, t=0):
        o = doc.addObject("Part::Feature", "Son%d" % len(ekli))
        o.Label = ad
        o.Shape = sh
        boya(o, renk, t)
        ekli.append(o)
        return o

    ekli = []
    # gosterim tupleri: son yollar (kablo_yolu_ekran.yollar global, kafa_ici_qled bas cercevesi)
    yl = KY.yollar()
    tup_gov = []
    for ad, yol in yl.items():
        c = [r_ for b_, r_ in KABLO_RENK if ad.startswith(b_)]
        if not c:
            continue
        o = ekle("Kablo " + ad, tup(yol, KY.KABLO[ad][0] / 2.0), R[c[0]])
        if max(q[1] for q in yol) < 1340.0:
            tup_gov.append(o)
    fan_b = Part.makeBox(30.0, 30.0, 10.0, V(*bas_g(12.5, 62.0, ZB + 2.6)))
    fan_o = ekle("Fan yeri", fan_b, R["fan"], 45)

    def kafa_gor(ac):
        for o in par:
            if ge[o.Name].YMax < 1340.0:
                gd.getObject(o.Name).Visibility = not ac
        for o in tup_gov:
            gd.getObject(o.Name).Visibility = not ac
        Gui.updateGui()

    def gizle(on):
        ls = [o for o in par if o.Label.startswith(tuple(on))]
        for o in ls:
            gd.getObject(o.Name).Visibility = False
        return ls

    def goster_(on):
        for o in par:
            if o.Label.startswith(tuple(on)):
                gd.getObject(o.Name).Visibility = True

    def kesit(nx, ny, nz, d):
        cp = coin.SoClipPlane()
        cp.plane.setValue(coin.SbPlane(coin.SbVec3f(nx, ny, nz), d))
        sg.insertChild(cp, 0)
        Gui.updateGui()
        return cp

    def kaydet(ad):
        Gui.updateGui()
        yol = os.path.join(OUT, ad)
        v.saveImage(yol, W, H, "White")
        log("gorsel", ad)
        return yol

    def m(lb):
        o = [q for q in par if q.Label.startswith(lb)][0]
        c = ge[o.Name].Center
        return (c.x, c.y, c.z)

    KAFA_M = bas_g(0.0, -6.4, -20.0)
    ICIN_AC = ("Arka kafa kabugu", "Kabuk civatasi", "Isil gomme somun M3 (kafa")
    mh = OLC["mic_hoparlor"]
    # 1) arkadan, arka kabuk sokulmus
    kafa_gor(True)
    gizle(ICIN_AC)
    Gui.updateGui()
    k = kamera(v, (-0.25, 0.25, -1.0), 380, KAFA_M)
    y = kaydet("SON-kafa-arka-acik.png")
    etiketle(y, k, "Son model: arka kabuk sökülmüş, kafa arkadan", [
        ("ReSpeaker Mic Array v2.0 (tavan altı, sağ yarı)", m("ReSpeaker"), R["dizi"]),
        ("USB ses kartı (y 47)", m("USB ses"), R["ses"]),
        ("PAM8403 (y 72)", m("PAM8403"), R["pam"]),
        ("SY8205", m("SY8205"), R["sy"]),
        ("Raspberry Pi 5", m("Raspberry"), R["pi"]),
        ("Ayrılmış fan yeri (parça değil)", bas_g(27.5, 77.0, ZB + 7.6), R["fan"]),
        ("USB koridoru z = -14: SY8205'in önünden", bas_g(10.0, 36.5, -14.0), R["usb"]),
    ], alt="Görselin solu modelde 'sağ' (+X) yan. Tepe civatası yerinde, MAX98357A ve kafa içi hub yok. Renkli çizgiler kablo yolu şeması, ölçüde parça sayılmaz.")
    goster_(ICIN_AC)
    # 2) mikrofon deliginden kesit
    mk = D_["mic"][0]
    mx, my, mz = D_["cx"] - mk[1], Y_PCB + mk[2], D_["cz"] - mk[0]
    cp = kesit(-1, 0, 0, -mx - 0.01)
    k = kamera(v, (1, 0, 0), 330, bas_g(mx, -6.4, -20.0))
    y = kaydet("SON-kafa-kesit.png")
    etiketle(y, k, "Son model: mikrofon deliğinden yan kesit, x = %s (ön solda)" % fv(mx), [
        ("ReSpeaker", bas_g(mx, Y_PCB, D_["cz"] + 12.0), R["dizi"]),
        ("Mikrofon deliği Ø3 (varsayım)", bas_g(mx, YU, mz), (0.1, 0.1, 0.1)),
        ("Pi + soğutucu", m("Raspberry"), R["pi"]),
        ("Ayrılmış fan yeri", bas_g(27.5, 77.0, ZB + 7.6), R["fan"]),
    ], alt="Delik yeri üretici STEP dosyasından; delik çapı ve keçe/conta kararı varsayım.")
    sg.removeChild(cp)
    # 3) ust govde yandan
    kafa_gor(False)
    fan_o.ViewObject.Visibility = False
    kol = [o for o in par if abs(ge[o.Name].Center.x) > 150.0 and ge[o.Name].YMin < 1400]
    for o in kol:
        gd.getObject(o.Name).Visibility = False
    cp = kesit(-1, 0, 0, -105.0)
    k = kamera(v, (1, 0, 0), 800, (0.0, 1230.0, 10.0))
    y = kaydet("SON-govde.png")
    sg.removeChild(cp)
    hc = KY.hoparlor_merkez()
    mg = bas_g(mx, my, mz)
    etiketle(y, k, "Son model: üst gövde yandan (ön solda)", [
        ("ReSpeaker", m("ReSpeaker"), R["dizi"]),
        ("Hoparlör (göğüs ekranı altı, duvara paralel)", m("Hoparlor 40"), R["hop"]),
        ("USB hub (servis kapağı içi)", m("USB Hub"), R["hub"]),
    ], cizgi=[(mg, m("Hoparlor 40"), "mikrofon - hoparlör: en az %s mm" % fv(mh["poz_min_mm"]), (0.8, 0.05, 0.05))],
        alt="En az %s mm: ±90 pan, ±15 tilt pozları. Ev pozu %s mm. Kablo çizgileri yol şeması." % (fv(mh["poz_min_mm"]), fv(mh["ev_min_mm"])))
    # 4) hub, kapak ic yuzu
    k = kamera(v, (-0.35, 0.2, -1.0), 420, (20.0, 1125.0, -40.0))
    y = kaydet("SON-hub-kapak.png")
    etiketle(y, k, "Son model: hub, üst arka servis kapağının iç yüzünde", [
        ("USB hub (4 port: 2 dolu, 2 boş)", m("USB Hub"), R["hub"]),
        ("Köpük bant", m("Kopuk bant (USB Hub"), R["kopuk"]),
        ("Üst arka servis kapağı", (-50.0, 1125.0, -82.0), R["kabuk"]),
        ("Hub uzatması (Pi 3. port)", (40.0, 1176.0, -60.0), R["usb"]),
        ("Hoparlör", m("Hoparlor 40"), R["hop"]),
    ], alt="Hub kapağa takozla oturur (toplam boşluk 1...3,9 mm, 1 mm köpük). Kablolarda 150 mm kapak sökme payı (tahmin).")
    App.closeDocument(doc.Name)
    log("TAMAM")
    Gui.getMainWindow().close()


def guvenli():
    try:
        go()
    except Exception:
        log(traceback.format_exc())
        Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
