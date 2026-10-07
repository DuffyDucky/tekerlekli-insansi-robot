# Ortak parca kutuphanesi (FreeCAD 1.1, Part): temel govdeler, standart baglanti elemanlari, sigma profil,
# kose baglantilari. Olculer arayuz.py'den gelir; sigma kesiti sigma_profil.py'deki dogrulanmis kesittir.
# Modul kutuphaneleri (omuz_lib.py ...) bunu "from ortak_lib import *" ile alir.
import os, sys, math
import FreeCAD as App
import Part

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from arayuz import DIN912, CLEAR, NUT934, NUT985, WASH125, INSERT, DIN913, CEKIC_SOMUN, KOSE, IC_KOSE   # noqa
from arayuz import LIP, KANAL_TABAN                                                                  # noqa
from sigma_profil import kesit as _sigma_kesit

V = App.Vector


# ------------------------------------------------------------------ temel govdeler
def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, p0, p1):
    """p0'dan p1'e silindir (eksen keyfi)."""
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return Part.makeCylinder(r, d.Length, p0, d.normalize())


def hexprism(s, p0, p1, flat_dir=None):
    """Altigen prizma: anahtar agzi s, p0 -> p1 ekseni. flat_dir: bir duz yuzun bakacagi yon."""
    p0, p1 = V(*p0), V(*p1)
    ax = (p1 - p0)
    h = ax.Length
    ax.normalize()
    if flat_dir is None:
        flat_dir = V(1, 0, 0) if abs(ax.x) < 0.9 else V(0, 1, 0)
    u = V(*flat_dir)
    u = (u - ax * u.dot(ax)).normalize()
    w = ax.cross(u)
    rc = s / math.sqrt(3)  # kose yaricapi
    pts = []
    for i in range(6):
        a = math.radians(30 + 60 * i)  # 0 derecede duz yuz u yonune bakar
        pts.append(p0 + u * (rc * math.cos(a)) + w * (rc * math.sin(a)))
    pts.append(pts[0])
    f = Part.Face(Part.makePolygon(pts))
    return f.extrude(ax * h)


def unit(v):
    v = V(*v)
    return v.normalize()


def yerlestir(shape, m):
    """Geometriyi kopyalayarak tasir (transformShape(m, True)); kopyasiz hali konumu yalniz Placement'a yazar
    ve Part::Feature'a atanip kaydedilince kaybolur. m: App.Matrix veya App.Placement."""
    s = shape.copy()
    if isinstance(m, App.Placement):
        m = m.toMatrix()
    s.transformShape(m, True)
    return s


def matris(e1, e2, e3, t):
    """Yerel X,Y,Z -> e1,e2,e3 (sutunlar) + oteleme t. Sag elli olmali (det = +1)."""
    m = App.Matrix(e1[0], e2[0], e3[0], t[0], e1[1], e2[1], e3[1], t[1], e1[2], e2[2], e3[2], t[2], 0, 0, 0, 1)
    if abs(m.determinant() - 1.0) > 1e-9:
        raise ValueError("matris sag elli degil")
    return m


# ------------------------------------------------------------------ standart elemanlar
def screw912(d, L, p, direction):
    """Imbus civata. p: kafa alt yuzu merkezi, direction: govdenin gittigi yon."""
    dk, k, s = DIN912[d]
    u = unit(direction)
    p = V(*p)
    head = Part.makeCylinder(dk / 2, k, p - u * k, u)
    sock = hexprism(s, p - u * (k + 0.1), p - u * (k * 0.4))
    head = head.cut(sock)
    shank = Part.makeCylinder(d / 2, L, p, u)
    return head.fuse(shank).removeSplitter()


def setscrew913(d, L, p, direction):
    """DIN 913 set (grub) vida, duz uclu. p: ust (anahtar) yuzu merkezi, direction: vidanin ilerledigi yon."""
    u = unit(direction)
    p = V(*p)
    g = Part.makeCylinder(d / 2, L, p, u)
    s = DIN913[d]
    return g.cut(hexprism(s, p - u * 0.1, p + u * (0.6 * d)))


def nut(d, p, direction, kind="985", flat_dir=None):
    s, m = (NUT985 if kind == "985" else NUT934)[d]
    u = unit(direction)
    p = V(*p)
    n = hexprism(s, p, p + u * m, flat_dir)
    return n.cut(Part.makeCylinder(d / 2, m + 2, p - u, u))


def washer(d, p, direction):
    di, do, t = WASH125[d]
    u = unit(direction)
    p = V(*p)
    return Part.makeCylinder(do / 2, t, p, u).cut(Part.makeCylinder(di / 2, t + 2, p - u, u))


def insert(d, p, direction):
    """Isil gomme somun: p = agiz yuzu, direction = deligin icine dogru. Ic cap = civata capi."""
    od, L = INSERT[d]
    u = unit(direction)
    p = V(*p)
    return Part.makeCylinder(od / 2, L, p, u).cut(Part.makeCylinder(d / 2, L + 2, p - u, u))


def insert_hole(d, p, direction, extra=0.5):
    od, L = INSERT[d]
    u = unit(direction)
    return Part.makeCylinder(od / 2, L + extra, V(*p), u)


def bearing(di, do, w, p, direction, ri_out, ro_in):
    """Rulman: ic bilezik ve dis bilezik ayri (bilyeler cizilmedi)."""
    u = unit(direction)
    p = V(*p)
    inner = Part.makeCylinder(ri_out, w, p, u).cut(Part.makeCylinder(di / 2, w + 2, p - u, u))
    outer = Part.makeCylinder(do / 2, w, p, u).cut(Part.makeCylinder(ro_in, w + 2, p - u, u))
    return inner, outer


def hammer_nut(p_top, normal, long_dir, d=6, L=16.0, W=10.0, T=5.0):
    """Cekic somun (kanal 10): p_top = ust yuzu merkezi (dudak alti), normal = profil disina dogru.
    long_dir: kilitli konumda uzun kenar (kanala dik). Varsayilanlar arayuz.CEKIC_SOMUN ile ayni."""
    n = unit(normal)
    a = unit(long_dir)
    b = n.cross(a)
    p = V(*p_top)
    c0 = p - n * T - a * (L / 2) - b * (W / 2)
    pts = [c0, c0 + a * L, c0 + a * L + b * W, c0 + b * W, c0]
    blk = Part.Face(Part.makePolygon(pts)).extrude(n * T)
    return blk.cut(Part.makeCylinder(d / 2, T + 2, p - n * (T + 1), n))


assert (CEKIC_SOMUN["d"], CEKIC_SOMUN["L"], CEKIC_SOMUN["W"], CEKIC_SOMUN["T"]) == (6, 16.0, 10.0, 5.0)


# ------------------------------------------------------------------ sigma 40x40 agir (sigma_profil.py kesiti)
def sigma_kesit():
    """XY duzleminde kesit yuzu (merkez orijinde)."""
    return _sigma_kesit()


def sigma_x(x0, x1):
    """X ekseni boyunca sigma: kesit YZ duzleminde, eksen y = z = 0."""
    f = sigma_kesit()
    f.rotate(V(0, 0, 0), V(0, 1, 0), 90)   # XY -> ZY (normal +X)
    f.translate(V(x0, 0, 0))
    return f.extrude(V(x1 - x0, 0, 0))


def sigma_y(y0, y1, x=0.0, z=0.0):
    """Y ekseni boyunca sigma (eksen x, z)."""
    f = sigma_kesit()
    f.rotate(V(0, 0, 0), V(1, 0, 0), -90)  # XY -> XZ (normal +Y)
    f.translate(V(x, y0, z))
    return f.extrude(V(0, y1 - y0, 0))


def sigma_z(z0, z1, x=0.0, y=0.0):
    """Z ekseni boyunca sigma (eksen x, y)."""
    f = sigma_kesit()
    f.translate(V(x, y, z0))
    return f.extrude(V(0, 0, z1 - z0))


# ------------------------------------------------------------------ 40x40 genis kose baglanti (satin alinan)
def _oval(merkez, eksen, boy, cap, p_alt, p_ust):
    """Oval delik govdesi: merkez boyunca 'eksen' yonunde boy uzunlukta, cap genislikte; p_alt -> p_ust derinlik."""
    m = V(*merkez)
    a = unit(eksen)
    d = V(*p_ust) - V(*p_alt)
    h = (boy - cap) / 2
    s = Part.makeCylinder(cap / 2, d.Length, m - a * h + V(*p_alt), unit(d))
    s = s.fuse(Part.makeCylinder(cap / 2, d.Length, m + a * h + V(*p_alt), unit(d)))
    c = a.cross(unit(d))
    q0 = m - a * h - c * (cap / 2) + V(*p_alt)
    pts = [q0, q0 + a * (2 * h), q0 + a * (2 * h) + c * cap, q0 + c * cap, q0]
    return s.fuse(Part.Face(Part.makePolygon(pts)).extrude(d))


def kose_baglanti():
    """Yerel: kose orijinde. Ayak A y=0 yuzune yatar, +X'e uzanir (profili y<0'da); ayak B x=0 yuzune dayanir, +Y'ye
    uzanir (profili x<0'da). Genislik Z'de +-W/2. Kamalar profil kanal agzina girer."""
    A, B, W, T, D = KOSE["A"], KOSE["B"], KOSE["W"], KOSE["T"], KOSE["DUVAR"]
    s = box(0, A, 0, T, -W / 2, W / 2).fuse(box(0, T, 0, B, -W / 2, W / 2))
    ceyrek = Part.makeCylinder(A, W, V(0, 0, -W / 2), V(0, 0, 1)).common(box(0, A, 0, B, -W / 2, W / 2))
    for z0, z1 in ((-W / 2, -W / 2 + D), (W / 2 - D, W / 2)):
        s = s.fuse(ceyrek.common(box(0, A, 0, B, z0, z1)))
    kw, kh, k0 = KOSE["KAMA_W"], KOSE["KAMA_H"], KOSE["KAMA_X0"]
    s = s.fuse(box(k0, A, -kh, 0, -kw / 2, kw / 2)).fuse(box(-kh, 0, k0, B, -kw / 2, kw / 2))
    m, L, dc = KOSE["DELIK_M"], KOSE["DELIK_BOY"], KOSE["DELIK_D"]
    s = s.cut(_oval((m, 0, 0), (1, 0, 0), L, dc, (0, -kh - 1, 0), (0, T + 1, 0)))
    s = s.cut(_oval((0, m, 0), (0, 1, 0), L, dc, (-kh - 1, 0, 0), (T + 1, 0, 0)))
    return s.removeSplitter()


def kose_baglanti_elemanlari():
    """Yerel cerceve (kose_baglanti ile ayni): her ayak icin (ad, sekil, kod) listesi: pul, civata, cekic somun.
    Civata kanal agzindan gecer; cekic somun ust yuzu dudak altinda, uzun kenari kanala dik (Z)."""
    T, m = KOSE["T"], KOSE["DELIK_M"]
    d, L = KOSE["civata"]
    t = WASH125[d][2]
    out = []
    for (p_yuz, n) in (((m, T, 0), (0, 1, 0)), ((T, m, 0), (1, 0, 0))):
        pv, nv = V(*p_yuz), V(*n)
        out.append(("pul", washer(d, pv, nv)))
        out.append(("civata", screw912(d, L, pv + nv * t, nv * -1)))
        p_somun = pv - nv * T - nv * LIP          # profil yuzu (ayak alti) - dudak
        out.append(("somun", hammer_nut(p_somun, nv, (0, 0, 1), d=d)))
    return out


# ------------------------------------------------------------------ ic kose baglanti, kanal 10 (tahmini olculer)
def ic_kose_baglanti():
    """Yerel: birlesim kosesi orijinde. Ayak 1 +X boyunca (profil 1 kanalinda, derinlik -Z), ayak 2 +Z boyunca
    (profil 2 kanalinda, derinlik -X). Y = kanal genisligi yonu. Profil 1 x>=0, z<=0'da; profil 2 x<=0'da.
    Doner: (govde, [set vida 1, set vida 2])."""
    G, bw, fw, ft, vm = IC_KOSE["LEG"], IC_KOSE["BOYUN_W"], IC_KOSE["FLANS_W"], IC_KOSE["FLANS_T"], IC_KOSE["VIDA_M"]
    dd = LIP + ft
    a1 = box(0, G, -bw / 2, bw / 2, -LIP, 0).fuse(box(0, G, -fw / 2, fw / 2, -dd, -LIP))
    a2 = box(-LIP, 0, -bw / 2, bw / 2, -dd, G).fuse(box(-dd, -LIP, -fw / 2, fw / 2, -dd, G))
    g = a1.fuse(a2)
    d, L = IC_KOSE["vida"]
    ust = KANAL_TABAN - L                                       # vida ust yuzu yuzden bu kadar iceride
    g = g.cut(cyl(d / 2, (vm, 0, 1), (vm, 0, -dd - 1))).cut(cyl(d / 2, (1, 0, vm), (-dd - 1, 0, vm)))
    v1 = setscrew913(d, L, (vm, 0, -ust), (0, 0, -1))
    v2 = setscrew913(d, L, (-ust, 0, vm), (-1, 0, 0))
    return g.removeSplitter(), [v1, v2]
