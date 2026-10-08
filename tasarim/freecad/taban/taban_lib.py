# Taban modulu - parca kutuphanesi (FreeCAD 1.1, Part)
# Genel elemanlar ../ortak_lib.py'de; baski analizi ../dirsek/dirsek_lib.py'den (kabuk/kafa ile ayni yontem).
# Burada tabana ozgu: JGB37-520 motor + L braket + 12 mm altigen kaplin + 125 x 58 teker (rc:204-258), LiFePO4 aku (rc:339),
# kartlar (Pi 5 + Active Cooler, ESP32, PCA9685, BNO055, MAX98357A, BTS7960, XL4016; rc:302-337 + 04), HC-SR04 (rc:349),
# Emas acil stop (rc:357), tahmini zarflar (sigorta kutusu, role, ana anahtar, ana sigorta yuvasi), burclar, plaka yardimcilari,
# M2,5 / M4 / M5 / ISO 7380 M6 elemanlari ve DXF (R12) yazici. Yerel cizimler global eksenlerde, cagiran yerlestirir.
import os, sys, math
import FreeCAD as App
import Part

_HERE = os.path.dirname(os.path.abspath(__file__))
_UST = os.path.dirname(_HERE)
for _p in (_UST, os.path.join(_UST, "dirsek"), os.path.join(_UST, "kabuk")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from ortak_lib import *   # noqa
from dirsek_lib import baski_analiz   # noqa
import arayuz as A

# ------------------------------------------------------------------ ek standart elemanlar (ISO/DIN nominal)
DIN912_T = dict(A.DIN912)
DIN912_T[2.5] = (4.5, 2.5, 2.0)            # DIN 912 M2,5: dk, k, s
CLEAR_T = dict(A.CLEAR)
CLEAR_T[2.5] = 2.9
ISO7380_T = dict(A.ISO7380)
ISO7380_T[6] = (10.5, 3.3, 4.0)            # ISO 7380-1 M6: dk, k, s
WASH_T = dict(A.WASH125)


def vida912(d, L, p, direction):
    """DIN 912 (M2,5 dahil). p: bas alt yuzu merkezi, direction: govdenin gittigi yon."""
    dk, k, s = DIN912_T[d]
    u = unit(direction)
    p = V(*p)
    head = Part.makeCylinder(dk / 2, k, p - u * k, u)
    head = head.cut(hexprism(s, p - u * (k + 0.1), p - u * (k * 0.4)))
    return head.fuse(Part.makeCylinder(d / 2, L, p, u)).removeSplitter()


def vida7380(d, L, p, direction):
    dk, k, s = ISO7380_T[d]
    u = unit(direction)
    p = V(*p)
    head = Part.makeCylinder(dk / 2, k, p - u * k, u)
    head = head.cut(hexprism(s, p - u * (k + 0.1), p - u * (k * 0.35)))
    return head.fuse(Part.makeCylinder(d / 2, L, p, u)).removeSplitter()


def setvida(d, L, p, direction, s=None):
    """DIN 913 duz uclu set vida (saplama olarak). p: ust (anahtar) yuzu, direction: ilerleme yonu."""
    s = s or {3: 1.5, 4: 2.0, 5: 2.5, 6: 3.0}[d]
    u = unit(direction)
    p = V(*p)
    return Part.makeCylinder(d / 2, L, p, u).cut(hexprism(s, p - u * 0.1, p + u * (0.6 * d)))


def pul(d, p, direction):
    di, do, t = WASH_T[d]
    u = unit(direction)
    p = V(*p)
    return Part.makeCylinder(do / 2, t, p, u).cut(Part.makeCylinder(di / 2, t + 2, p - u, u))


def burc(af, L, p0, direction, d):
    """Altigen burc (disi-disi). p0: alt yuz merkezi, direction: eksen. Delik = nominal dis capi d (vida ile cakismaz)."""
    u = unit(direction)
    p0 = V(*p0)
    return hexprism(af, p0, p0 + u * L, V(1, 0, 0) if abs(u.x) < 0.9 else V(0, 0, 1)).cut(
        Part.makeCylinder(d / 2, L + 2, p0 - u, u))


def kutu_r(x0, x1, y0, y1, z0, z1, r, eksen="Y"):
    """Kenarlari eksene paralel kose yuvarlatmali kutu."""
    b = box(x0, x1, y0, y1, z0, z1)
    if r <= 0:
        return b
    ed = []
    for e in b.Edges:
        a, c = e.Vertexes[0].Point, e.Vertexes[1].Point
        d = c - a
        if (eksen == "Y" and abs(d.y) > 1e-6) or (eksen == "X" and abs(d.x) > 1e-6) or (eksen == "Z" and abs(d.z) > 1e-6):
            ed.append(e)
    return b.makeFillet(r, ed)


def plaka_xz(x0, x1, z0, z1, y0, t, koseler):
    """XZ duzleminde plaka, koseler: {(sx, sz): r} (sx, sz = -1/+1). r = 0 keskin."""
    b = box(x0, x1, y0, y0 + t, z0, z1)
    for (sx, sz), r in koseler.items():
        if r <= 0:
            continue
        cx = (x1 - r) if sx > 0 else (x0 + r)
        cz = (z1 - r) if sz > 0 else (z0 + r)
        kx = x1 if sx > 0 else x0
        kz = z1 if sz > 0 else z0
        kare = box(min(cx, kx), max(cx, kx), y0 - 1, y0 + t + 1, min(cz, kz), max(cz, kz))
        b = b.cut(kare.cut(Part.makeCylinder(r, t + 4, V(cx, y0 - 2, cz), V(0, 1, 0))))
    return b


def delik_y(x, z, d, y0, t):
    return Part.makeCylinder(d / 2, t + 2, V(x, y0 - 1, z), V(0, 1, 0))


def yarik_y(x0, x1, z0, z1, y0, t):
    """Yuvarlak uclu yarik (uzun kenari hangi eksendeyse o yonde)."""
    w = min(x1 - x0, z1 - z0)
    r = w / 2
    if (x1 - x0) >= (z1 - z0):
        s = box(x0 + r, x1 - r, y0 - 1, y0 + t + 1, z0, z1)
        for x in (x0 + r, x1 - r):
            s = s.fuse(Part.makeCylinder(r, t + 2, V(x, y0 - 1, (z0 + z1) / 2), V(0, 1, 0)))
    else:
        s = box(x0, x1, y0 - 1, y0 + t + 1, z0 + r, z1 - r)
        for z in (z0 + r, z1 - r):
            s = s.fuse(Part.makeCylinder(r, t + 2, V((x0 + x1) / 2, y0 - 1, z), V(0, 1, 0)))
    return s


def kesik_r(x0, x1, z0, z1, r, y0, t):
    return kutu_r(x0, x1, y0 - 1, y0 + t + 1, z0, z1, r, "Y")


# ------------------------------------------------------------------ JGB37-520 (rc:204-219, 04: O37 x 24 reduktor, O33 x 22 motor,
# enkoder ~O34 x 18, mil O6 D x 15, 7 mm kacik, on yuz 6x M3 O31 daire). Yerel: mil +X, orijin = reduktor on yuzu x 0, mil ekseni y=z=0.
JGB = dict(gb_d=37.0, gb_l=24.0, mot_d=33.0, mot_l=22.0, enc_d=34.0, enc_l=18.0, sh_d=6.0, sh_l=15.0, e=7.0, pcd=31.0,
           delik_derin=6.0, kutle_g=200.0)
JGB_DELIK_ACI = (30, 150, 210, 330)        # braketin kullandigi 4 delik (6 delikli daireden; tahmini, braket gelince)


def jgb_delikler():
    e = JGB["e"]
    return [(e + JGB["pcd"] / 2 * math.sin(math.radians(a)), JGB["pcd"] / 2 * math.cos(math.radians(a))) for a in (30, 90, 150, 210, 270, 330)]


def jgb37_local():
    e = JGB["e"]
    gb = Part.makeCylinder(JGB["gb_d"] / 2, JGB["gb_l"], V(-JGB["gb_l"], e, 0), V(1, 0, 0))
    for (y, z) in jgb_delikler():
        gb = gb.cut(Part.makeCylinder(1.5, JGB["delik_derin"] + 1, V(-JGB["delik_derin"], y, z), V(1, 0, 0)))
    x0 = -JGB["gb_l"] - JGB["mot_l"]
    can = Part.makeCylinder(JGB["mot_d"] / 2, JGB["mot_l"], V(x0, e, 0), V(1, 0, 0))
    enc = Part.makeCylinder(JGB["enc_d"] / 2, JGB["enc_l"], V(x0 - JGB["enc_l"], e, 0), V(1, 0, 0))
    conn = box(x0 - JGB["enc_l"] + 3, x0 - 3, e - 6, e + 6, -JGB["enc_d"] / 2 - 5, -JGB["enc_d"] / 2 + 1)
    boss = Part.makeCylinder(6.0, 2.0, V(0, 0, 0), V(1, 0, 0))
    sh = Part.makeCylinder(JGB["sh_d"] / 2, JGB["sh_l"], V(0, 0, 0), V(1, 0, 0)).cut(box(3, JGB["sh_l"] + 1, 2.5, 4, -4, 4))
    govde = gb.fuse([can, enc, conn, boss, sh]).removeSplitter()
    return govde


# 37 mm L braket (04: 46 x 42 x 40, sac 1,5, delik O3,5; JGB37 delik duzeni kontrol). Yerel: dikey plaka x 0...1,5 (motor on yuzune
# dayali), flans x -32...1,5 plakanin altinda (y BR_UP-1,5...BR_UP). Flans delikleri uzun rayin kanal hizasinda (x_ray - x_br).
BRK = dict(t=1.5, y0=-21.0, y1=A.BR_UP, z=21.0, flans=-32.0, orta_r=6.5, kutle_g=30.0)


def braket_local(dx_ray, dz):
    t = BRK["t"]
    v = box(0, t, BRK["y0"], BRK["y1"], -BRK["z"], BRK["z"]).cut(Part.makeCylinder(BRK["orta_r"], t + 2, V(-1, 0, 0), V(1, 0, 0)))
    for i, (y, z) in enumerate(jgb_delikler()):
        if (30, 90, 150, 210, 270, 330)[i] in JGB_DELIK_ACI:
            v = v.cut(Part.makeCylinder(1.75, t + 2, V(-1, y, z), V(1, 0, 0)))
    f = box(BRK["flans"], t, BRK["y1"] - t, BRK["y1"], -BRK["z"], BRK["z"])
    for s in (-1, 1):
        f = f.cut(Part.makeCylinder(A.CLEAR[4] / 2, t + 2, V(dx_ray, BRK["y1"] - t - 1, s * dz), V(0, 1, 0)))
    return v.fuse(f).removeSplitter()


# 12 mm altigen pirinc kaplin (04: 12 AA x 30, O6 delik, 35 g). Yerel: x 0...30, mil tarafi O6,1 x 14, teker tarafi M4 dis x 12 (tahmini).
KAP = dict(af=12.0, L=30.0, mil_derin=14.0, m4_derin=12.0, kutle_g=35.0)


def kaplin_local():
    h = hexprism(KAP["af"], V(0, 0, 0), V(KAP["L"], 0, 0), V(0, 1, 0))
    h = h.cut(Part.makeCylinder(3.05, KAP["mil_derin"] + 1, V(-1, 0, 0), V(1, 0, 0)))
    return h.cut(Part.makeCylinder(2.0, KAP["m4_derin"] + 1, V(KAP["L"] - KAP["m4_derin"], 0, 0), V(1, 0, 0)))


# 125 x 58 arazi tekeri (04 dogrulandi: O125 x 58, 12 mm altigen gobek, 140 g). Ic geometri tahmini: lastik (kenar r9) + jant +
# gobek manson; altigen yuva ic yuzden 17,5 derin, ortasinda 6 mm gobek gogsu (M4 vida O4,5). Yerel: merkez orijin, eksen X,
# ic yuz (robota bakan) x = -29.
TEK = dict(R=A.TEKER_D / 2, W=A.TEKER_W, jant_r=42.0, jant_ri=36.0, gobek_r=13.0, yuva_derin=17.5, gogus=6.0, kutle_g=140.0)


def teker_local():
    R, w = TEK["R"], TEK["W"]
    tire = Part.makeCylinder(R, w, V(-w / 2, 0, 0), V(1, 0, 0))
    ed = [e for e in tire.Edges if e.Curve.__class__.__name__ == "Circle" and abs(e.Curve.Radius - R) < 1e-6]
    tire = tire.makeFillet(9.0, ed)
    tire = tire.cut(Part.makeCylinder(TEK["jant_r"], w + 2, V(-w / 2 - 1, 0, 0), V(1, 0, 0)))
    rim = Part.makeCylinder(TEK["jant_r"], 50, V(-25, 0, 0), V(1, 0, 0)).cut(Part.makeCylinder(TEK["jant_ri"], 52, V(-26, 0, 0), V(1, 0, 0)))
    x0 = -w / 2 + TEK["yuva_derin"]           # gogus ic yuzu (-11,5)
    disk = Part.makeCylinder(TEK["jant_ri"] + 0.5, TEK["gogus"], V(x0, 0, 0), V(1, 0, 0))
    for i in range(6):
        a = math.radians(60 * i)
        disk = disk.cut(Part.makeCylinder(7.0, TEK["gogus"] + 2, V(x0 - 1, 24 * math.sin(a), 24 * math.cos(a)), V(1, 0, 0)))
    gobek = Part.makeCylinder(TEK["gobek_r"], TEK["yuva_derin"] + TEK["gogus"], V(-w / 2, 0, 0), V(1, 0, 0))
    jant = rim.fuse([disk, gobek])
    jant = jant.cut(hexprism(KAP["af"] + 0.1, V(-w / 2 - 1, 0, 0), V(x0, 0, 0), V(0, 1, 0)))
    jant = jant.cut(Part.makeCylinder(2.25, 20, V(x0 - 2, 0, 0), V(1, 0, 0))).removeSplitter()
    return tire.fuse(jant).removeSplitter()


# ------------------------------------------------------------------ LiFePO4 aku (rc:339-345, yatik: 181 x, 77 y, 167 z; kutuplar +Z
# yuzunde x +-65,5, y orta). Yerel: alt yuz merkezi orijin, kutup yuzu +Z.
AKU = A.TABAN["aku"]


def aku_local():
    l, w, h = AKU["olcu"]
    b = kutu_r(-l / 2, l / 2, 0, w, -h / 2, h / 2, 4.0, "Y")
    t1 = Part.makeCylinder(5.0, 9.0, V(-l / 2 + 25, w / 2, h / 2), V(0, 0, 1))
    t2 = Part.makeCylinder(5.0, 9.0, V(l / 2 - 25, w / 2, h / 2), V(0, 0, 1))
    return b.fuse([t1, t2]).removeSplitter()


# ------------------------------------------------------------------ kartlar (yerel: PCB alt yuzu y = 0, merkez x = z = 0)
def kart(l, w, t, comps=(), delikler=(), delik_d=3.0):
    b = box(-l / 2, l / 2, 0, t, -w / 2, w / 2)
    for (x, z) in delikler:
        b = b.cut(Part.makeCylinder(delik_d / 2, t + 2, V(x, -1, z), V(0, 1, 0)))
    parts = [box(x0, x1, y0, y1, z0, z1) for (x0, x1, y0, y1, z0, z1) in comps]
    return b.fuse(parts).removeSplitter() if parts else b


# Raspberry Pi 5 (mekanik cizim: 85 x 56, delik O2,7, 58 x 49, kenardan 3,5; Active Cooler 63,5 x 42,5 x 13,7). USB/Ethernet +X ucunda,
# SD yuvasi -X ucunda altta (kartin 2,5 mm disina tasar), GPIO +Z kenarinda, micro HDMI + USB-C -Z kenarinda (rc:308-332 dizilimi).
PI = dict(l=85.0, w=56.0, t=1.6, delik=2.7, kutle_g=46.0 + 12.0)
PI_DELIK = [(-PI["l"] / 2 + 3.5 + dx, -PI["w"] / 2 + 3.5 + dz) for dx in (0.0, 58.0) for dz in (0.0, 49.0)]


def pi5_local():
    l, w = PI["l"], PI["w"]
    comps = [(l / 2 - 17, l / 2 + 2, 1.6, 17.6, -w / 2 + 2, -w / 2 + 16), (l / 2 - 17, l / 2 + 2, 1.6, 17.6, -w / 2 + 20, -w / 2 + 34),
             (l / 2 - 21, l / 2 + 2, 1.6, 15.1, w / 2 - 18, w / 2 - 2),
             (-l / 2 + 6, -l / 2 + 6 + 63.5, 1.6, 1.6 + 13.7, -21.25, 21.25),        # Active Cooler (fan dahil 13,7)
             (-l / 2 + 7, -l / 2 + 58, 1.6, 10.1, w / 2 - 6, w / 2 - 1),           # GPIO
             (-l / 2 - 2.5, -l / 2 + 12, -1.4, 0.0, -6.0, 6.0),                    # microSD yuvasi + kart (altta, kenardan tasar)
             (-l / 2 + 20, -l / 2 + 58, 1.6, 4.6, -w / 2 - 1, -w / 2 + 6)]         # micro HDMI x2 + USB-C (tek blok)
    return kart(l, w, PI["t"], comps, PI_DELIK, PI["delik"])


PCA = dict(l=62.2, w=25.4, delik=2.5, dx=55.9, dz=19.05, kutle_g=9.0)       # 04 Adafruit 815
BNO = dict(l=27.0, w=20.0, delik=2.5, dx=20.0, dz=12.0, kutle_g=3.0)        # 04 Adafruit 2472 (eldeki muadil: olculecek)
AMP = dict(l=19.4, w=17.8, kutle_g=2.0)                                     # 04 Adafruit 3006 (montaj deligi yok)
ESP = dict(l=52.0, w=28.0, sira=25.4, kutle_g=10.0)                         # rc:34 DOIT 30 pin ~52 x 28 (orta guven)
PERF = dict(l=70.0, w=50.0, t=1.6, delik=3.0, kenar=2.5, kutle_g=14.0)      # delikli pertinaks 70 x 50 (tahmini; BOM'da yok)
BTS = dict(l=50.0, w=50.0, h=43.0, delik=3.0, dk=21.0, kutle_g=66.0)        # 04: 50 x 50 x 43, 4x M3 (aralik tahmini)
XL = dict(l=65.0, w=47.0, h=23.5, delik=3.0, dx=58.0, dz=26.0, kutle_g=60.0)   # 04: 65 x 47 x 23,5, delik 58 x 26
SONAR = dict(l=45.0, w=20.0, t=1.6, td=16.0, th=12.0, kutle_g=9.0)          # 04: 45 x 20 x 15, transduser O16 (pin blogu tahmini)


def pca_local():
    d = [(sx * PCA["dx"] / 2, sz * PCA["dz"] / 2) for sx in (-1, 1) for sz in (-1, 1)]
    return kart(PCA["l"], PCA["w"], 1.6, [(-24, 24, 1.6, 12.6, -12, -4), (-5, 5, 1.6, 10.6, 4, 12), (-3, 3, 1.6, 3.1, -2, 2)], d, PCA["delik"])


def bno_local():
    d = [(sx * BNO["dx"] / 2, sz * BNO["dz"] / 2) for sx in (-1, 1) for sz in (-1, 1)]
    return kart(BNO["l"], BNO["w"], 1.6, [(-4, 4, 1.6, 2.8, -4, 4)], d, BNO["delik"])


def amp_local():
    return kart(AMP["l"], AMP["w"], 1.6, [(-3, 3, 1.6, 2.6, -3, 3), (-8, 8, 1.6, 4.1, AMP["w"] / 2 - 4, AMP["w"] / 2 - 1)])


def esp_local():
    """ESP32 DevKit: PCB + WROOM kabi ustte, pin siralari altta (8,5 mm, disi header'a girer)."""
    l, w, s = ESP["l"], ESP["w"], ESP["sira"]
    comps = [(-l / 2 + 1, -l / 2 + 19, 1.6, 4.8, -8, 8), (l / 2 - 6, l / 2 + 1, 1.6, 4.6, -4, 4)]
    b = kart(l, w, 1.6, comps)
    for sz in (-1, 1):
        b = b.fuse(box(-18.9, 18.9, -6.0, 0.0, sz * s / 2 - 0.32, sz * s / 2 + 0.32))   # pin siralari (header'in icine 6 mm)
    return b.removeSplitter()


def perf_local():
    l, w, k = PERF["l"], PERF["w"], PERF["kenar"]
    d = [(sx * (l / 2 - k), sz * (w / 2 - k)) for sx in (-1, 1) for sz in (-1, 1)]
    b = kart(l, w, PERF["t"], (), d, PERF["delik"])
    for sz in (-1, 1):   # 15'li disi header x2 (2,54 adim), sira araligi ESP32'ye gore
        z = sz * ESP["sira"] / 2
        hd = box(-19.05, 19.05, PERF["t"], PERF["t"] + 8.5, z - 1.27, z + 1.27)
        hd = hd.cut(box(-19.0, 19.0, PERF["t"] + 2.5, PERF["t"] + 9.0, z - 0.33, z + 0.33))   # pin yuvasi
        b = b.fuse(hd)
    return b.removeSplitter()


def bts_local():
    d = [(sx * BTS["dk"], sz * BTS["dk"]) for sx in (-1, 1) for sz in (-1, 1)]
    comps = [(-17, 17, 1.6, BTS["h"], -17, 17), (-12, 12, 1.6, 11.6, 19, 25), (19.5, 24.5, 1.6, 10.6, -10, 10)]   # sogutucu, klemens, header
    return kart(BTS["l"], BTS["w"], 1.6, comps, d, BTS["delik"])


def xl_local():
    d = [(sx * XL["dx"] / 2, sz * XL["dz"] / 2) for sx in (-1, 1) for sz in (-1, 1)]
    comps = [(-26, -6, 1.6, XL["h"], -20, 20), (4, 20, 1.6, 15.6, 4, 20), (20, 25.5, 1.6, 11.6, -18, 8)]
    return kart(XL["l"], XL["w"], 1.6, comps, d, XL["delik"])


def sonar_local():
    """HC-SR04: yerel PCB arka yuzu z = 0, on yuzu z = 1,6, transduserler +Z; merkez x = y = 0. Pin blogu alt kenarda (asagi)."""
    l, w, t = SONAR["l"], SONAR["w"], SONAR["t"]
    b = box(-l / 2, l / 2, -w / 2, w / 2, 0, t)
    for dx in (-13.0, 13.0):
        b = b.fuse(Part.makeCylinder(SONAR["td"] / 2, SONAR["th"], V(dx, 0, t), V(0, 0, 1)))
    b = b.fuse(box(-5.08, 5.08, -w / 2 - 7.5, -w / 2, 0.2, 2.7))      # 4 pinli dik acili header (tahmini)
    return b.removeSplitter()


def acil_stop_local():
    """Emas B200E60 (rc:357-365; 04): panel ust yuzu y = 0. Mantar O60 (on 28), arka 48, arka govde 42 x 30. Iki kati:
    ust (mantar + bilezik) ve alt (boyun + kontak govdesi). Doner (ust, alt)."""
    cap = Part.makeCylinder(30.0, 12.0, V(0, 16, 0), V(0, 1, 0)).fuse(Part.makeCylinder(14.0, 10.5, V(0, 6, 0), V(0, 1, 0)))
    ust = cap.fuse(Part.makeCylinder(16.0, 6.0, V(0, 0, 0), V(0, 1, 0))).removeSplitter()
    alt = Part.makeCylinder(11.0, 12.0, V(0, -12, 0), V(0, 1, 0)).fuse(box(-21, 21, -48, -12, -15, 15)).removeSplitter()
    return ust, alt


def zarf(x0, x1, y0, y1, z0, z1, r=2.0):
    return kutu_r(x0, x1, y0, y1, z0, z1, r, "Y")


# ------------------------------------------------------------------ DXF (R12, ASCII) yazici: plakanin alt yuzu (y = y0) ust bakis
def dxf_yaz(shape, y0, path, katman="KESIM"):
    """Plakanin y = y0 duzlemindeki yuzunun kenarlari -> DXF. DXF X = robot x, DXF Y = -robot z (ustten bakis, robotun onu
    cizimin altinda). Duz kenar LINE, tam daire CIRCLE, yay ARC. Doner (cizgi, daire, yay) sayilari."""
    yuz = [f for f in shape.Faces if abs(f.BoundBox.YMin - y0) < 1e-6 and abs(f.BoundBox.YMax - y0) < 1e-6]
    if not yuz:
        raise ValueError("alt yuz bulunamadi")
    f = max(yuz, key=lambda q: q.Area)
    L = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"]
    n = [0, 0, 0]

    def P(v):
        return v.x, -v.z
    for e in f.Edges:
        c = e.Curve
        tn = c.__class__.__name__
        if tn in ("Line", "LineSegment"):
            a, b = P(e.Vertexes[0].Point), P(e.Vertexes[-1].Point)
            L += ["0", "LINE", "8", katman, "10", "%.4f" % a[0], "20", "%.4f" % a[1], "11", "%.4f" % b[0], "21", "%.4f" % b[1]]
            n[0] += 1
        elif tn == "Circle":
            cx, cy = P(c.Center)
            if e.isClosed():
                L += ["0", "CIRCLE", "8", katman, "10", "%.4f" % cx, "20", "%.4f" % cy, "40", "%.4f" % c.Radius]
                n[1] += 1
            else:
                ps = P(e.valueAt(e.FirstParameter))
                pe = P(e.valueAt(e.LastParameter))
                pm = P(e.valueAt(0.5 * (e.FirstParameter + e.LastParameter)))
                ang = lambda p: math.degrees(math.atan2(p[1] - cy, p[0] - cx)) % 360.0
                a0, a1, am = ang(ps), ang(pe), ang(pm)
                if (am - a0) % 360.0 > (a1 - a0) % 360.0:
                    a0, a1 = a1, a0
                L += ["0", "ARC", "8", katman, "10", "%.4f" % cx, "20", "%.4f" % cy, "40", "%.4f" % c.Radius, "50", "%.4f" % a0,
                      "51", "%.4f" % a1]
                n[2] += 1
        else:   # beklenmeyen egri: cokgen
            pts = [P(p) for p in e.discretize(Deflection=0.02)]
            for a, b in zip(pts[:-1], pts[1:]):
                L += ["0", "LINE", "8", katman, "10", "%.4f" % a[0], "20", "%.4f" % a[1], "11", "%.4f" % b[0], "21", "%.4f" % b[1]]
                n[0] += 1
    L += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", newline="\r\n") as fh:
        fh.write("\n".join(L) + "\n")
    return n, f.Area
