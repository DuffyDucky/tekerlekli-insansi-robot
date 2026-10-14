# Pi 5 kafa tablasina DOGRUDAN vidalanabilir mi? - GECICI olcum betigi (modul dosyalarina yazmaz).
# Calistir: FC_SCRIPT=<bu dosya> PYTHONDONTWRITEBYTECODE=1 freecadcmd C:\Users\Victus\.robot-cad\run_fc.py
# Kafa tablasi (Kafa iskeleti, y 178-183) uzerinde: 4 Pi deligi (58 x 49) tabla katisina >= R_ETLI mm icinde dusen konumlar
# (hafifletme cepleri ve kablo gecisi disarida), 4 yonelim (bilesen yukari), 1 mm adim; sonra kesin cakisma (Part common)
# ile Pi govdesi + S1 koruma hacimleri (fan ustu 10, kablo kenari 30, USB tarafi 20, SD 15) kafa parcalariyla cakisiyor mu.
# Cikti: pi_kafada_tabla_sonuc.json
import os, sys, math, json, time
import numpy as np
import FreeCAD as App
import Part

BU = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.dirname(os.path.dirname(BU))
FC = os.path.join(KOK, "tasarim", "freecad")
for _p in (os.path.join(FC, "kafa"), FC):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.dont_write_bytecode = True
t0 = time.time()


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


import kafa_parcalar as KP
V = App.Vector
KAF = [p for p in KP.P if p["grup"] == "Kafa" and p["tur"] != "Referans"]
ISK = next(p for p in KP.P if p["ad"] == "Kafa iskeleti")["shape"]
YT, ZT = KP.YT, KP.ZT
Y_MID = 180.5                     # tabla orta duzlemi (178-183)
R_ETLI = 3.5                      # M2,5 isil gomme somun O4 + 3 mm et -> delik merkezinden katiya >= 3,5 mm... (tahmini)
STAND = 6.0

# 1 mm izgarada tabla katisi
xs = np.arange(-105, 106, 1.0)
zs = np.arange(-60, 61, 1.0)
solid = np.zeros((len(xs), len(zs)), bool)
bb = ISK.BoundBox
for i, x in enumerate(xs):
    for j, z in enumerate(zs):
        if abs(x) <= 102.5 and -58 <= z <= 58:
            solid[i, j] = ISK.isInside(V(x, Y_MID, z), 1e-6, True)
log("tabla izgarasi", int(solid.sum()))


def erode(a, r):
    n = int(math.ceil(r))
    out = a.copy()
    for dx in range(-n, n + 1):
        for dz in range(-n, n + 1):
            if dx * dx + dz * dz <= r * r and (dx or dz):
                out &= np.roll(np.roll(a, dx, 0), dz, 1)
    return out


core = erode(solid, R_ETLI)
log("erode sonrasi (delik icin uygun) nokta", int(core.sum()))

DELIK = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
# 4 yonelim: yerel x, y -> kafa (X,Z) ; z -> +Y.  R = [[xx, yx, 0], [0,0,1], [xz, yz, 0]] sutunlar: yerel eksenlerin goruntusu
YON = {
    "R0 (kablo kenari +Z, on)": ((1, 0), (0, -1)),
    "R1 (kablo kenari +X, sag)": ((0, -1), (-1, 0)),
    "R2 (kablo kenari -Z, arka)": ((-1, 0), (0, 1)),
    "R3 (kablo kenari -X, sol)": ((0, 1), (1, 0)),
}
# tork modeli
ANA = json.load(open(os.path.join(FC, "kafa", "kafa-analiz.json"), encoding="utf-8"))
tk = ANA["tork"]["tilt"]
mK, cK, I_t, ALFA = tk["kutle_g"], np.array(tk["am"]), tk["I_kgm2"], tk["alfa_rad_s2"]
M_EK = 145.0
I_OWN = 0.145 * (0.085 ** 2 + 0.056 ** 2) / 12.0


def tork(c):
    M = mK + M_EK
    cc = (mK * cK + M_EK * np.array(c)) / M
    g = 0.0
    for th in range(-25, 31, 5):
        r = math.radians(th)
        g = max(g, abs(M * ((cc[1] - YT) * math.sin(r) + (cc[2] - ZT) * math.cos(r)) / 1e4))
    I = I_t + M_EK / 1000 * (((c[1] - YT) ** 2 + (c[2] - ZT) ** 2) / 1e6) + I_OWN
    return g + I * ALFA / 9.81 * 100


GOVDE = [
    ("PCB", 0, 85, 0, 56, 0, 1.3), ("alt pay", 0, 85, 0, 56, -1.5, 0), ("USB-C+HDMI", 6.5, 46, -1.7, 6.2, 1.3, 4.6),
    ("CSI", 47, 57, 0, 17, 1.3, 5.3), ("USB/Eth", 66.4, 88.1, 2.3, 54.2, -0.7, 17.5), ("GPIO", 7, 58, 50, 55.5, 1.3, 11.0),
    ("Cooler", 6, 69.5, 6.5, 49, 1.3, 15.0)]
KORUMA = [("fan 10", 6, 69.5, 6.5, 49, 15.0, 25.0), ("kablo 30", 6.5, 57, -30, 0, -1, 12), ("USB 20", 88.1, 108, 2.3, 54.2, -1, 17.5),
          ("SD 15", -15, 0, 18, 38, -3, 6)]


def sekil(parts, mat, t):
    m = App.Matrix(mat[0][0], mat[0][1], mat[0][2], t[0], mat[1][0], mat[1][1], mat[1][2], t[1], mat[2][0], mat[2][1], mat[2][2], t[2],
                   0, 0, 0, 1)
    bx = []
    for (_, x0, x1, y0, y1, z0, z1) in parts:
        b = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
        b.transformShape(m)
        bx.append(b)
    return bx[0].fuse(bx[1:])


SON = {}
for ad, (ex, ey) in YON.items():
    # kafa(X,Z) = cx + ex*(px) + ey*(py) ; tam: head = R.p + t, burada px,py kart koordinati (kose orijin)
    # R = kolonlar: yerel x -> (ex0,0,ex1), yerel y -> (ey0,0,ey1), yerel z -> (0,1,0)
    R = [[ex[0], ey[0], 0], [0, 0, 1], [ex[1], ey[1], 0]]
    adaylar = []
    # t = (tx, ty, tz): kose orijinin kafa konumu. Delikler = R.(hx,hy,0)+t -> core uzerinde
    for tx in np.arange(-130, 131, 1.0):
        for tz in np.arange(-110, 111, 1.0):
            ok = True
            for (hx, hy) in DELIK:
                X = tx + ex[0] * hx + ey[0] * hy
                Z = tz + ex[1] * hx + ey[1] * hy
                i, j = int(round(X - xs[0])), int(round(Z - zs[0]))
                if not (0 <= i < len(xs) and 0 <= j < len(zs)) or not core[i, j]:
                    ok = False
                    break
            if ok:
                adaylar.append((tx, tz))
    log(ad, "delikleri tabla katisinda olan konum sayisi", len(adaylar))
    # tork icin Pi kutle merkezi: kart merkezi (42.5, 28, 7)
    ty = 183.0 + STAND                                  # kart alt yuzu (PCB z=0) = tabla ust yuzu + burc
    siral = []
    for (tx, tz) in adaylar:
        c = (tx + ex[0] * 42.5 + ey[0] * 28.0, ty + 7.0, tz + ex[1] * 42.5 + ey[1] * 28.0)
        siral.append((tork(c), tx, tz, c))
    siral.sort()
    sonuc = []
    gecen, denen = 0, 0
    for (tk_, tx, tz, c) in siral[::max(1, len(siral) // 60)]:
        if gecen >= 4 or denen >= 40:
            break
        denen += 1
        body = sekil(GOVDE, R, (tx, ty, tz))
        kor = sekil(KORUMA, R, (tx, ty, tz))
        ovl, mind = [], 1e9
        for p in KAF:
            sh = p["shape"]
            b = App.BoundBox(body.BoundBox)
            b.enlarge(12)
            if not b.intersect(sh.BoundBox):
                continue
            v = body.common(sh).Volume if body.BoundBox.intersect(sh.BoundBox) else 0.0
            vk = kor.common(sh).Volume if kor.BoundBox.intersect(sh.BoundBox) else 0.0
            d = body.distToShape(sh)[0]
            mind = min(mind, d)
            if v > 0.5 or vk > 0.5:
                ovl.append((p["ad"], round(v, 1), round(vk, 1)))
        if not ovl:
            gecen += 1
        sonuc.append(dict(t=[tx, ty, tz], c=[round(v, 1) for v in c], tork=round(tk_, 3), cakisma=ovl, en_yakin=round(mind, 2)))
        log("  ", ad, "t", (tx, ty, tz), "tork %.2f" % tk_, "cakisma", ovl, "en yakin %.1f" % mind)
    SON[ad] = dict(n=len(adaylar),
                   xrange=[min(a[0] for a in adaylar), max(a[0] for a in adaylar)] if adaylar else None,
                   zrange=[min(a[1] for a in adaylar) , max(a[1] for a in adaylar)] if adaylar else None, ornek=sonuc)

json.dump(SON, open(os.path.join(BU, "pi_kafada_tabla_sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
log("bitti")
