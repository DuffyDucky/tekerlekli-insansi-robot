# K2 kontrolu ortak yardimcilari (FreeCAD 1.1). Yalniz okur: FCStd dosyalari gecici kopyadan acilir.
import os, sys, json, math, time, shutil, tempfile, datetime, importlib.util
import FreeCAD as App
import Part
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(HERE, "..", ".."))
R = os.path.join(KOK, "tasarim", "freecad")
if R not in sys.path:
    sys.path.insert(0, R)
import arayuz as A

V = App.Vector
OY = A.MODULLER["omuz_sag"]["konum"]
XR = 185.0
D = A.DIRSEK
GIRDI = {}


def log(*a):
    print(*a, flush=True)


def yukle(ad):
    sp = importlib.util.spec_from_file_location(ad.replace("-", "_").replace(".py", ""), os.path.join(HERE, ad))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def ac(rel, etiket="K2"):
    src = os.path.join(R, rel)
    st = os.stat(src)
    dst = os.path.join(tempfile.gettempdir(), "%s_%d_%s" % (etiket, os.getpid(), os.path.basename(rel)))
    shutil.copy2(src, dst)
    GIRDI[rel] = datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
    d = App.openDocument(dst)
    out = []
    for o in d.Objects:
        if o.TypeId == "Part::Feature":
            par = o.getParentGeoFeatureGroup()
            s = o.Shape.copy()
            s.Placement = o.getGlobalPlacement()
            s = s.copy()
            out.append(dict(ad=o.Label, grup=par.Name if par else "-", shape=s, malzeme=getattr(o, "Malzeme", ""),
                            tur=getattr(o, "Tur", ""), kod=getattr(o, "Kod", ""), kutle_prop=getattr(o, "Kutle_g", None)))
    App.closeDocument(d.Name)
    try:
        os.remove(dst)
    except Exception:
        pass
    return out


def kabuk_yerel(KAB, sag=True):
    """Kabuk parcalari (global) -> sag omuz yereli; yalniz sag taraf (ad 'sag' icerir) ya da hepsi."""
    out = []
    for p in KAB:
        if sag and "sag" not in p["ad"]:
            continue
        s = p["shape"].copy()
        s.translate(V(-OY[0], -OY[1], -OY[2]))
        q = dict(p)
        q["shape"] = s
        out.append(q)
    return out


def Pp(phi):
    return App.Placement(V(0, 0, 0), App.Rotation(V(-1, 0, 0), phi), V(0, 0, 0))


def Pr(th):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th), V(XR, 0, 0))


def Pe(al):
    return App.Placement(V(0, 0, 0), App.Rotation(V(*D["eksen_yon"]), al), V(0, D["eksen_y"], D["eksen_z"]))


def Pb(be):
    return App.Placement(V(0, 0, 0), App.Rotation(V(*D["bilek_yon"]), be), V(D["bilek_x"], 0, D["bilek_z"]))


def tasi(s, pl):
    s = s.copy()
    s.transformShape(pl.toMatrix(), True)
    return s


def psi_yz(psi, r):
    a = math.radians(psi)
    return r * math.cos(a), -r * math.sin(a)


def yz_psi(y, z):
    return math.degrees(math.atan2(-z, y)) % 360.0, math.hypot(y, z)


def enaz(a_list, b_list, pay=10.0):
    """En kucuk mesafe (mesafe, a, b); sinir kutusu on elemesi."""
    best = (1e9, None, None)
    for a, sa in a_list:
        bba = App.BoundBox(sa.BoundBox)
        bba.enlarge(pay)
        for b, sb in b_list:
            if not bba.intersect(sb.BoundBox):
                continue
            dd = sa.distToShape(sb)[0]
            if dd < best[0]:
                best = (dd, a, b)
    return best


def kaydet(ad, OUT):
    OUT["girdi"] = GIRDI
    json.dump(OUT, open(os.path.join(HERE, ad), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
