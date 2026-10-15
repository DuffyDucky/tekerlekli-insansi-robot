# K kontrolu: S1 (on-arka) gecisi icin serbest bolge olcumu. Yalniz okur (FCStd gecici kopyalari), cikti K-s1.json.
# S1 ekseni omuz yerelinde X ekseni; S1 donusu x koordinatini degistirmez. Bu yuzden her parca grubu icin "S1 eksenine uzaklik r"
# dilimlerinde en kucuk / en buyuk x, S1'in butun pozlari icin gecerlidir. Kol grubu S2 (yana) pozuna bagli: 3, 5, 10, 20 derece.
# Calistir: FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
import os, sys, json, math, shutil, tempfile
import FreeCAD as App
import Part
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
sys.path.insert(0, R)
import arayuz as A
V = App.Vector


def ac(rel):
    dst = os.path.join(tempfile.gettempdir(), "K_s1_" + os.path.basename(rel))
    shutil.copy2(os.path.join(R, rel), dst)
    d = App.openDocument(dst)
    out = []
    for o in d.Objects:
        if o.TypeId == "Part::Feature":
            par = o.getParentGeoFeatureGroup()
            s = o.Shape.copy()
            s.Placement = o.getGlobalPlacement()
            out.append(dict(ad=o.Label, grup=par.Name if par else "-", shape=s))
    App.closeDocument(d.Name)
    return out


OMU, DIR, KAB = ac("omuz/omuz-montaj.FCStd"), ac("dirsek/dirsek-montaj.FCStd"), ac("kabuk/kabuk-montaj.FCStd")
oy = (0.0, 955.0, 0.0)


def noktalar(sh, pl=None, defl=0.15):
    s = sh.copy()
    if pl is not None:
        s.transformShape(pl.toMatrix(), True)
    P = []
    for f in s.Faces:
        try:
            pts, _ = f.tessellate(defl)
            P += [(p.x, p.y, p.z) for p in pts]
        except Exception:
            pass
    P += [(v.Point.x, v.Point.y, v.Point.z) for v in s.Vertexes]
    return np.array(P) if P else np.zeros((0, 3))


RB = np.arange(20.0, 80.1, 2.0)        # r dilimleri (S1 eksenine uzaklik)
X0, X1 = 140.0, 175.0


def kabuklar():
    out = []
    for a, b in zip(RB[:-1], RB[1:]):
        sh = Part.makeCylinder(b, X1 - X0, V(X0, 0, 0), V(1, 0, 0)).cut(Part.makeCylinder(a, X1 - X0 + 2, V(X0 - 1, 0, 0), V(1, 0, 0)))
        out.append(sh)
    return out


KAB_R = kabuklar()


def profil(sekiller, en_kucuk=True):
    """Her r dilimi (halka, x 140...175) icin sekillerin o halka icindeki en kucuk / en buyuk x'i (boolean, kesin)."""
    out = []
    for hal in KAB_R:
        best = None
        for s in sekiller:
            if not s.BoundBox.intersect(hal.BoundBox):
                continue
            try:
                c = s.common(hal)
            except Exception:
                continue
            if c.Volume < 1e-4:
                continue
            v = c.BoundBox.XMin if en_kucuk else c.BoundBox.XMax
            if best is None or (v < best if en_kucuk else v > best):
                best = v
        out.append(None if best is None else round(best, 2))
    return out


def tasi(sh, pl):
    s = sh.copy()
    s.transformShape(pl.toMatrix(), True)
    return s


def Pr(th):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th), V(185.0, 0, 0))


sonuc = dict(r_dilim=[float(a) for a in RB[:-1]], x_araligi=[X0, X1])
gov = [p["shape"] for p in OMU if p["grup"] == "Govde" and "referans" not in p["ad"].lower() and "civatasi" not in p["ad"]]
civ = [p["shape"] for p in OMU if p["ad"].startswith("Kapak civatasi")]
kabs = [tasi(p["shape"], App.Placement(V(-oy[0], -oy[1], -oy[2]), App.Rotation())) for p in KAB
        if p["ad"].startswith("Omuz bandi sag") or p["ad"].startswith("Gogus bandi sag")]
sonuc["govde_max_x"] = profil(gov, False)
sonuc["kapak_civata_max_x"] = profil(civ, False)
cb = Part.makeCompound(civ).BoundBox
sonuc["kapak_civata_bb"] = [round(v, 2) for v in (cb.XMin, cb.XMax)]
sonuc["kabuk_max_x"] = profil(kabs, False)
sonuc["gobek_min_x"] = profil([p["shape"] for p in OMU if p["grup"] == "Gobek"], True)
kol = [p["shape"] for p in OMU if p["grup"] == "Kol"] + [p["shape"] for p in DIR if p["grup"] == "UstKol"]
for th in (3, 5, 10, 20):
    sonuc["kol_min_x_S2_%d" % th] = profil([tasi(s_, Pr(th)) for s_ in kol], True)
kab = np.vstack([noktalar(s_, None, 0.3) for s_ in kabs])
# kabuk bandinin S1 cevresinde ust siniri (y) ve on/arka (z) siniri: x 147...152 duz yan duvar
m = (kab[:, 0] > 140) & (kab[:, 0] < 160)
sonuc["kabuk_y_max_x140_160"] = round(float(kab[m][:, 1].max()), 1) if m.any() else None
sonuc["kabuk_z_aralik_x140_160"] = [round(float(kab[m][:, 2].min()), 1), round(float(kab[m][:, 2].max()), 1)] if m.any() else None
json.dump(sonuc, open(os.path.join(HERE, "K-s1.json"), "w", encoding="utf-8"), indent=1)
print("r  govde kabuk civata gobek kol3 kol5 kol10")
for i, a in enumerate(sonuc["r_dilim"]):
    print(a, sonuc["govde_max_x"][i], sonuc["kabuk_max_x"][i], sonuc["kapak_civata_max_x"][i], sonuc["gobek_min_x"][i],
          sonuc["kol_min_x_S2_3"][i], sonuc["kol_min_x_S2_5"][i], sonuc["kol_min_x_S2_10"][i])
print("civata x", sonuc["kapak_civata_bb"], "kabuk y max", sonuc["kabuk_y_max_x140_160"], "z", sonuc["kabuk_z_aralik_x140_160"])
