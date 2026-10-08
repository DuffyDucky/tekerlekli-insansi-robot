# Dirsek modulu - parca kutuphanesi (FreeCAD 1.1, Part)
# Genel elemanlar ../ortak_lib.py'de; burada dirsege ozgu: MG996R servo ve 25T disk horn, ISO 7380 (kabuk_lib'den),
# baski analizi (kabuk_montaj.baski_analiz ile ayni yontem: X2D'ye sigma, 45 derece cikinti orani, 1 mm katmanlarla
# desteksiz basilabilirlik; kabuk dosyasi import edilince tum kabuk montaji calistigi icin buraya kopyalandi).
import os, sys, math
import FreeCAD as App
import Part

_HERE = os.path.dirname(os.path.abspath(__file__))
_UST = os.path.dirname(_HERE)
for _p in (_UST, os.path.join(_UST, "kabuk")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from ortak_lib import *   # noqa
import arayuz as A
from kabuk_lib import screw7380   # noqa  ISO 7380 bombe basli M3 (kabukla ayni cizim)

# ------------------------------------------------------------------ MG996R (04: Tower Pro datasheet)
# 40,7 x 19,7; kasa ustu 36,6; mil ustu 42,9 (horn dahil 47,6); kulaklarla 53,6; kulak alt yuzu tabandan 26,6; 25T.
# Kulak delik dizilimi ve mil kacikligi robot_cad servo() ile ayni (rc:271-287: delikler govde merkezinden +-24,75 / +-5,
# mil govde ucundan 10,2). Kulak delik capi 4,6 (rc).
MG = dict(L=40.7, W=19.7, H=36.6, TAB=53.6, TAB_TOP=36.6 - 26.6 - 2.5, TAB_T=2.5, SH=10.2, HOLE=4.6,
          HOLE_DX=5.0, HOLE_DY=24.75, MIL_UST=42.9 - 36.6, kutle_g=55.0)
# 25T aluminyum disk horn (omuzdaki ile ayni tip). Horn alt yuzu kasa ustunden 3,0 (tahmini), ust yuzu mil ucuyla ayni (6,3).
HORN_MG = dict(R=12.5, Z0=3.0, Z1=MG["MIL_UST"], PCD_R=8.5, HOLE_D=3.0)


def mg996r_local():
    """Yerel: mil +Z, orijin kasa ust yuzunde mil merkezi; govde y in [-(L-SH), SH], z in [-H, 0] (omuz servo_local gibi).
    Doner (govde+kulaklar, cikis mili (kubbe + dis), govde merkezi y)."""
    L, W, H, SH = MG["L"], MG["W"], MG["H"], MG["SH"]
    body = box(-W / 2, W / 2, -(L - SH), SH, -H, 0)
    ext = (MG["TAB"] - L) / 2
    tz1 = -MG["TAB_TOP"]
    tz0 = tz1 - MG["TAB_T"]
    tabs = box(-W / 2, W / 2, -(L - SH) - ext, SH + ext, tz0, tz1)
    yc = (SH - (L - SH)) / 2
    for yy in (yc - MG["HOLE_DY"], yc + MG["HOLE_DY"]):
        for xx in (-MG["HOLE_DX"], MG["HOLE_DX"]):
            tabs = tabs.cut(cyl(MG["HOLE"] / 2, (xx, yy, tz0 - 1), (xx, yy, tz1 + 1)))
    body = body.fuse(tabs).removeSplitter()
    dome = cyl(6.5, (0, 0, 0), (0, 0, 2.0)).fuse(cyl(2.9, (0, 0, 2.0), (0, 0, HORN_MG["Z1"])))
    dome = dome.cut(cyl(1.5, (0, 0, -1), (0, 0, HORN_MG["Z1"] + 1)))
    return body, dome.removeSplitter(), yc


def mg_delikler():
    """Kulak delikleri (yerel x, y) ve kulak yuzleri z: (taban tarafi, mil tarafi)."""
    yc = (MG["SH"] - (MG["L"] - MG["SH"])) / 2
    tz1 = -MG["TAB_TOP"]
    return [(xx, yy) for yy in (yc - MG["HOLE_DY"], yc + MG["HOLE_DY"]) for xx in (-MG["HOLE_DX"], MG["HOLE_DX"])], \
        (tz1 - MG["TAB_T"], tz1)


def horn_mg_local():
    h = cyl(HORN_MG["R"], (0, 0, HORN_MG["Z0"]), (0, 0, HORN_MG["Z1"]))
    h = h.cut(cyl(3.0, (0, 0, HORN_MG["Z0"] - 1), (0, 0, HORN_MG["Z1"] + 1)))
    holes = []
    for i in range(4):
        a = math.radians(45 + 90 * i)
        x, y = HORN_MG["PCD_R"] * math.cos(a), HORN_MG["PCD_R"] * math.sin(a)
        holes.append((x, y))
        h = h.cut(cyl(HORN_MG["HOLE_D"] / 2, (x, y, HORN_MG["Z0"] - 1), (x, y, HORN_MG["Z1"] + 1)))
    return h, holes


def horn_vidasi_local():
    """M3 x 5 horn merkez vidasi (servo ile gelir): kafa horn ustunde, govde mil deliginde."""
    return screw912(3, 5.0, (0, 0, HORN_MG["Z1"]), (0, 0, -1))


def yerlestir_m(shape, m):
    s = shape.copy()
    s.transformShape(m, True)
    return s


def koni(r0, r1, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return Part.makeCone(r0, r1, d.Length, p0, d.normalize())


def prizma(pts2, eksen, z0, z1):
    """pts2: duzlem noktalari (a, b) listesi; eksen 'x' -> (y, z) duzleminde, x z0..z1; 'z' -> (x, y), z z0..z1."""
    if eksen == "x":
        P3 = [V(z0, a, b) for (a, b) in pts2]
        d = V(z1 - z0, 0, 0)
    elif eksen == "z":
        P3 = [V(a, b, z0) for (a, b) in pts2]
        d = V(0, 0, z1 - z0)
    else:
        P3 = [V(a, z0, b) for (a, b) in pts2]
        d = V(0, z1 - z0, 0)
    return Part.Face(Part.makePolygon(P3 + [P3[0]])).extrude(d)


# ------------------------------------------------------------------ baski analizi (kabuk_montaj.baski_analiz ile ayni)
BRIDGE = 15.0        # bu boydan uzun desteksiz bolge = destek gerekir (tahmini; 2 mm'den dar seritler haric)


def baski_analiz(ad, sh, yukari, doluluk):
    import numpy as np
    import MeshPart
    Y = A.YAZICI
    UX, UY, UZ = Y["kullanilabilir"]
    rot = App.Rotation(V(*yukari), V(0, 0, 1))
    s = sh.copy()
    s.transformShape(App.Placement(V(0, 0, 0), rot).toMatrix(), True)
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.1, AngularDeflection=0.3)
    pts, tris = mesh.Topology
    X = np.array([[p.x, p.y, p.z] for p in pts])
    Tn = np.array(tris)
    zmin, zmax = X[:, 2].min(), X[:, 2].max()
    en = None
    for th in range(0, 91, 1):
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        x = X[:, 0] * c - X[:, 1] * s_
        y = X[:, 0] * s_ + X[:, 1] * c
        w, h = x.max() - x.min(), y.max() - y.min()
        w, h = max(w, h), min(w, h)
        if en is None or w < en[1]:
            en = (th, w, h)
    sigar = en[1] <= UX and en[2] <= UY and (zmax - zmin) <= UZ
    sigar_cift = en[1] <= Y["kullanilabilir_cift"][1] and en[2] <= Y["kullanilabilir_cift"][0] and (zmax - zmin) <= Y["kullanilabilir_cift"][2]
    a, b, c3 = X[Tn[:, 0]], X[Tn[:, 1]], X[Tn[:, 2]]
    cr = np.cross(b - a, c3 - a)
    alan = 0.5 * np.linalg.norm(cr, axis=1)
    nz = cr[:, 2] / np.maximum(2 * alan, 1e-12)
    zc = (a[:, 2] + b[:, 2] + c3[:, 2]) / 3
    tabla = zc < zmin + 0.05
    cik = (nz < -math.cos(math.radians(45))) & ~tabla
    oran = float(alan[cik].sum() / alan.sum())
    sorun = []
    onceki = None
    n_kat = int((zmax - zmin) // 1.0)
    for kk in range(n_kat):
        z = zmin + 0.5 + kk * 1.0
        try:
            ws = s.slice(V(0, 0, 1), z)
            yuz = Part.makeFace(ws, "Part::FaceMakerBullseye") if ws else None
        except Exception:
            yuz = None
        if yuz is not None and onceki is not None:
            try:
                dest = [f.makeOffset2D(1.0, 0) for f in onceki.Faces]
                dest = dest[0].fuse(dest[1:]) if len(dest) > 1 else dest[0]
                dest.translate(V(0, 0, 1.0))
                acik = yuz.cut(dest)
            except Exception as e:
                acik = None
                sorun.append(dict(z=round(z - zmin, 1), hata=repr(e)[:80]))
            if acik is not None:
                for f in acik.Faces:
                    if f.Area < 0.5:
                        continue
                    try:
                        dar = f.makeOffset2D(-1.0, 0)
                        dar_alan = sum(g.Area for g in dar.Faces)
                    except Exception:
                        dar_alan = 0.0
                    boy = max(f.BoundBox.XLength, f.BoundBox.YLength)
                    if dar_alan > 0.01 and boy > BRIDGE:
                        sorun.append(dict(z=round(z - zmin, 1), alan=round(f.Area, 1), boy=round(boy, 1)))
        onceki = yuz
    hac = sh.Volume
    kutle = hac / 1000 * A.PETG_RHO * doluluk
    return dict(ad=ad, olcu=[round(en[1], 1), round(en[2], 1), round(zmax - zmin, 1)], tabla_aci=en[0], sigar=bool(sigar),
                sigar_cift=bool(sigar_cift), cikinti_orani=round(oran, 4), cikinti_alan_cm2=round(float(alan[cik].sum()) / 100, 2),
                yuzey_cm2=round(float(alan.sum()) / 100, 1), destek_sorun=sorun[:20], destek_sorun_sayi=len(sorun),
                desteksiz=len(sorun) == 0, hacim_cm3=round(hac / 1000, 1), kutle_g=round(kutle, 1),
                filament_g=round(kutle * 1.05, 1), sure_saat=round(hac * doluluk / A.PETG_HACIM_HIZI / 3600, 2),
                katman=n_kat)
