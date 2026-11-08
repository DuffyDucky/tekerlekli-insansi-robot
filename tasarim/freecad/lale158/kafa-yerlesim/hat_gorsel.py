# -*- coding: utf-8 -*-
# Lale 1,58 m - F1a P1.3 AI HAT+ secenek gorselleri (FreeCAD GUI). Ana modele dokunmaz; hat_secenek.py'nin HAT_FCSTD ile yazdigi
# gecici FCStd'leri (depo disi) acar, hicbirini kaydetmez. Cikti: gorsel/HAT-<s>-arka.png, gorsel/HAT-<s>-kesit.png (s = 0, a, b).
#   HAT_FC_DIR=<hat-0/a/b.FCStd klasoru> FC_SCRIPT=<bu dosya> freecad.exe run_fc.py
# Koordinat: kafa yereli (ev pozu). Bas cercevesi = kafa yereli - (0, YT, ZT). Kirmizi: dikis civatasi + isil gomme somun (boss yeri);
# secenek 0'da HAT ile arka kabuk ortak hacmi ayrica kirmizi kati. Mor yari saydam: "Fan yeri 30x30x10 (listede yok)" zarfi.
import os, sys, json, tempfile, traceback
sys.dont_write_bytecode = True
import FreeCAD as App
import FreeCADGui as Gui
import Part
from PySide import QtCore
from pivy import coin

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gorsel")
DIR = os.environ.get("HAT_FC_DIR", tempfile.gettempdir())
LOG = os.path.join(DIR, "hat_gorsel.log")
open(LOG, "w").close()
YT, ZT = 188.878, 25.0
R = dict(kabuk=(0.86, 0.87, 0.90), hat=(0.96, 0.55, 0.13), pi=(0.10, 0.45, 0.20), kirmizi=(0.85, 0.10, 0.10), fan=(0.55, 0.25, 0.75),
         iskelet=(0.18, 0.52, 0.86), gri=(0.62, 0.62, 0.64), dizi=(0.15, 0.15, 0.17))
BOSS_X = {"0": -8.0, "a": -5.0, "b": -8.0}


def log(*a):
    with open(LOG, "a", encoding="utf-8") as fh:
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


def bir(s):
    doc = App.openDocument(os.path.join(DIR, "hat-%s.FCStd" % s))
    gd = Gui.getDocument(doc.Name)
    Gui.ActiveDocument = gd
    v = gd.activeView()
    v.setAnimationEnabled(False)
    v.setCameraType("Orthographic")
    par = [o for o in doc.Objects if o.TypeId == "Part::Feature"]

    def boya(o, c, t=0, gor=True):
        vo = gd.getObject(o.Name)
        vo.ShapeColor = c
        vo.Transparency = t
        vo.Visibility = gor

    kabuk = []
    for o in par:
        lb = o.Label
        if lb.startswith("ZARF "):
            boya(o, R["fan"], 55, "Fan yeri" in lb)
        elif lb.startswith(("Yuz kabugu", "Arka kafa kabugu")):
            boya(o, R["kabuk"], 70)
            kabuk.append(o)
        elif lb.startswith("AI HAT+"):
            boya(o, R["hat"], 0)
        elif lb.startswith("Raspberry"):
            boya(o, R["pi"], 0)
        elif "arka duvar ust" in lb:
            boya(o, R["kirmizi"], 0)
        elif lb.startswith("Kafa iskeleti"):
            boya(o, R["iskelet"], 60)
        elif lb.startswith("ReSpeaker"):
            boya(o, R["dizi"], 30)
        elif lb.startswith("Yuz ekrani"):
            boya(o, R["gri"], 0, False)
        else:
            boya(o, R["gri"], 40)
    ekli = []
    if s == "0":                       # cakisma hacmi: HAT parcalari x arka kabuk sag
        hat = [o for o in par if o.Label.startswith("AI HAT+")]
        sag = [o for o in par if o.Label == "Arka kafa kabugu sag"][0]
        c = Part.makeCompound([h.Shape.common(sag.Shape) for h in hat])
        log(s, "cakisma hacmi", round(sum(x.Volume for x in c.Solids), 2))
        n = doc.addObject("Part::Feature", "Cakisma")
        n.Shape = c
        boya(n, R["kirmizi"], 0)
        ekli.append(n)
    Gui.updateGui()
    m = (-10.0, YT + 58.0, ZT - 45.0)
    kamera(v, (-0.35, 0.55, -1.0), 175, m)
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, "HAT-%s-arka.png" % s), 1200, 1000, "White")
    log(s, "arka")
    # kesit: x <= boss x yarisi (kesit yuzu boss ekseninden), +X'ten bakis
    bx = BOSS_X[s]
    kutu = Part.makeBox(300, 300, 300, V(bx - 300, YT - 100, ZT - 200))
    gizle = []
    for o in par + ekli:
        vo = gd.getObject(o.Name)
        if not vo.Visibility:
            continue
        vo.Visibility = False
        gizle.append(o)
        try:
            c = o.Shape.common(kutu)
        except Exception:
            continue
        if c.Volume > 1e-3:
            n = doc.addObject("Part::Feature", "K_" + o.Name)
            n.Shape = c
            boya(n, vo.ShapeColor, 0 if o not in kabuk else 0)
            ekli.append(n)
    kamera(v, (1, 0, 0), 120, (bx, YT + 58.0, ZT - 55.0))
    Gui.updateGui()
    v.saveImage(os.path.join(OUT, "HAT-%s-kesit.png" % s), 1200, 1000, "White")
    log(s, "kesit")
    App.closeDocument(doc.Name)


def guvenli():
    try:
        for s in ("0", "a", "b"):
            bir(s)
        log("BITTI")
    except Exception:
        log(traceback.format_exc())
    Gui.getMainWindow().close()


QtCore.QTimer.singleShot(3000, guvenli)
