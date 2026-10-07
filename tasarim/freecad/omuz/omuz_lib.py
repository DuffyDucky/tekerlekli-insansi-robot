# Omuz modulu - parca kutuphanesi (FreeCAD 1.1, Part)
# Koordinat: X disari (sag omuz), Y yukari, Z ileri. Birim mm. Ev pozu: kol asagida.
# Genel elemanlar (box/cyl/hexprism, DIN 912/934/985/125, isil gomme somun, cekic somun, rulman, sigma)
# ../ortak_lib.py'de; burada yalniz omuza ozgu servo ve horn var. "from omuz_lib import *" eskisi gibi hepsini verir.
import os, sys, math
import FreeCAD as App
import Part

_UST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _UST not in sys.path:
    sys.path.insert(0, _UST)
from ortak_lib import *   # noqa  (V, box, cyl, hexprism, unit, DIN912, CLEAR, NUT934, NUT985, WASH125, INSERT,
#                                  screw912, nut, washer, insert, insert_hole, bearing, hammer_nut, sigma_kesit, sigma_x)


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
