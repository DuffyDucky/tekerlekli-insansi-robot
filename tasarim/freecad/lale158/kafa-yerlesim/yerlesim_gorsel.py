# -*- coding: utf-8 -*-
# Lale 1,58 m - kafa yerlesim secenekleri gorselleri (FreeCAD GUI). Dosya KAYDEDILMEZ; yalniz gorsel/*.png yazilir.
# FC_SCRIPT=<bu dosya> FC_MONTAJ=<robot-montaj.FCStd KOPYASI> FC_LOG=<log> freecad.exe run_fc.py
import os, sys, json, math, tempfile, traceback
sys.dont_write_bytecode = True
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore, QtGui
from pivy import coin

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yerlesim_lib as Y
from yerlesim_lib import bas_g, bas2g, YT, ZT, Y0, ZB, YU, X_IC, Y_IC_UST

OUT = os.path.join(HERE, "gorsel")
LOG = os.environ.get("FC_LOG") or os.path.join(tempfile.gettempdir(), "yerlesim_gorsel.log")
open(LOG, "w").close()
SONUC = json.load(open(os.path.join(HERE, "sonuc.json"), encoding="utf-8"))
W, H = 1600, 1100

R = dict(dizi=(0.90, 0.08, 0.10), hop=(0.55, 0.10, 0.80), hub=(0.05, 0.40, 0.95), ses=(0.05, 0.70, 0.25), ses_zarf=(0.55, 0.88, 0.60), pam=(1.00, 0.50, 0.00),
         boss=(0.95, 0.85, 0.10), zarf=(0.95, 0.70, 0.70), celik=(0.3, 0.3, 0.3), sy=(0.95, 0.10, 0.70), fan=(0.0, 0.8, 0.85), pi=(0.45, 0.62, 0.48), kabuk=(0.80, 0.82, 0.86), gri=(0.72, 0.72, 0.74), usb_t=(0.0, 0.25, 0.85), usb_d=(0.85, 0.05, 0.05), hopk=(0.55, 0.10, 0.80), usb_h=(0.05, 0.60, 0.95), usb_s=(0.05, 0.60, 0.25), jak=(0.85, 0.65, 0.05))


def f1(x):
    return ("%.1f" % x).replace(".", ",")


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
        bas = 90.0
        adim = 46.0
        ys = [max(bas + i * adim, q[0] - 14) for i, q in enumerate(ls)]
        for i in range(n - 2, -1, -1):
            pass
        alt_s = H - 110.0
        for i in range(n - 1, -1, -1):
            lim = alt_s - (n - 1 - i) * adim
            ys[i] = min(ys[i], lim)
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

    def taban():
        """Kabuk seffaf, diger her sey soluk gri; kola ve alt govdeye kapali gorunum."""
        for o in par:
            lb = o.Label
            vo = gd.getObject(o.Name)
            vo.Visibility = True
            if lb.startswith(("Yuz kabugu", "Arka kafa kabugu")) or "abuk" in lb or "bandi" in lb or "kapagi" in lb or "Etek" in lb:
                boya(o, R["kabuk"], 82)
            elif lb.startswith("SY8205"):
                boya(o, R["sy"], 0)
            elif lb.startswith(("Raspberry", "Active Cooler")):
                boya(o, R["pi"], 25)
            else:
                boya(o, R["gri"], 55)

    ekli = []
    gov_ek = []

    def kafa_gor(ac):
        """ac: kafa gorunumu (govde ve eklenen govde parcalari gizli); degilse hepsi acik."""
        for o in par:
            if ge[o.Name].YMax < 1340.0:
                gd.getObject(o.Name).Visibility = not ac
        for o in gov_ek:
            gd.getObject(o.Name).Visibility = not ac
        Gui.updateGui()

    def ekle(ad, sh, renk, t=0):
        o = doc.addObject("Part::Feature", "Sec%d" % len(ekli))
        o.Label = ad
        o.Shape = sh
        boya(o, renk, t)
        ekli.append(o)
        return o

    def temizle():
        for o in list(ekli):
            doc.removeObject(o.Name)
        ekli[:] = []
        gov_ek[:] = []

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

    def bb_m(s):
        b = s.BoundBox
        return (b.Center.x, b.Center.y, b.Center.z)

    KAFA_M = bas_g(0.0, -6.4, -20.0)
    KABUK_ARKA = ("Arka kafa kabugu",)
    ICIN_AC = ("Arka kafa kabugu", "Kabuk civatasi", "Isil gomme somun M3 (kafa")
    MAX_AD = ("MAX98357A", "Kopuk bant (MAX98357A")

    # fan yeri / referans
    fan_g = Y.box(12.5, 42.5, 62.0, 92.0, ZB + Y.KT + 0.1, ZB + Y.KT + 10.1)
    SY_G = bas_g(36.0, 35.5, 14.0)
    PI_G = bas_g(-5.0, 50.0, -55.0)
    SLOT_G = bas_g(27.5, 50.0, ZB)

    # ---------------------------------------------------------- 0: bugunku yer
    SADECE = os.environ.get("FC_HARFLER", "0,A,B,C,R2").split(",")
    taban()
    for o in par:
        if o.Label.startswith("USB Hub"):
            boya(o, R["hub"], 0)
        elif o.Label.startswith("USB ses"):
            boya(o, R["ses"], 0)
        elif o.Label.startswith("PAM8403"):
            boya(o, R["pam"], 0)
        elif o.Label.startswith("MAX98357A"):
            boya(o, (0.6, 0.2, 0.2), 0)
    y0 = Y._Y["USB dokunmatik"][:18]
    ekle("Sematik USB", Y.tup(y0, 2.0), R["usb_t"])
    ekle("Fan yeri", bas2g(fan_g), R["fan"], 45)
    ls = gizle(ICIN_AC)
    kafa_gor(True)
    k = kamera(v, (-0.25, 0.25, -1.0), 380, KAFA_M)
    y = kaydet("0-mevcut-kafa-arka-acik.png" if "0" in SADECE else "_gecici.png")
    etiketle(y, k, "Bugünkü model: arka kabuk sökülmüş, kafa arkadan", [
        ("USB hub (72 x 25 x 19)", bas_g(121.0, 50.0, -28.0), R["hub"]),
        ("USB ses kartı (45 x 18 x 11, fiş sayılmıyor)", bas_g(-126.0, 44.0, -19.5), R["ses"]),
        ("PAM8403", bas_g(-127.0, 44.0, -56.0), R["pam"]),
        ("MAX98357A (çıkacak)", bas_g(80.0, 32.0, 6.0), (0.6, 0.2, 0.2)),
        ("SY8205 kafa ekranı 5 V", SY_G, R["sy"]),
        ("Dokunmatik USB şematik yolu: SY8205'ten geçiyor", bas_g(50.0, 38.0, 20.0), R["usb_t"]),
        ("Raspberry Pi 5", PI_G, R["pi"]),
        ("Ayrılmış fan yeri 30 x 30 x 10", bas_g(27.5, 77.0, ZB + 8.0), R["fan"]),
    ], alt="Sorun 1: USB çizgisi SY8205'in içinden geçiyor (249,7 mm³). Sorun 2: PAM, ses kartının USB fişinin önünde. Sorun 3: hub ve ses kartı karşılıklı duvarlarda, arada kablo yok. Görselin solu modelde 'sağ' (+X) yan.")
    goster_(ICIN_AC)
    temizle()

    for harf, baslik in (("A", "A: dizi kafa tepesinde, hub yerinde, hoparlör göğüs altında"), ("B", "B: dizi kafa tepesinde, hub gövdede, hoparlör göğüs altında"), ("C", "C: dizi kafa tepesinde, hoparlör KAFA içinde (40 cm şartını sağlamaz)"), ("R2", "R2 çeşidi: B yerleşimi, dizi pan ekseninde")):
        if harf not in SADECE:
            continue
        S = Y.secenek(harf, lid_z=SONUC.get("ust_kapak_ic_z"))
        Sn = SONUC["secenek"][harf]
        taban()
        kaldir = S["kaldir"]
        for o in par:
            if o.Label in kaldir or o.Label.startswith(tuple(kaldir)):
                gd.getObject(o.Name).Visibility = False
            elif harf not in ("B", "R2") and o.Label.startswith("USB Hub"):
                boya(o, R["hub"], 0)
        for q in S["kafa"]:
            ekle(q["ad"], bas2g(q["sh"]), R.get(q["renk"], R["gri"]), 35 if q["zarf"] else 0)
        for q in S["govde"]:
            gov_ek.append(ekle(q["ad"], q["sh"], R.get(q["renk"], R["gri"]), 35 if q["zarf"] else 0))
        for f in S["dizi"]["delik"]:
            ekle("Mikrofon deligi", bas2g(f), (0.0, 0.0, 0.0))
        KABLO_RENK = {"USB uzatma": R["usb_s"], "Ses karti": R["usb_s"], "3,5": R["jak"], "Hoparlor": R["hopk"], "Gogus": R["usb_t"], "Hub": R["usb_h"], "Dizi": R["usb_d"], "PAM 5 V": (0.9, 0.3, 0.0)}
        for ad, (yol, r, _l, _n) in S["kablo"].items():
            c = [v_ for k_, v_ in KABLO_RENK.items() if ad.startswith(k_)][0]
            ekle("Kablo " + ad, Y.tup(yol, r), c, 0)
        ekle("Fan yeri", bas2g(fan_g), R["fan"], 45)
        cx, cz = S["R"]["cx"], S["R"]["cz"]
        d_g = bas_g(cx, Y.Y_PCB_UST, cz)
        h = S["hop"]
        hop_g = V(h["merkez_diyafram"]) if S["hop_cerceve"] == "g" else V(*bas_g(h["merkez_diyafram"].x, h["merkez_diyafram"].y, h["merkez_diyafram"].z))
        hop_t = (hop_g.x, hop_g.y, hop_g.z)
        s_b = S["ses"]["govde"].BoundBox
        ses_g = bas_g(s_b.Center.x, s_b.Center.y, s_b.Center.z)
        pam = [q for q in S["kafa"] if q["ad"] == "PAM8403"][0]["sh"].BoundBox
        pam_g = bas_g(pam.Center.x, pam.Center.y, pam.Center.z)
        ak = Sn["akustik"]
        mm = ak["mic_hoparlor_poz_min_mm"]
        ev = ak["mic_hoparlor_ev_min_mm"]
        hub_t = bas_g(121.0, 50.0, -28.0) if harf not in ("B", "R2") else tuple(S["hub_g"].BoundBox.Center)
        ort = [("ReSpeaker Mic Array v2.0", d_g, R["dizi"]), ("PAM8403", pam_g, R["pam"]), ("USB ses kartı (+ fişleri)", ses_g, R["ses"]), ("SY8205", SY_G, R["sy"]), ("Fan yeri (ayrılmış)", bas_g(27.5, 77.0, ZB + 8.0), R["fan"])]
        if harf not in ("B", "R2"):
            ort.append(("USB hub", hub_t, R["hub"]))
        kab_ad = [a for a in S["kablo"] if a.startswith("Dizi")][0]
        ort.append(("Dizi USB kablosu", bas_g(68.0, 55.0, S["kablo"][kab_ad][0][2][2] - ZT), R["usb_d"]))
        gk = [a for a in S["kablo"] if a.startswith(("Gogus", "Hub uzatmasi"))][0]
        ort.append(("Boyun USB koridoru: SY8205'in önünden geçer", bas_g(10.0, 36.5, -13.4), R["usb_t"]))

        kafa_gor(True)
        # 1) arkadan, arka kabuk sokulmus
        if harf != "R2":
            gizle(ICIN_AC)
            kafa_gor(True)
            k = kamera(v, (-0.25, 0.25, -1.0), 380, KAFA_M)
            y = kaydet("%s-kafa-arka-acik.png" % harf)
            e = list(ort)
            if harf == "C":
                e.append(("Hoparlör (kafa içi)", hop_t, R["hop"]))
            etiketle(y, k, baslik, e, alt="Arka kabuk sökülmüş, kafaya arkadan bakıyoruz; görselin solu modelde 'sağ' (+X) yan. Renkliler bu seçeneğin parçaları, griler mevcut model.")
            goster_(ICIN_AC)

        # 2) seffaf uc ceyrek
        if harf != "R2":
            Gui.updateGui()
            k = kamera(v, (0.75, 0.45, -1.0), 400, KAFA_M)
            y = kaydet("%s-kafa-seffaf.png" % harf)
            e = [("ReSpeaker Mic Array v2.0", d_g, R["dizi"]), ("PAM8403", pam_g, R["pam"]), ("USB ses kartı", ses_g, R["ses"]), ("SY8205", SY_G, R["sy"])]
            if harf not in ("B", "R2"):
                e.append(("USB hub", hub_t, R["hub"]))
            etiketle(y, k, baslik, e, alt="Şeffaf kabuk, sağ arkadan.")

        # 3) bir mikrofon deliginden yan kesit
        mk = S["dizi"]["mic"][0]
        cp = kesit(-1, 0, 0, -mk[0] - 0.01)
        k = kamera(v, (1, 0, 0), 330, bas_g(mk[0], -6.4, -20.0))
        y = kaydet("%s-kafa-kesit.png" % harf)
        e = [("ReSpeaker (bu kesitte bir kirişi görünüyor)", bas_g(mk[0], Y.Y_PCB_UST, cz + 12.0), R["dizi"]), ("Mikrofon deliği Ø3 (varsayım)", bas_g(mk[0], YU, mk[2]), (0.1, 0.1, 0.1)), ("Pi + soğutucu", PI_G, R["pi"]), ("Tabla", bas_g(mk[0], 29.5, 15.0), R["gri"]), ("PAM8403 (yan duvarda)", pam_g, R["pam"]), ("USB ses kartı (yan duvarda)", ses_g, R["ses"])]
        if mk[0] >= 12.5:          # fan yeri x 12,5...42,5; kesit daha soldaysa gorunmez
            e.append(("Fan yeri (ayrılmış)", bas_g(27.5, 77.0, ZB + 8.0), R["fan"]))
        etiketle(y, k, "%s: mikrofon deliğinden yan kesit, x = %s (ön solda)" % (harf, f1(mk[0])), e, alt="Mikrofon portu ile dış hava arası %s mm: duvara kadar %s mm, duvar %s mm." % (f1(ak["port_kabuk"]["toplam_yol_mm"]), f1(ak["port_kabuk"]["port_ust_duvar_ic_mm"]), f1(Y.KT)))
        if harf in ("A", "R2"):
            k = kamera(v, (1, 0, 0), 50, bas_g(mk[0], mk[1], mk[2]))
            y = kaydet("%s-dizi-yakin.png" % harf)
            e = [("Kabuk tavanı 2,5 mm", bas_g(mk[0], Y_IC_UST + 1.2, mk[2] + 12.0), R["gri"]), ("Delik Ø3 (varsayım)", bas_g(mk[0], YU - 1.0, mk[2]), (0.1, 0.1, 0.1)), ("Mikrofon portu (kılıf üstü)", bas_g(mk[0], mk[1], mk[2]), R["dizi"]), ("PCB", bas_g(mk[0], Y.Y_PCB_UST - 0.6, mk[2] + 8.0), R["dizi"])]
            etiketle(y, k, "%s: dizi ile tavan yakın kesit" % harf, e, cizgi=[(bas_g(mk[0], mk[1], mk[2]), bas_g(mk[0], YU, mk[2]), f1(YU - mk[1]) + " mm", (0.8, 0.05, 0.05))], alt="Yakın görünüm, 50 mm yükseklik. Delik yeri üretici STEP dosyasından; delik çapı ve keçe/conta kararı varsayım, ölçülecek.")
        sg.removeChild(cp)

        # 4) ustten
        gizle(("Yuz ekrani", "Ekran"))
        k = kamera(v, (0, 1, 0), 330, (0.0, Y0 + YT + 60.0, ZT - 20.0))
        y = kaydet("%s-ust.png" % harf)
        goster_(("Yuz ekrani", "Ekran"))
        e = [("Mikrofon deliği x 4", bas_g(*[S["dizi"]["mic"][0][0], YU, S["dizi"]["mic"][0][2]]), (0.1, 0.1, 0.1)), ("Fan yeri (ayrılmış)", bas_g(27.5, 92.0, ZB + 8.0), R["fan"]), ("x = 0 dikişi", bas_g(0.0, YU, 30.0), (0.3, 0.3, 0.3)), ("z = +10 dikişi (ön / arka)", bas_g(120.0, YU, 10.0), (0.3, 0.3, 0.3))]
        if harf not in ("B", "R2"):
            e.append(("USB hub", hub_t, R["hub"]))
        e.append(("ReSpeaker", d_g, R["dizi"]))
        etiketle(y, k, "%s: üstten (arka yukarıda)" % harf, e, alt="Dizi merkezi pan ekseninden %s mm uzakta." % f1(ak["dizi_merkez_pan_ekseni_mm"]))

        # 5) ust govde yandan, mikrofon-hoparlor mesafesi
        if harf == "R2":
            temizle()
            log("bitti", harf)
            continue
        kafa_gor(False)
        for ad_ in kaldir:
            gizle((ad_,))
        kol = [o for o in par if abs(ge[o.Name].Center.x) > 150.0 and ge[o.Name].YMin < 1400 and gd.getObject(o.Name).Visibility]
        for o in kol:
            gd.getObject(o.Name).Visibility = False
        cp = kesit(-1, 0, 0, -105.0)
        k = kamera(v, (1, 0, 0), 800, (0.0, 1230.0, 10.0))
        y = kaydet("%s-govde.png" % harf)
        sg.removeChild(cp)
        for o in kol:
            gd.getObject(o.Name).Visibility = True
        mg = bas_g(*S["dizi"]["mic"][0])
        e = [("ReSpeaker", d_g, R["dizi"]), ("Hoparlör", hop_t, R["hop"])]
        if harf in ("B", "R2"):
            e.append(("USB hub (servis kapağı içi)", hub_t, R["hub"]))
        cz_ = [(mg, hop_t, "mikrofon - hoparlör: en az %.0f mm" % mm, (0.8, 0.05, 0.05))]
        etiketle(y, k, "%s: üst gövde yandan (ön solda)" % harf, e, cizgi=cz_, alt="En az %.0f mm: kafa ±90 pan, ±15 tilt tüm pozlar. Ev pozu %.0f mm. Öneri H1: en az 400 mm. %s" % (mm, ev, "SAĞLIYOR" if ak["h1_40cm"] else "SAĞLAMIYOR"))
        if harf == "B":
            k = kamera(v, (-0.35, 0.2, -1.0), 420, (20.0, 1125.0, -40.0))
            y = kaydet("B-hub-kapak.png")
            bz = S["hub_g"].BoundBox
            e = [("USB hub (kapağın iç yüzünde)", hub_t, R["hub"]), ("Hub USB fiş payı 40 mm", (47.5, 1125.0, bz.ZMax + 20.0), R["zarf"]), ("Hub uzatması (Pi'den)", (40.0, 1176.0, -60.0), R["usb_h"]), ("Üst arka servis kapağı", (-50.0, 1125.0, -82.0), R["kabuk"])]
            etiketle(y, k, "B: hub gövdede, üst arka servis kapağının iç yüzünde", e, alt="Kapak sökülünce hub kapakla birlikte gelir; kablolarda kapak sökme payı gerekir. Kapak iç yüzü eğik: takoz 1...3,9 mm.")
        temizle()
        log("bitti", harf)
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
