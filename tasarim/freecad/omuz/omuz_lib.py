# Omuz modulu - parca ve baglanti elemani kutuphanesi (FreeCAD 1.1, Part)
# Koordinat: X disari (sag omuz), Y yukari, Z ileri. Birim mm. Ev pozu: kol asagida.
import math
import FreeCAD as App
import Part

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


# ------------------------------------------------------------------ standart elemanlar
# DIN 912 imbus civata: (dk, k, s anahtar)
DIN912 = {3: (5.5, 3.0, 2.5), 4: (7.0, 4.0, 3.0), 5: (8.5, 5.0, 4.0), 6: (10.0, 6.0, 5.0)}
CLEAR = {3: 3.4, 4: 4.5, 5: 5.5, 6: 6.6}           # gecme delik
NUT934 = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0), 6: (10.0, 5.0)}
NUT985 = {3: (5.5, 4.0), 4: (7.0, 5.0), 5: (8.0, 5.0), 6: (10.0, 6.0)}   # kontra (naylon) somun
WASH125 = {3: (3.2, 7.0, 0.5), 4: (4.3, 9.0, 0.8), 5: (5.3, 10.0, 1.0), 6: (6.4, 12.0, 1.6)}
INSERT = {3: (4.6, 5.7), 5: (7.0, 7.0)}            # isil gomme somun: dis cap, boy (tahmini tipik)


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
    """Cekic somun (kanal 10): p_top = ust yuzu merkezi (dudak alti), normal = profil disina dogru."""
    n = unit(normal)
    a = unit(long_dir)
    b = n.cross(a)
    p = V(*p_top)
    c0 = p - n * T - a * (L / 2) - b * (W / 2)
    pts = [c0, c0 + a * L, c0 + a * L + b * W, c0 + b * W, c0]
    blk = Part.Face(Part.makePolygon(pts)).extrude(n * T)
    return blk.cut(Part.makeCylinder(d / 2, T + 2, p - n * (T + 1), n))


# ------------------------------------------------------------------ servo (DS3218MG)
DS = dict(L=40.0, W=20.0, H=40.4, TAB=54.5, TAB_TOP=40.4 - 27.7 - 2.5, TAB_T=2.5, SH=10.0, HOLE=4.6,
          HOLE_DX=5.0, HOLE_DY=24.75)
HORN = dict(R=12.5, Z0=2.0, Z1=5.3, PCD_R=8.5, HOLE_D=3.0)   # 25T aluminyum disk horn (delik dizilimi dogrulanacak)


def servo_local():
    """Yerel: mil +Z, orijin govde ust yuzunde mil merkezi; govde y in [-(L-SH), SH] -> [-30, 10], z in [-H, 0]."""
    L, W, H, SH = DS['L'], DS['W'], DS['H'], DS['SH']
    body = box(-W / 2, W / 2, -(L - SH), SH, -H, 0)
    ext = (DS['TAB'] - L) / 2
    tz1 = -DS['TAB_TOP']
    tz0 = tz1 - DS['TAB_T']
    tabs = box(-W / 2, W / 2, -(L - SH) - ext, SH + ext, tz0, tz1)
    yc = (SH - (L - SH)) / 2
    for yy in (yc - DS['HOLE_DY'], yc + DS['HOLE_DY']):
        for xx in (-DS['HOLE_DX'], DS['HOLE_DX']):
            tabs = tabs.cut(cyl(DS['HOLE'] / 2, (xx, yy, tz0 - 1), (xx, yy, tz1 + 1)))
    body = body.fuse(tabs).removeSplitter()
    dome = cyl(6.5, (0, 0, 0), (0, 0, HORN['Z0'])).fuse(cyl(2.9, (0, 0, HORN['Z0']), (0, 0, HORN['Z1'])))
    dome = dome.cut(cyl(1.5, (0, 0, -1), (0, 0, HORN['Z1'] + 1)))
    return body, dome, yc


def horn_local():
    h = cyl(HORN['R'], (0, 0, HORN['Z0']), (0, 0, HORN['Z1']))
    h = h.cut(cyl(3.0, (0, 0, HORN['Z0'] - 1), (0, 0, HORN['Z1'] + 1)))
    holes = []
    for i in range(4):
        a = math.radians(45 + 90 * i)
        x, y = HORN['PCD_R'] * math.cos(a), HORN['PCD_R'] * math.sin(a)
        holes.append((x, y))
        h = h.cut(cyl(HORN['HOLE_D'] / 2, (x, y, HORN['Z0'] - 1), (x, y, HORN['Z1'] + 1)))
    return h, holes


def horn_center_screw_local():
    # M3 x 5 horn merkez vidasi: kafa horn ustunde, govde spline icinde
    return screw912(3, 5.0, (0, 0, HORN['Z1']), (0, 0, -1))


# ------------------------------------------------------------------ sigma 40x40 agir
def sigma_kesit():
    SG, R_DIS, SLOT, LIP, CAV_W, CAV_D, CAV_TAB = 40.0, 1.5, 10.2, 4.3, 20.0, 7.5, 13.0
    CAV_DIK = CAV_D - (CAV_W - CAV_TAB) / 2
    h = SG / 2
    i = h - R_DIS
    s = Part.Face(Part.makePolygon([V(-i, -i, 0), V(i, -i, 0), V(i, i, 0), V(-i, i, 0), V(-i, -i, 0)])).makeOffset2D(R_DIS)
    for aci in (0, 90, 180, 270):
        agiz = Part.makePlane(SLOT, LIP + 1, V(-SLOT / 2, h - LIP, 0))
        y0 = h - LIP
        ic = Part.Face(Part.makePolygon([
            V(-CAV_W / 2, y0, 0), V(CAV_W / 2, y0, 0), V(CAV_W / 2, y0 - CAV_DIK, 0),
            V(CAV_TAB / 2, y0 - CAV_D, 0), V(-CAV_TAB / 2, y0 - CAV_D, 0),
            V(-CAV_W / 2, y0 - CAV_DIK, 0), V(-CAV_W / 2, y0, 0)]))
        k = agiz.fuse(ic)
        k.rotate(V(0, 0, 0), V(0, 0, 1), aci)
        s = s.cut(k)
    s = s.cut(Part.Face(Part.Wire(Part.makeCircle(4.5, V(0, 0, 0)))))
    for (cx, cy) in ((15.1, 15.1), (-15.1, 15.1), (15.1, -15.1), (-15.1, -15.1)):
        s = s.cut(Part.Face(Part.Wire(Part.makeCircle(2.55, V(cx, cy, 0)))))
    return s.removeSplitter()


def sigma_x(x0, x1):
    """X ekseni boyunca sigma: kesit YZ duzleminde."""
    f = sigma_kesit()
    f.rotate(V(0, 0, 0), V(0, 1, 0), 90)   # XY -> ZY (normal +X)
    f.translate(V(x0, 0, 0))
    return f.extrude(V(x1 - x0, 0, 0))
