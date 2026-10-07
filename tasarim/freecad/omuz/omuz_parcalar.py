# Sag omuz modulu (2 eksen) + ust kol baglantisi - PARCALAR, kutle ve kinematik (FreeCAD 1.1, Part)
# Import edilebilir: omuz_montaj.py (kontroller + kayit) ve ../carpisma.py (moduller arasi tarama) bunu kullanir.
# Koordinat: X disari, Y yukari, Z ileri; orijin = omuz traversi (sigma) merkezi = one-arka ekseni uzerinde.
# Global yerlesim ve arayuz olculeri (travers boyu, yuva bolgesi, dudak derinligi): ../arayuz.py
import os, sys, json, math, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from omuz_lib import *   # noqa
from arayuz import SG, TRAVERS_L, OMUZ_YUVA_X, LIP_ALTI_MERKEZ   # noqa

# arayuz: travers 200 mm, omuz yerel orijini = travers merkezi; yuva traversin x 70...103 ucuna gecer
YX0, YX1 = OMUZ_YUVA_X                      # 70, 103
T_UC = TRAVERS_L / 2                        # traversin ucu (100)
YUVA_IC = SG / 2 + 0.2                      # yuva ic yari olcusu: profil + 0.2 bosluk

t0 = time.time()
ROT_S1 = App.Rotation(V(0, 1, 0), 90)       # servo yerel +Z -> global +X
ROT_S2 = App.Rotation(V(0, 0, 1), 180)      # servo yerel -Y -> global +Y (govde yukari)
X_S1 = 144.7                                # S1 ust yuzu (mil tarafi)
XR = 185.0                                  # yana acma ekseni X
Z_S2 = 20.2                                 # S2 ust yuzu Z
ZC = -1.25                                  # kol catali / tup merkezi Z


def place(shape, base, rot):
    # transformShape(m, True): geometri kopyalanarak tasinir. Kopyasiz hali konumu yalniz Placement'a yaziyor,
    # Part::Feature'a atanip kaydedilince kayboluyordu (servolar dosyada orijinde kaldi).
    s = shape.copy()
    s.transformShape(App.Placement(V(*base), rot).toMatrix(), True)
    return s


def gpt(local, base, rot):
    return App.Placement(V(*base), rot).multVec(V(*local))


P = []   # parcalar


def add(ad, grup, shape, tur, malzeme, kod=None, renk="gri", patlat=(0, 0, 0), not_=""):
    P.append(dict(ad=ad, grup=grup, shape=shape, tur=tur, malzeme=malzeme, kod=kod or ad, renk=renk,
                  patlat=list(patlat), not_=not_))


# ====================================================================== SABIT (govde)
add("Omuz traversi (sigma 40x40 agir, 200 mm)", "Govde", sigma_x(-T_UC, T_UC), "Satin", "Aluminyum 6063",
    kod="Sigma 40x40 agir kanal 10, 200 mm", renk="alu")

# --- omuz yuvasi (PETG): traversin ucuna gecer, S1'i tasir, rulman kapagini tutar
yuva = box(YX0, YX1, -25, 25, -25, 25).cut(box(YX0 - 1, T_UC + 0.5, -YUVA_IC, YUVA_IC, -YUVA_IC, YUVA_IC))
yuva = yuva.fuse(box(YX1, 127, -25, 22, 20, 25)).fuse(box(YX1, 127, -25, 22, -25, -20))
yuva = yuva.fuse(box(127, 132, -42, 22, -25, 25)).fuse(box(127, 132, -12, 12, -38, 38))
yuva = yuva.fuse(box(132, 146, -12, 12, 26, 38)).fuse(box(132, 146, -12, 12, -38, -26))
yuva = yuva.cut(box(126, 133, -30.5, 10.5, -10.5, 10.5))
S1_HOLES = [(14.75, -5), (14.75, 5), (-34.75, -5), (-34.75, 5)]       # (y, z)
for (y, z) in S1_HOLES:
    yuva = yuva.cut(cyl(CLEAR[4] / 2, (126, y, z), (133, y, z)))
SLEEVE = [((86, 25, 0), (0, -1, 0), (0, 0, 1)), ((86, -25, 0), (0, 1, 0), (0, 0, 1)),
          ((86, 0, 25), (0, 0, -1), (0, 1, 0)), ((86, 0, -25), (0, 0, 1), (0, 1, 0))]   # (dis yuz noktasi, ice yon, cekic somun uzun yon)
for (p, d, ld) in SLEEVE:
    pv, dv = V(*p), V(*d)
    yuva = yuva.cut(Part.makeCylinder(CLEAR[6] / 2, 7, pv - dv, dv))
CAP_B = [(y, z) for y in (-6, 6) for z in (-33, 33)]   # z=32 iken civata basi halkaya 0.75 mm3 biniyordu
for (y, z) in CAP_B:
    yuva = yuva.cut(insert_hole(3, (146, y, z), (-1, 0, 0)))
add("Omuz yuvasi", "Govde", yuva.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(-60, 0, 0))

# --- S1 (one-arka servo) + kulak civatalari
body, dome, yc = servo_local()
add("S1 servo DS3218MG (one-arka)", "Govde", place(body, (X_S1, 0, 0), ROT_S1), "Satin", "-", kod="DS3218MG servo",
    renk="siyah", patlat=(40, 0, 0))
add("S1 servo cikis mili", "Govde", place(dome, (X_S1, 0, 0), ROT_S1), "Satin", "-", kod="(servo ile)", renk="siyah",
    patlat=(40, 0, 0))
for (y, z) in S1_HOLES:
    add("S1 kulak civatasi M4x16", "Govde", screw912(4, 16, (134.5, y, z), (-1, 0, 0)), "Baglanti", "Celik 8.8",
        kod="M4x16 DIN 912", renk="celik", patlat=(70, 0, 0))
    add("S1 kontra somun M4", "Govde", nut(4, (127, y, z), (-1, 0, 0), "985", (0, -1 if y > 0 else 1, 0)),
        "Baglanti", "Celik", kod="M4 DIN 985 kontra somun", renk="celik", patlat=(-30, 0, 0))

# --- yuva -> sigma: 4x M6x16 + pul + cekic somun
for (p, d, ld) in SLEEVE:
    pv, dv = V(*p), V(*d)
    add("Yuva baglanti pulu M6", "Govde", washer(6, pv, dv * -1), "Baglanti", "Celik", kod="M6 DIN 125 pul",
        renk="celik", patlat=tuple(dv * -25))
    add("Yuva baglanti civatasi M6x16", "Govde", screw912(6, 16, pv - dv * WASH125[6][2], dv), "Baglanti", "Celik 8.8",
        kod="M6x16 DIN 912", renk="celik", patlat=tuple(dv * -40))
    ptop = pv + dv * (25 - LIP_ALTI_MERKEZ)      # cekic somun ust yuzu dudak altinda
    add("Cekic somun M6 (kanal 10)", "Govde", hammer_nut(ptop, dv * -1, ld), "Baglanti", "Celik",
        kod="M6 cekic somun, kanal 10", renk="celik", patlat=tuple(dv * 10))

# --- rulman kapagi (PETG) + 6808 dis bilezik + 4x M3x12 + 4x M3 isil gomme
cap = cyl(30, (146, 0, 0), (160, 0, 0))
cap = cap.fuse(box(146, 152, -12, 12, 26, 38)).fuse(box(146, 152, -12, 12, -38, -26))
cap = cap.cut(cyl(24, (145, 0, 0), (153.01, 0, 0))).cut(cyl(26, (153, 0, 0), (161, 0, 0)))
for (y, z) in CAP_B:
    cap = cap.cut(cyl(CLEAR[3] / 2, (145, y, z), (153, y, z)))
add("Rulman kapagi", "Govde", cap.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(55, 0, 0))
b_in, b_out = bearing(40, 52, 7, (153, 0, 0), (1, 0, 0), 22.3, 24.4)
add("6808-2RS rulman (dis bilezik)", "Govde", b_out, "Satin", "Celik", kod="6808-2RS rulman 40x52x7", renk="celik",
    patlat=(75, 0, 0))
for (y, z) in CAP_B:
    add("Kapak civatasi M3x12", "Govde", screw912(3, 12, (152, y, z), (-1, 0, 0)), "Baglanti", "Celik 8.8",
        kod="M3x12 DIN 912", renk="celik", patlat=(90, 0, 0))
    add("Isil gomme somun M3 (yuvada)", "Govde", insert(3, (146, y, z), (-1, 0, 0)), "Baglanti", "Pirinc",
        kod="M3 isil gomme somun", renk="pirinc", patlat=(-8, 0, 0))

# --- V3 govde kabugunun yan yuzu (yaklasik referans: x=152 duz duvar, omuz icin O84 delik)
shell = box(147, 152, -300, 30, -102, 102).cut(cyl(42, (146, 0, 0), (153, 0, 0)))
add("Govde kabugu yan yuzu (referans)", "Govde", shell, "Referans", "PETG", renk="kabuk",
    not_="V3 kabugu x=152'de duz duvar varsayildi; gercek kabuk egri")

# ====================================================================== GOBEK (one-arka ile doner)
horn, hholes = horn_local()
add("S1 horn 25T aluminyum disk", "Gobek", place(horn, (X_S1, 0, 0), ROT_S1), "Satin", "Aluminyum",
    kod="25T aluminyum disk horn", renk="alu", patlat=(60, 0, 0))
add("S1 horn merkez vidasi M3", "Gobek", place(horn_center_screw_local(), (X_S1, 0, 0), ROT_S1), "Baglanti", "Celik",
    kod="M3x5 horn vidasi (servo ile)", renk="celik", patlat=(70, 0, 0))
add("6808-2RS rulman (ic bilezik)", "Gobek", b_in, "Satin", "Celik", kod="(6808 ile)", renk="celik", patlat=(75, 0, 0))

hub = cyl(20, (150, 0, 0), (160, 0, 0)).fuse(cyl(22.5, (160, 0, 0), (163, 0, 0)))
hub = hub.fuse(box(163, 168, -23, 42, -27, 23))
hub = hub.fuse(box(168, 199, -22, 42, 2.5, 7.5)).fuse(box(168, 199, -22, 42, -27, -21))
hub = hub.fuse(box(168, 199, 39, 43, -27, 7.5))
hub = hub.fuse(cyl(4, (XR, 0, -27), (XR, 0, -28)))
hub = hub.cut(cyl(4.5, (149, 0, 0), (153, 0, 0)))
S1_HORN = [gpt((x, y, 0), (X_S1, 0, 0), ROT_S1) for (x, y) in hholes]
for g in S1_HORN:
    hub = hub.cut(cyl(CLEAR[3] / 2, (149, g.y, g.z), (160, g.y, g.z))).cut(cyl(3.3, (159, g.y, g.z), (169, g.y, g.z)))
hub = hub.cut(box(174.5, 195.5, -10.5, 30.5, 2, 8))
S2_HOLES = [(XR - 5, -14.75), (XR + 5, -14.75), (XR - 5, 34.75), (XR + 5, 34.75)]   # (x, y)
for (x, y) in S2_HOLES:
    hub = hub.cut(cyl(CLEAR[4] / 2, (x, y, 2), (x, y, 8)))
hub = hub.cut(insert_hole(5, (XR, 0, -28), (0, 0, 1), extra=0.0))
add("Omuz gobegi", "Gobek", hub.removeSplitter(), "Baski", "PETG", renk="petg2", patlat=(110, 0, 0))
for g in S1_HORN:
    add("Gobek-horn civatasi M3x12", "Gobek", screw912(3, 12, (159, g.y, g.z), (-1, 0, 0)), "Baglanti", "Celik 8.8",
        kod="M3x12 DIN 912", renk="celik", patlat=(140, 0, 0))

body2, dome2, _ = servo_local()
add("S2 servo DS3218MG (yana acma)", "Gobek", place(body2, (XR, 0, Z_S2), ROT_S2), "Satin", "-", kod="DS3218MG servo",
    renk="siyah", patlat=(110, 0, 45))
add("S2 servo cikis mili", "Gobek", place(dome2, (XR, 0, Z_S2), ROT_S2), "Satin", "-", kod="(servo ile)", renk="siyah",
    patlat=(110, 0, 45))
for (x, y) in S2_HOLES:
    add("S2 kulak civatasi M4x16", "Gobek", screw912(4, 16, (x, y, 10), (0, 0, -1)), "Baglanti", "Celik 8.8",
        kod="M4x16 DIN 912", renk="celik", patlat=(110, 0, 75))
    add("S2 kontra somun M4", "Gobek", nut(4, (x, y, 2.5), (0, 0, -1), "985", (0, 1 if y < 0 else -1, 0)),
        "Baglanti", "Celik", kod="M4 DIN 985 kontra somun", renk="celik", patlat=(110, 0, -20))
add("Isil gomme somun M5 (gobekte)", "Gobek", insert(5, (XR, 0, -28), (0, 0, 1)), "Baglanti", "Pirinc",
    kod="M5 isil gomme somun", renk="pirinc", patlat=(110, 0, -15))
b5_in, b5_out = bearing(5, 16, 5, (XR, 0, -33), (0, 0, 1), 4.1, 6.4)
add("625ZZ rulman (ic bilezik)", "Gobek", b5_in, "Satin", "Celik", kod="625ZZ rulman 5x16x5", renk="celik",
    patlat=(110, -40, -45))
add("Mafsal pulu M5", "Gobek", washer(5, (XR, 0, -33), (0, 0, -1)), "Baglanti", "Celik", kod="M5 DIN 125 pul",
    renk="celik", patlat=(110, -40, -60))
add("Mafsal civatasi M5x12", "Gobek", screw912(5, 12, (XR, 0, -34), (0, 0, 1)), "Baglanti", "Celik 8.8",
    kod="M5x12 DIN 912", renk="celik", patlat=(110, -40, -75))

# ====================================================================== KOL (yana acma ile doner)
horn2, hholes2 = horn_local()
add("S2 horn 25T aluminyum disk", "Kol", place(horn2, (XR, 0, Z_S2), ROT_S2), "Satin", "Aluminyum",
    kod="25T aluminyum disk horn", renk="alu", patlat=(110, -40, 60))
add("S2 horn merkez vidasi M3", "Kol", place(horn_center_screw_local(), (XR, 0, Z_S2), ROT_S2), "Baglanti", "Celik",
    kod="M3x5 horn vidasi (servo ile)", renk="celik", patlat=(110, -40, 70))
S2_HORN = [gpt((x, y, 0), (XR, 0, Z_S2), ROT_S2) for (x, y) in hholes2]

fork = cyl(16, (XR, 0, 25.5), (XR, 0, 30.5)).fuse(box(XR - 16, XR + 16, -34, 0, 25.5, 30.5))
fork = fork.fuse(cyl(16, (XR, 0, -33), (XR, 0, -28))).fuse(box(XR - 16, XR + 16, -34, 0, -33, -28))
fork = fork.fuse(box(XR - 20, XR + 20, -34, -28, -33, 30.5))
fork = fork.fuse(cyl(28, (XR, -34, ZC), (XR, -40, ZC))).fuse(cyl(25.4, (XR, -40, ZC), (XR, -60, ZC)))
fork = fork.cut(cyl(4.5, (XR, 0, 25), (XR, 0, 31)))
for g in S2_HORN:
    fork = fork.cut(cyl(CLEAR[3] / 2, (g.x, g.y, 25), (g.x, g.y, 31)))
fork = fork.cut(cyl(8, (XR, 0, -33.01), (XR, 0, -27.99)))
TUBE_S = [((XR, -50, ZC + 25.4), (0, 0, -1)), ((XR, -50, ZC - 25.4), (0, 0, 1))]
for (p, d) in TUBE_S:
    fork = fork.cut(insert_hole(3, p, d))
add("Kol catali", "Kol", fork.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(110, -40, 0))
add("625ZZ rulman (dis bilezik)", "Kol", b5_out, "Satin", "Celik", kod="(625ZZ ile)", renk="celik",
    patlat=(110, -40, -45))
for g in S2_HORN:
    add("Catal-horn civatasi M3x8", "Kol", screw912(3, 8, (g.x, g.y, 30.5), (0, 0, -1)), "Baglanti", "Celik 8.8",
        kod="M3x8 DIN 912", renk="celik", patlat=(110, -40, 40))
tube = cyl(28, (XR, -40, ZC), (XR, -140, ZC)).cut(cyl(25.5, (XR, -39, ZC), (XR, -141, ZC)))
for (p, d) in TUBE_S:
    tube = tube.cut(cyl(CLEAR[3] / 2, (XR, -50, ZC - 30), (XR, -50, ZC + 30)))
add("Ust kol tupu", "Kol", tube.removeSplitter(), "Baski", "PETG", renk="petg2", patlat=(110, -120, 0))
for (p, d) in TUBE_S:
    pv, dv = V(*p), V(*d)
    add("Isil gomme somun M3 (catalda)", "Kol", insert(3, pv, dv), "Baglanti", "Pirinc", kod="M3 isil gomme somun",
        renk="pirinc", patlat=(110, -40, 0))
    head = pv - dv * (2.6 + 0.14)
    add("Tup civatasi M3x8", "Kol", screw912(3, 8, head, dv), "Baglanti", "Celik 8.8", kod="M3x8 DIN 912",
        renk="celik", patlat=tuple(V(110, -120, 0) - dv * 30))

# patlatilmis gorunum: her parca takildigi yonde, montaj sirasina gore acilir
PATLAT = {
    "Omuz yuvasi": (0, 0, 0), "S1 servo DS3218MG (one-arka)": (60, 0, 0), "S1 servo cikis mili": (60, 0, 0),
    "S1 kulak civatasi M4x16": (105, 0, 0), "S1 kontra somun M4": (-35, 0, 0),
    "S1 horn 25T aluminyum disk": (125, 0, 0), "S1 horn merkez vidasi M3": (140, 0, 0),
    "Rulman kapagi": (175, 0, 0), "Kapak civatasi M3x12": (205, 0, 0), "Isil gomme somun M3 (yuvada)": (-10, 0, 0),
    "6808-2RS rulman (dis bilezik)": (190, 0, 0), "6808-2RS rulman (ic bilezik)": (190, 0, 0),
    "Omuz gobegi": (235, 0, 0), "Gobek-horn civatasi M3x12": (275, 0, 0),
    "S2 servo DS3218MG (yana acma)": (235, 0, 70), "S2 servo cikis mili": (235, 0, 70),
    "S2 kulak civatasi M4x16": (235, 0, 110), "S2 kontra somun M4": (235, 0, -30),
    "Isil gomme somun M5 (gobekte)": (235, 0, -12),
    "Kol catali": (235, -70, 0), "S2 horn 25T aluminyum disk": (235, -70, 50), "S2 horn merkez vidasi M3": (235, -70, 62),
    "Catal-horn civatasi M3x8": (235, -70, 45),
    "625ZZ rulman (dis bilezik)": (235, -70, -45), "625ZZ rulman (ic bilezik)": (235, -70, -45),
    "Mafsal pulu M5": (235, -70, -62), "Mafsal civatasi M5x12": (235, -70, -80),
    "Isil gomme somun M3 (catalda)": (235, -70, 0), "Ust kol tupu": (235, -160, 0),
}
for p in P:
    if p["ad"] in PATLAT:
        p["patlat"] = list(PATLAT[p["ad"]])
    elif p["ad"] == "Tup civatasi M3x8":
        z = 1 if p["shape"].BoundBox.Center.z > ZC else -1
        p["patlat"] = [235, -160, 30 * z]

ALT_KOL = dict(m=260.0, p=(XR, -200.0, ZC), ad="Dirsek + on kol + el (eski modelden tahmini 260 g)")

# ====================================================================== kutle
RHO = {"PETG": 1.27 * 0.6, "Aluminyum": 2.70, "Aluminyum 6063": 2.70, "Celik": 7.85, "Celik 8.8": 7.85,
       "Pirinc": 8.50}
for p in P:
    p["hacim"] = p["shape"].Volume
    sol = p["shape"].Solids
    p["kati"] = len(sol)
    if sol:
        vt = sum(s.Volume for s in sol)
        c = V(0, 0, 0)
        for s in sol:
            c = c + s.CenterOfMass * (s.Volume / vt)
        p["merkez"] = c
    else:
        p["merkez"] = p["shape"].BoundBox.Center
    if p["kod"] == "DS3218MG servo":
        p["kutle"] = 60.0
    elif p["tur"] in ("Referans",) or p["kod"] == "(servo ile)":
        p["kutle"] = 0.0
    else:
        p["kutle"] = p["hacim"] / 1000.0 * RHO.get(p["malzeme"], 1.0)
    p["bb"] = p["shape"].BoundBox

# ====================================================================== pozlar
def Pp(phi):   # one kaldirma: +phi kolu one (+Z) kaldirir
    return App.Placement(V(0, 0, 0), App.Rotation(V(-1, 0, 0), phi), V(0, 0, 0))


def Pr(th):    # yana acma: +th kolu disari (+X) acar
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th), V(XR, 0, 0))


def pose_place(p, phi, th):
    if p["grup"] == "Govde":
        return App.Placement()
    if p["grup"] == "Gobek":
        return Pp(phi)
    return Pp(phi).multiply(Pr(th))



# hareket taramasi araliklari (omuz_montaj ve carpisma ayni araligi kullanir)
PHIS = list(range(-60, 181, 10))
THS = list(range(-20, 151, 5))
