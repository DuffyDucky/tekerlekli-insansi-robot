# 40x40 agir sigma profil, kanal 10 - FreeCAD test parcasi
# Calistir: freecadcmd.exe sigma_profil.py
# Not: freecadcmd, yolunda "ü" (Masaüstü) olan betik verilince cokuyor; ASCII yoldaki bir baslaticidan exec ile calistir.
# Olculer: tasarim/cad/robot_cad.py ile ayni (04-parca-olculeri.md, Robolink cizimi + sigmaprofil.com.tr):
# kanal 10.2, dudak 4.3, merkez O9, kose delik O5.1 @ 30.2, 1.99 kg/m, kesit 7.32 cm2.
# Kanal ici bosluk: dudak altinda 20 genislik, CAV_DIK kadar dik iner, 45 derece egimle CAV_TAB genislige daralir.
# Egimli bolum gobegi koselere baglayan capraz duvarlari birakir (dikdortgen bosluk gobegi koparirdi).
# CAV_DIK / CAV_TAB uretici ciziminden olculmedi; kesit alani ureticinin 7.32 cm2 degerine gore ayarlandi.
import os
import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))

SG = 40.0         # dis olcu
R_DIS = 1.5       # dis kose radyusu
SLOT = 10.2       # kanal agzi
LIP = 4.3         # dudak kalinligi
CAV_W = 20.0      # kanal ic genisligi
CAV_D = 7.5       # kanal ic derinligi (dudak altindan)
CAV_TAB = 13.0    # kanal tabani genisligi (tahmini)
CAV_DIK = CAV_D - (CAV_W - CAV_TAB) / 2  # dik bolum, kalan derinlik 45 derece egim
BORE = 9.0        # merkez delik
KOSE_D = 5.1      # kose delikleri
KOSE_A = 30.2     # kose delik araligi
KG_M = 1.99       # ureticinin kg/m degeri
UZUNLUK = 500.0   # test boyu (FreeCAD'de Extrude > Length ile degisir)


def kesit():
    h = SG / 2
    # Kose radyusu: (SG - 2R) karenin R kadar yuvarlak ofseti
    i = h - R_DIS
    kare = Part.Face(Part.makePolygon([V(-i, -i, 0), V(i, -i, 0), V(i, i, 0), V(-i, i, 0), V(-i, -i, 0)])).makeOffset2D(R_DIS)
    s = kare.removeSplitter()
    for aci in (0, 90, 180, 270):
        agiz = Part.makePlane(SLOT, LIP + 1, V(-SLOT / 2, h - LIP, 0))
        y0 = h - LIP
        ic = Part.Face(Part.makePolygon([
            V(-CAV_W / 2, y0, 0), V(CAV_W / 2, y0, 0), V(CAV_W / 2, y0 - CAV_DIK, 0),
            V(CAV_TAB / 2, y0 - CAV_D, 0), V(-CAV_TAB / 2, y0 - CAV_D, 0),
            V(-CAV_W / 2, y0 - CAV_DIK, 0), V(-CAV_W / 2, y0, 0)]))
        kanal = agiz.fuse(ic)
        kanal.rotate(V(0, 0, 0), V(0, 0, 1), aci)
        s = s.cut(kanal)
    s = s.cut(Part.Face(Part.Wire(Part.makeCircle(BORE / 2, V(0, 0, 0)))))
    k = KOSE_A / 2
    for (cx, cy) in ((k, k), (-k, k), (k, -k), (-k, -k)):
        s = s.cut(Part.Face(Part.Wire(Part.makeCircle(KOSE_D / 2, V(cx, cy, 0)))))
    return s.removeSplitter()


doc = App.newDocument("SigmaTest")
f = doc.addObject("Part::Feature", "Kesit_40x40")
f.Shape = kesit()
ext = doc.addObject("Part::Extrusion", "Sigma_40x40_Agir")
ext.Base = f
ext.DirMode = "Custom"
ext.Dir = V(0, 0, 1)
ext.LengthFwd = UZUNLUK
ext.Solid = True
doc.recompute()

alan = f.Shape.Area
hacim = ext.Shape.Volume
kutle = hacim * 2.70e-3  # 6063 aluminyum 2.70 g/cm3
print("Kesit alani: %.1f mm2 (uretici 732 mm2, fark %%%.1f)" % (alan, (alan - 732) / 732 * 100))
print("Kati sayisi: %s, gecerli: %s" % (len(ext.Shape.Solids), ext.Shape.isValid()))
print("Boy %.0f mm -> %.0f g (uretici kg/m ile %.0f g)" % (UZUNLUK, kutle, KG_M * UZUNLUK))
bb = ext.Shape.BoundBox
print("Sinir kutusu: %.1f x %.1f x %.1f mm" % (bb.XLength, bb.YLength, bb.ZLength))

doc.saveAs(os.path.join(HERE, "sigma-test.FCStd"))
ext.Shape.exportStep(os.path.join(HERE, "sigma-test.step"))
print("Kaydedildi:", HERE)
