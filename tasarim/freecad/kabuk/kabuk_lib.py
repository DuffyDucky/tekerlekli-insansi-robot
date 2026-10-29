# Kabuk modulu - parca kutuphanesi (FreeCAD 1.1, Part). Genel elemanlar ../ortak_lib.py'de; burada kabuga ozgu:
# yuvarlatilmis dikdortgen kesit, cizgisel (ruled) loft zarf, damla (teardrop) boss, ISO 7380 bombe basli civata,
# kesit parametreleri (analitik: ruled loft'ta ara kesit = dogrusal ara deger).
import os, sys, math
import FreeCAD as App
import Part

_UST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UST not in sys.path:
    sys.path.insert(0, _UST)
from ortak_lib import *   # noqa
import arayuz as A

C45 = math.sqrt(0.5)


# ------------------------------------------------------------------ kesit ve zarf
def kesit_param(secs, y):
    """Kesit tablosunda y yuksekligindeki (a, bf, bb, r) ve y'ye gore egimleri (da, dbf, dbb, dr)."""
    for i in range(len(secs) - 1):
        y0, y1 = secs[i][0], secs[i + 1][0]
        if y0 - 1e-9 <= y <= y1 + 1e-9:
            t = (y - y0) / (y1 - y0)
            v = [secs[i][k] + (secs[i + 1][k] - secs[i][k]) * t for k in range(1, 5)]
            d = [(secs[i + 1][k] - secs[i][k]) / (y1 - y0) for k in range(1, 5)]
            return v, d
    raise ValueError("y kesit araliginda degil: %.1f" % y)


def rrect_wire(y, a, bf, bb, r):
    """y duzleminde yuvarlatilmis dikdortgen: x +-a, z on = bf, arka = -bb, kose r. Her kesit ayni kenar sirasinda."""
    P = lambda x, z: V(x, y, z)
    e = [Part.LineSegment(P(-(a - r), bf), P(a - r, bf))]
    cx, cz = a - r, bf - r
    e.append(Part.Arc(P(cx, cz + r), P(cx + r * C45, cz + r * C45), P(cx + r, cz)))
    e.append(Part.LineSegment(P(a, bf - r), P(a, -(bb - r))))
    cx, cz = a - r, -(bb - r)
    e.append(Part.Arc(P(cx + r, cz), P(cx + r * C45, cz - r * C45), P(cx, cz - r)))
    e.append(Part.LineSegment(P(a - r, -bb), P(-(a - r), -bb)))
    cx, cz = -(a - r), -(bb - r)
    e.append(Part.Arc(P(cx, cz - r), P(cx - r * C45, cz - r * C45), P(cx - r, cz)))
    e.append(Part.LineSegment(P(-a, -(bb - r)), P(-a, bf - r)))
    cx, cz = -(a - r), bf - r
    e.append(Part.Arc(P(cx - r, cz), P(cx - r * C45, cz + r * C45), P(cx, cz + r)))
    return Part.Wire([x.toShape() for x in e])


def zarf(secs, e, alt_uzat=10.0):
    """Kesitlerden e kadar (yatay) iceri alinmis kati. e > 0: alt uc acik (asagi uzatilir), ust kapak e kalinlikta."""
    s2 = [(y, a - e, bf - e, bb - e, r - e) for (y, a, bf, bb, r) in secs]
    if e > 0:
        s2 = [(s2[0][0] - alt_uzat,) + tuple(s2[0][1:])] + s2
    sol = Part.makeLoft([rrect_wire(*s) for s in s2], True, True)
    if e > 0:
        sol = sol.common(box(-2000, 2000, -2000, secs[-1][0] - e, -2000, 2000))
    return sol


def rrect_prizma_z(x0, x1, y0, y1, r_alt, z0, z1):
    """XY'de alt koseleri r_alt yuvarlak dikdortgen, z0 -> z1 boyunca (arka kapak bolgesi)."""
    P = lambda x, y: V(x, y, z0)
    r = r_alt
    e = [Part.LineSegment(P(x0, y1), P(x0, y0 + r)),
         Part.Arc(P(x0, y0 + r), P(x0 + r - r * C45, y0 + r - r * C45), P(x0 + r, y0)),
         Part.LineSegment(P(x0 + r, y0), P(x1 - r, y0)),
         Part.Arc(P(x1 - r, y0), P(x1 - r + r * C45, y0 + r - r * C45), P(x1, y0 + r)),
         Part.LineSegment(P(x1, y0 + r), P(x1, y1)),
         Part.LineSegment(P(x1, y1), P(x0, y1))]
    return Part.Face(Part.Wire([x.toShape() for x in e])).extrude(V(0, 0, z1 - z0))


# ------------------------------------------------------------------ yuzey noktasi + normal (duz yuzlerde)
def yuzey(secs, yer, y, u, e=None):
    """Kabugun duz bir yuzunde orta yuzey (e = T/2) noktasi, disa normal ve normal dogrultusunda yari kalinlik.
    yer: 'on' (u = x), 'arka' (u = x), 'sag' / 'sol' (u = z). Doner (P_orta, n, yari_kalinlik_normal)."""
    T = A.KABUK_T
    e = T / 2 if e is None else e
    (a, bf, bb, r), (da, dbf, dbb, dr) = kesit_param(secs, y)
    if yer == "on":
        p, n, h = V(u, y, bf - e), V(0, -dbf, 1), V(0, 0, 1)
    elif yer == "arka":
        p, n, h = V(u, y, -(bb - e)), V(0, -dbb, -1), V(0, 0, -1)
    elif yer == "sag":
        p, n, h = V(a - e, y, u), V(1, -da, 0), V(1, 0, 0)
    else:
        p, n, h = V(-(a - e), y, u), V(-1, -da, 0), V(-1, 0, 0)
    n.normalize()
    return p, n, e * h.dot(n)


# ------------------------------------------------------------------ boss, civata
def damla(p0, eksen, r, L, asagi):
    """Damla (teardrop) boss: p0'dan eksen yonunde L boyunda O2r silindir + baski asagi yonune 45 derece sivri uc.
    Yatay eksenli boss'un alt yuzu boylece 45 derecede kalir (desteksiz basilir)."""
    ax = unit(eksen)
    p0 = V(*p0)
    cyl_ = Part.makeCylinder(r, L, p0, ax)
    d = V(*asagi)
    d = d - ax * d.dot(ax)
    if d.Length < 0.2:                       # eksen dikey: duz silindir yeter
        return cyl_
    d.normalize()
    e = ax.cross(d)
    tp = p0 + e * (r * C45) + d * (r * C45)
    tm = p0 - e * (r * C45) + d * (r * C45)
    ap = p0 + d * (r * math.sqrt(2))
    tri = Part.Face(Part.makePolygon([p0, tp, ap, tm, p0])).extrude(ax * L)
    return cyl_.fuse(tri).removeSplitter()


def screw7380(d, L, p, direction):
    """ISO 7380 bombe basli imbus (bas silindirle yaklasik): p = bas alt yuzu merkezi, direction = govdenin gittigi yon."""
    dk, k, s = A.ISO7380[d]
    u = unit(direction)
    p = V(*p)
    head = Part.makeCylinder(dk / 2, k, p - u * k, u)
    head = head.cut(hexprism(s, p - u * (k + 0.1), p - u * (k * 0.35)))
    return head.fuse(Part.makeCylinder(d / 2, L, p, u)).removeSplitter()


def percin_somun(pc, p, direction):
    """Duz flansli percin somun, takilmis hal (M6 K1/K2, Y3): p = flansin oturdugu sac yuzu, direction = govdenin saca girdigi yon.
    pc = arayuz.M6[...]["percin"] (d, flans_d, flans_t, govde_d, govde_L). Ic delik civata capinda (dis), cokme bolgesi cizilmez."""
    u = unit(direction)
    p = V(*p)
    fl = Part.makeCylinder(pc["flans_d"] / 2, pc["flans_t"], p - u * pc["flans_t"], u)
    gv = Part.makeCylinder(pc["govde_d"] / 2, pc["govde_L"], p, u)
    return fl.fuse(gv).cut(Part.makeCylinder(pc["d"] / 2, pc["flans_t"] + pc["govde_L"] + 2, p - u * (pc["flans_t"] + 1), u)).removeSplitter()


# (Nextion ekran cercevesi yardimcilari 1,65 m'de kaldirildi: gogus ekrani yok; Duffy, 25 Ekim 2026)
