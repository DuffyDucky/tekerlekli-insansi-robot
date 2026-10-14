# Tolerans kuponlari (FreeCAD 1.1, Part): buyuk parcalari basmadan once gecme olculerini denemek icin iki kucuk baski.
# Cikti: test/stl/*.stl + test/tolerans-kuponu.step. Baski koordinati: Z yukari (tabla), mm.
#
# Kupon A (PETG-CF basilir): 6808-2RS dis bilezigi (O52) icin 4 halka, delik O52,0 / 52,1 / 52,2 / 52,3, kalinlik 7 (rulman eni).
# Kupon B (PETG-CF + PETG, iki kez basilir):
#   - 625ZZ yuvasi (O16) 4 delik: O16,0 / 16,1 / 16,2 / 16,3, kalinlik 5 (rulman eni)
#   - 6808 ic bilezigi (O40) icin 4 boru mil: O39,8 / 39,9 / 40,0 / 40,1, boy 8
#   - M3 isil gomme somun deligi 4 adet: O3,8 / 3,9 / 4,0 / 4,1, derinlik 6,2 (arayuz.INSERT boy 5,7 + 0,5)
#   - M5 isil gomme somun deligi 3 adet: O6,2 / 6,4 / 6,6, derinlik 7,5
# Her olcunun yaninda nokta sayisi = sira (1 nokta en kucuk olcu). Secilen olcu arayuz.py'ye (INSERT_DELIK, rulman yuvasi) girer.
import os, sys
import FreeCAD as App
import Part
import MeshPart

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
if UST not in sys.path:
    sys.path.insert(0, UST)
from ortak_lib import box, cyl, V   # noqa
import arayuz as A

L_I3 = A.INSERT[3][1] + 0.5
L_I5 = A.INSERT[5][1] + 0.5


def noktalar(n, x, y, z_ust, aralik=3.0):
    """Ust yuzde n adet O1,6 x 0,6 cukur (sira etiketi), x'ten +X yonunde."""
    s = None
    for i in range(n):
        c = cyl(0.8, (x + i * aralik, y, z_ust - 0.6), (x + i * aralik, y, z_ust + 1))
        s = c if s is None else s.fuse(c)
    return s


# ---------------------------------------------------------------- Kupon A: 2 x 2 halka, kopruyle bagli
A_T = 7.0
R_DIS = 30.0
ADIM = 64.0
a = None
merkez = [(0, 0), (ADIM, 0), (0, ADIM), (ADIM, ADIM)]
for i, (x, y) in enumerate(merkez):
    h = cyl(R_DIS, (x, y, 0), (x, y, A_T))
    a = h if a is None else a.fuse(h)
a = a.fuse(box(0, ADIM, -6, 6, 0, A_T)).fuse(box(0, ADIM, ADIM - 6, ADIM + 6, 0, A_T)).fuse(box(-6, 6, 0, ADIM, 0, A_T))
for i, (x, y) in enumerate(merkez):
    a = a.cut(cyl(26.0 + 0.05 * i, (x, y, -1), (x, y, A_T + 1)))          # O52,0 + 0,1 * i
    a = a.cut(noktalar(i + 1, x - 4.0, y - 28.0, A_T, aralik=2.6))
kupon_a = a.removeSplitter()

# ---------------------------------------------------------------- Kupon B: serit (taban 5 mm) + mil borulari + somun bloklari
B_T = 5.0
Y1 = 12.5                                                                 # 1. sira ekseni: 625ZZ delikleri + M3 bloklari
b = box(0, 200, 0, 25, 0, B_T)
for i in range(4):                                                        # 625ZZ delikleri
    x = 15 + i * 24
    b = b.cut(cyl(8.0 + 0.05 * i, (x, Y1, -1), (x, Y1, B_T + 1)))       # O16,0 + 0,1 * i
    b = b.cut(noktalar(i + 1, x - 4.0, 2.0, B_T, aralik=2.6))
for i in range(4):                                                        # M3 somun bloklari 12 x 12 x 10
    x = 116 + i * 22
    b = b.fuse(box(x - 6, x + 6, Y1 - 6, Y1 + 6, 0, 10))
Y2 = 35.0                                                                 # 2. sira: M5 bloklari 16 x 16 x 11
b = b.fuse(box(100, 186, 25, 45, 0, B_T))
for i in range(3):
    x = 116 + i * 30
    b = b.fuse(box(x - 8, x + 8, Y2 - 8, Y2 + 8, 0, 11))
b = b.removeSplitter()
for i in range(4):
    x = 116 + i * 22
    b = b.cut(cyl(1.9 + 0.05 * i, (x, Y1, 10 - L_I3), (x, Y1, 11)))      # O3,8 + 0,1 * i
    b = b.cut(noktalar(i + 1, x - 4.0, 2.0, B_T, aralik=2.6))
for i in range(3):
    x = 116 + i * 30
    b = b.cut(cyl(3.1 + 0.1 * i, (x, Y2, 11 - L_I5), (x, Y2, 12)))       # O6,2 + 0,2 * i
    b = b.cut(noktalar(i + 1, x - 4.0, 25.8, B_T, aralik=2.6))
r_mil = [19.9, 19.95, 20.0, 20.05]                                        # 6808 ic bilezik mili: O39,8 / 39,9 / 40,0 / 40,1
Y3 = 70.0
m = box(0, 96, 24, 95, 0, 2.0).fuse(box(96, 200, 44, 95, 0, 2.0))       # boru tabani 2 mm (seride bitisik)
for i, r in enumerate(r_mil):
    x = 25 + i * 50
    m = m.fuse(cyl(r, (x, Y3, 0), (x, Y3, 2.0 + 8.0)).cut(cyl(r - 2.5, (x, Y3, 1.0), (x, Y3, 20))))
    m = m.cut(noktalar(i + 1, x - 4.0, Y3 - 22.0, 2.0, aralik=2.6))
kupon_b = b.fuse(m).removeSplitter()

os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
for ad, s in (("kupon-a-rulman-O52", kupon_a), ("kupon-b-yuva-mil-somun", kupon_b)):
    bb = s.BoundBox
    assert s.isValid() and len(s.Solids) == 1, ad
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.1).write(os.path.join(HERE, "stl", ad + ".stl"))
    print("%s: %.0f x %.0f x %.0f mm, %.1f cm3 (~%.0f g PETG %%100)" % (ad, bb.XLength, bb.YLength, bb.ZLength, s.Volume / 1000,
                                                                      s.Volume / 1000 * 1.27))
doc = App.newDocument("kupon")
for ad, s in (("KuponA", kupon_a), ("KuponB", kupon_b)):
    doc.addObject("Part::Feature", ad).Shape = s
Part.export(list(doc.Objects), os.path.join(HERE, "tolerans-kuponu.step"))
print("bitti")
