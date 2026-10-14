# Pi 5 kafada mi? - GECICI olcum betigi (modul dosyalarina yazmaz; yalniz kafa_parcalar'i import eder).
# Calistir: FC_SCRIPT=<bu dosya> PYTHONDONTWRITEBYTECODE=1 freecadcmd C:\Users\Victus\.robot-cad\run_fc.py
# Cikti: pi_kafada_sonuc.json (bu klasorde) + konsol.
#  1) kafa ici bos hacim: kabuk ici (KP.ic) + tum kafa parcalari + tilt taramasinda Pan/Govde parcalari, 2,5 mm voxel
#  2) Pi 5 + Active Cooler + konnektor/kablo/fan/SD koruma hacimleri, 24 yonelim, FFT korelasyonla tum konumlar
#  3) en iyi adaylar icin kesin dogrulama (Part common / distToShape), tilt taramasi (-25..30)
#  4) tork: kafa-analiz.json'daki kutle/AM/atalet + eklenen kutle (tilt ve pan), kafa_montaj.py formulleriyle
import os, sys, math, json, time, itertools
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
log("kafa_parcalar yuklendi, parca", len(KP.P))

KAF = [p for p in KP.P if p["grup"] == "Kafa" and p["tur"] != "Referans"]
PAN = [p for p in KP.P if p["grup"] == "Pan"]
GOV = [p for p in KP.P if p["grup"] == "Govde"]
ISK = next(p for p in KP.P if p["ad"] == "Kafa iskeleti")
ONK = next(p for p in KP.P if p["ad"].startswith("Yuz kabugu"))
ARK = next(p for p in KP.P if p["ad"].startswith("Arka kafa"))
YT, ZT = KP.YT, KP.ZT
SONUC = {}

# ---------------------------------------------------------------- 0) iç hacim ve serbest derinlik (kesin, ray)
def z_aralik(x, y, parcalar):
    """(x,y) dogrusu boyunca parcalarin kapladigi z araliklari (birlestirilmis)."""
    ln = Part.makeLine(V(x, y, -200), V(x, y, 200))
    iv = []
    for p in parcalar:
        sh = p["shape"]
        bb = sh.BoundBox
        if not (bb.XMin - 1e-6 <= x <= bb.XMax + 1e-6 and bb.YMin - 1e-6 <= y <= bb.YMax + 1e-6):
            continue
        try:
            c = sh.common(ln)
        except Exception:
            continue
        for e in c.Edges:
            iv.append((round(e.BoundBox.ZMin, 2), round(e.BoundBox.ZMax, 2), p["ad"]))
    iv.sort()
    return iv


rays = {}
for (x, y) in [(0, 200), (0, 230), (0, 260), (-50, 215), (50, 215), (90, 215), (-90, 215), (0, 120), (60, 150), (-60, 150), (80, 130)]:
    iv = z_aralik(x, y, KAF)
    rays["%g,%g" % (x, y)] = iv
    log("ray", x, y, [(a, b, n[:18]) for a, b, n in iv])
SONUC["ray"] = rays

# ---------------------------------------------------------------- 1) voxel doluluk
H = 2.5
X0, X1, Y0, Y1, Z0, Z1 = -115.0, 115.0, 85.0, 285.0, -75.0, 97.5
nx, ny, nz = int(round((X1 - X0) / H)), int(round((Y1 - Y0) / H)), int(round((Z1 - Z0) / H))
xs = X0 + (np.arange(nx) + 0.5) * H
ys = Y0 + (np.arange(ny) + 0.5) * H
zs = Z0 + (np.arange(nz) + 0.5) * H
log("grid", nx, ny, nz)
XX, YY, ZZ = np.meshgrid(xs, ys, zs, indexing="ij")


def ic_icinde():
    """kabuk ici (ic bos hacim), analitik: XY'de R25,5 yuvarlak dikdortgen (Z'ye paralel kenarlar) + on/arka yuz kenarlari R9,5.
    Kesin ic (KP.ic) ile 600 rastgele noktada karsilastirilir (uyumsuzluk orani raporlanir)."""
    ax, ay0, ay1, az0, az1 = 102.5, 97.5, 272.5, -62.5, 82.5
    R, rf = 25.5, 9.5
    cx, cy0, cy1 = ax - R, ay0 + R, ay1 - R
    dx = np.maximum(np.abs(XX) - cx, 0.0)
    dy = np.where(YY < cy0, cy0 - YY, np.where(YY > cy1, YY - cy1, 0.0))
    # XY'de ic yuzeye dik mesafe (icerde pozitif): yuvarlak dikdortgen
    sd = np.minimum(ax - np.abs(XX), np.minimum(YY - ay0, ay1 - YY))                 # duz kenarlara uzaklik
    kose = (np.abs(XX) > cx) & ((YY < cy0) | (YY > cy1))
    sd = np.where(kose, R - np.hypot(dx, dy), sd)
    dz = np.minimum(ZZ - az0, az1 - ZZ)                                                  # on/arka yuzlere uzaklik
    gerek = np.where(dz < rf, rf - np.sqrt(np.maximum(rf * rf - (rf - dz) ** 2, 0.0)), 0.0)
    return (sd >= gerek) & (dz > 0)


def parca_dolu(sh, ek_mask=None, pad=0.0):
    bb = sh.BoundBox
    m = (XX >= bb.XMin - pad) & (XX <= bb.XMax + pad) & (YY >= bb.YMin - pad) & (YY <= bb.YMax + pad) & (ZZ >= bb.ZMin - pad) & (ZZ <= bb.ZMax + pad)
    if ek_mask is not None:
        m &= ek_mask
    out = np.zeros(XX.shape, bool)
    for (i, j, k) in np.argwhere(m):
        if sh.isInside(V(XX[i, j, k], YY[i, j, k], ZZ[i, j, k]), 1e-6, True):
            out[i, j, k] = True
    return out


CACHE = os.path.join(os.environ.get("TEMP", "."), "pi_kafada_voxel.npz")
if os.path.exists(CACHE):
    _z = np.load(CACHE)
    ic_bos, tabla, diger, onozel, arkaozel, pan_dolu = [_z[k] for k in ("ic_bos", "tabla", "diger", "onozel", "arkaozel", "pan_dolu")]
    duvar = ~ic_bos
    log("voxel onbellekten yuklendi", CACHE)
else:
    ic_bos = ic_icinde()
    import random
    random.seed(1)
    _uyum = 0
    _n = 600
    for _ in range(_n):
        q = V(random.uniform(-110, 110), random.uniform(90, 280), random.uniform(-70, 90))
        a = KP.ic.isInside(q, 1e-6, True)
        i_ = int((q.x - X0) // H); j_ = int((q.y - Y0) // H); k_ = int((q.z - Z0) // H)
        if a != bool(ic_bos[i_, j_, k_]):
            _uyum += 1
    SONUC["ic_analitik_uyumsuz_oran"] = _uyum / _n
    log("analitik ic uyumsuz oran", _uyum / _n)
    log("ic bos voxel", int(ic_bos.sum()), "hacim cm3 %.0f" % (ic_bos.sum() * H ** 3 / 1000))
    duvar = ~ic_bos                                       # kabuk duvari + dis
    ic_mask = ic_bos
    tabla = parca_dolu(ISK["shape"], ic_mask)             # kafa iskeleti (tabla, yanaklar, bosslar)
    log("tabla voxel", int(tabla.sum()))
    # diger kafa parcalari (kabuklar haric): LCD, vizor, kamera, rulman/horn/civata ... (ic bosluktaki)
    diger = np.zeros(XX.shape, bool)
    for p in KAF:
        if p is ISK or p is ARK or p is ONK:
            continue
        if p["ad"].startswith("Vizor"):
            continue
        diger |= parca_dolu(p["shape"], ic_mask)
    log("diger kafa parca voxel", int(diger.sum()))
    # on kabugun ic ozellikleri (LCD cercevesi, bosslar, kamera bossu): yalniz z > 74
    onozel = parca_dolu(ONK["shape"], ic_mask & (ZZ > 74.0))
    # arka kabuk dil / civata bosslari (z 29..37)
    arkaozel = parca_dolu(ARK["shape"], ic_mask & (ZZ > 28.0) & (ZZ < 38.0))
    log("kabuk ozel voxel", int(onozel.sum()), int(arkaozel.sum()))

    # Pan/Govde parcalari: tilt taramasinda kafa gozunden dolu (kafa cercevesine -th ile tasinmis)
    alt = ic_bos & (YY < 182.0)
    pan_dolu = np.zeros(XX.shape, bool)
    alt_idx = np.argwhere(alt)
    P3 = np.stack([XX[alt], YY[alt], ZZ[alt]], axis=1)
    for th in range(-25, 31, 5):
        # kafa th kadar doner: kafa cercevesindeki nokta dunyada Ptilt(th) ile; Pan/Govde parcalari dunyada sabit
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        yy = YT + (P3[:, 1] - YT) * c - (P3[:, 2] - ZT) * s_
        zz = ZT + (P3[:, 1] - YT) * s_ + (P3[:, 2] - ZT) * c
        W = np.stack([P3[:, 0], yy, zz], axis=1)
        for p in PAN + GOV:
            sh = p["shape"]
            bb = sh.BoundBox
            m = (W[:, 0] >= bb.XMin) & (W[:, 0] <= bb.XMax) & (W[:, 1] >= bb.YMin) & (W[:, 1] <= bb.YMax) & (W[:, 2] >= bb.ZMin) & (W[:, 2] <= bb.ZMax)
            for q in np.nonzero(m)[0]:
                if sh.isInside(V(*W[q]), 1e-6, True):
                    i, j, k = alt_idx[q]
                    pan_dolu[i, j, k] = True
        log("tilt", th, "pan voxel", int(pan_dolu.sum()))


    np.savez_compressed(CACHE, ic_bos=ic_bos, tabla=tabla, diger=diger, onozel=onozel, arkaozel=arkaozel, pan_dolu=pan_dolu)
    log("voxel onbellege yazildi")

dolu0 = duvar | tabla | diger | onozel | arkaozel | pan_dolu            # dilatasyonsuz


def genislet(a, r=1):
    o = a.copy()
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx or dy or dz:
                    o |= np.roll(np.roll(np.roll(a, dx, 0), dy, 1), dz, 2)
    return o


dolu1 = genislet(dolu0, 1)                                                    # >= 2,5 mm pay
# sinir: domain disina tasan konumlar gecersiz (korelasyon s araligi), duvar zaten dolu
bos_h = (~dolu0).sum() * H ** 3 / 1000
SONUC["ic_bos_hacim_cm3"] = round(float(ic_bos.sum() * H ** 3 / 1000), 1)
bosic = ic_bos & ~(tabla | diger | onozel | arkaozel | pan_dolu)
SONUC["bos_ic_cm3_ustu"] = round(float((bosic & (YY > 183.0)).sum() * H ** 3 / 1000), 1)
SONUC["bos_ic_cm3_alt"] = round(float((bosic & (YY <= 183.0)).sum() * H ** 3 / 1000), 1)
log("bos ic: ust %.0f cm3, alt %.0f cm3" % (SONUC["bos_ic_cm3_ustu"], SONUC["bos_ic_cm3_alt"]))

# ---------------------------------------------------------------- 2) Pi 5 modeli (STEP'ten alinan siniflar, 04-parca-olculeri + datasheet)
# yerel: kart kosesi orijin, x 85, y 56, z yukari (bilesen tarafi). Kutular (ad,x0,x1,y0,y1,z0,z1)
GOVDE = [
    ("PCB", 0, 85, 0, 56, 0, 1.3),
    ("alt pay (SD yuvasi 1,45)", 0, 85, 0, 56, -1.5, 0),
    ("USB-C + 2 micro-HDMI (y=0 kenari)", 6.5, 46, -1.7, 6.2, 1.3, 4.6),
    ("CSI/DSI x2", 47, 57, 0, 17, 1.3, 5.3),
    ("USB x4 + Ethernet", 66.4, 88.1, 2.3, 54.2, -0.7, 17.5),
    ("GPIO basligi", 7, 58, 50, 55.5, 1.3, 11.0),
    ("Active Cooler 63,5x42,5x13,7", 6, 69.5, 6.5, 49, 1.3, 15.0),
]
SENARYO = {
    # tam koruma: fan ustu 10, kablo kenari 30, USB fis tarafi 20, SD erisimi 15
    "S1_tam": [
        ("fan hava girisi 10 mm", 6, 69.5, 6.5, 49, 15.0, 25.0),
        ("kablo kenari 30 mm", 6.5, 57, -30, 0, -1, 12),
        ("USB fis tarafi 20 mm", 88.1, 108, 2.3, 54.2, -1, 17.5),
        ("microSD erisimi 15 mm", -15, 0, 18, 38, -3, 6),
    ],
    # kompakt: acili fis / kisa adaptor: fan ustu 8, kablo kenari 22, USB tarafi 8, SD 8
    "S2_kompakt": [
        ("fan hava girisi 8 mm", 6, 69.5, 6.5, 49, 15.0, 23.0),
        ("kablo kenari 22 mm", 6.5, 57, -22, 0, -1, 10),
        ("USB tarafi 8 mm", 88.1, 96, 2.3, 54.2, -1, 17.5),
        ("microSD erisimi 8 mm", -8, 0, 18, 38, -3, 6),
    ],
}
DELIK = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]               # 58 x 49 aralik, kenardan 3,5 (datasheet)
STAND = 6.25                                                                # M2,5 burc ~6 mm (voxel merkezi)

allb = GOVDE + sum(SENARYO.values(), [])
lo = [math.floor(min(b[1 + 2 * a] for b in allb) / H) * H for a in range(3)]
hi = [math.ceil(max(b[2 + 2 * a] for b in allb) / H) * H for a in range(3)]
lo[2] = min(lo[2], -STAND - H)
na = [int(round((hi[a] - lo[a]) / H)) for a in range(3)]
lx = lo[0] + (np.arange(na[0]) + 0.5) * H
ly = lo[1] + (np.arange(na[1]) + 0.5) * H
lz = lo[2] + (np.arange(na[2]) + 0.5) * H
LX, LY, LZ = np.meshgrid(lx, ly, lz, indexing="ij")


def kutu_dizi(liste):
    a = np.zeros(LX.shape, bool)
    for (_, x0, x1, y0, y1, z0, z1) in liste:
        a |= (LX > x0) & (LX < x1) & (LY > y0) & (LY < y1) & (LZ > z0) & (LZ < z1)
    return a


A_g = kutu_dizi(GOVDE)
S_dz = np.zeros(LX.shape, np.float64)
for (hx, hy) in DELIK:
    S_dz[int((hx - lo[0]) // H), int((hy - lo[1]) // H), int((-STAND - lo[2]) // H)] = 1.0
log("Pi dizisi", na, "govde voxel", int(A_g.sum()))


def donusumler():
    out = []
    for perm in itertools.permutations(range(3)):
        for sg in itertools.product((1, -1), repeat=3):
            R = np.zeros((3, 3), int)
            for j in range(3):
                R[perm[j], j] = sg[j]
            if round(np.linalg.det(R)) == 1:
                out.append((perm, sg, R))
    return out


def don_dizi(A, perm, sg):
    axes = [0, 0, 0]
    for j in range(3):
        axes[perm[j]] = j
    B = np.transpose(A, axes)
    for j in range(3):
        if sg[j] < 0:
            B = np.flip(B, axis=perm[j])
    return np.ascontiguousarray(B)


def lo_donus(perm, sg):
    lop = [0.0] * 3
    for j in range(3):
        lop[perm[j]] = lo[j] if sg[j] > 0 else -(lo[j] + na[j] * H)
    return np.array(lop)


O1 = dolu1.astype(np.float64)
N = (nx, ny, nz)
FO1 = np.fft.rfftn(O1)
FT0 = np.fft.rfftn(tabla.astype(np.float64))
FW0 = np.fft.rfftn(duvar.astype(np.float64))


def korel(F, B):
    return np.fft.irfftn(F * np.conj(np.fft.rfftn(B, s=N)), s=N)


# tork modeli (kafa_montaj.py ile ayni formuller)
ANA = json.load(open(os.path.join(FC, "kafa", "kafa-analiz.json"), encoding="utf-8"))
tk = ANA["tork"]["tilt"]
mK, cK, I_t = tk["kutle_g"], np.array(tk["am"]), tk["I_kgm2"]
ALFA = tk["alfa_rad_s2"]
STALL = 9.4
THS = list(range(-25, 31, 5))
M_EK = 145.0                                         # g (120-170 araligin ortasi)
I_OWN = 0.145 * (0.085 ** 2 + 0.056 ** 2) / 12.0     # kutu kendi ataleti (kaba ust sinir)


def tilt_tork_vec(m_ek, c, own=True):
    """c: (n,3) kafa cercevesinde nokta kutle konumlari. Doner (yercekimi, ivme, toplam, I)."""
    c = np.atleast_2d(c)
    M = mK + m_ek
    cc = (mK * cK[None, :] + m_ek * c) / M
    g = np.zeros(len(c))
    for th in THS:
        r = math.radians(th)
        zr = (cc[:, 1] - YT) * math.sin(r) + (cc[:, 2] - ZT) * math.cos(r)
        g = np.maximum(g, np.abs(M * zr / 1e4))
    I = I_t + (m_ek / 1000.0) * (((c[:, 1] - YT) ** 2 + (c[:, 2] - ZT) ** 2) / 1e6) + (I_OWN if own and m_ek > 0 else 0.0)
    ti = I * ALFA / 9.81 * 100
    return g, ti, g + ti, I


g0, ti0, tot0, _ = tilt_tork_vec(0.0, np.array([[0.0, 0.0, 0.0]]))
SONUC["tilt_mevcut_kontrol"] = dict(gravity=float(g0[0]), ivme=float(ti0[0]), toplam=float(tot0[0]))
log("kontrol: mevcut tilt yercekimi %.3f ivme %.3f toplam %.3f (kafa-analiz: 2.58/1.876/4.46)" % (g0[0], ti0[0], tot0[0]))

sonuclar = {}
for sen, KOR in SENARYO.items():
    A_all = (A_g | kutu_dizi(KOR)).astype(np.float64)
    for (perm, sg, R) in donusumler():
        B_all = don_dizi(A_all, perm, sg)
        B_s = don_dizi(S_dz, perm, sg)
        ax = B_all.shape
        lop = lo_donus(perm, sg)
        ok = korel(FO1, B_all) < 0.5
        msk = np.zeros(N, bool)
        msk[:N[0] - ax[0] + 1, :N[1] - ax[1] + 1, :N[2] - ax[2] + 1] = True
        ok &= msk
        sup_t = korel(FT0, B_s) > 3.5
        sup_w = korel(FW0, B_s) > 3.5
        for dm, destek in (("herhangi", np.ones(N, bool)), ("tabla", sup_t), ("duvar", sup_w)):
            a = ok & destek
            n = int(a.sum())
            if n == 0:
                continue
            idx = np.argwhere(a)
            pc = np.array([42.5, 28.0, 7.0])
            t = np.stack([X0 + idx[:, 0] * H, Y0 + idx[:, 1] * H, Z0 + idx[:, 2] * H], axis=1) - lop[None, :]
            c = (R.dot(pc))[None, :] + t
            g, ti, tot, I = tilt_tork_vec(M_EK, c)
            o = np.argsort(tot)[:3]
            kayit = dict(sen=sen, destek=dm, R=R.tolist(), perm=list(perm), sg=list(sg), n=n,
                         cmin=[round(float(v), 1) for v in c.min(0)], cmax=[round(float(v), 1) for v in c.max(0)],
                         en_iyi=[dict(tork=round(float(tot[q]), 3), grav=round(float(g[q]), 3), ivme=round(float(ti[q]), 3),
                                      c=[round(float(v), 1) for v in c[q]], idx=[int(v) for v in idx[q]]) for q in o])
            sonuclar.setdefault(sen, []).append(kayit)
            log(sen, dm, R.tolist(), "n", n, "en iyi tork %.2f c=(%.0f,%.0f,%.0f)" % (tot[o[0]], c[o[0]][0], c[o[0]][1], c[o[0]][2]))
SONUC["tarama"] = sonuclar

ozet = {}
for sen in SENARYO:
    for dm in ("herhangi", "tabla", "duvar"):
        L = [k for k in sonuclar.get(sen, []) if k["destek"] == dm]
        L.sort(key=lambda k: k["en_iyi"][0]["tork"])
        ozet["%s/%s" % (sen, dm)] = [dict(R=k["R"], n=k["n"], tork=k["en_iyi"][0]["tork"], c=k["en_iyi"][0]["c"]) for k in L[:4]]
        for ad, f in (("alt", lambda c: c[1] < 178), ("ust", lambda c: c[1] >= 183)):
            L2 = [k for k in L if f(k["en_iyi"][0]["c"])]
            ozet["%s/%s/%s" % (sen, dm, ad)] = [dict(R=k["R"], n=k["n"], tork=k["en_iyi"][0]["tork"], c=k["en_iyi"][0]["c"]) for k in L2[:2]]
SONUC["ozet"] = ozet
for k, v in ozet.items():
    log("OZET", k, v[:1])


# ---------------------------------------------------------------- 3) kesin dogrulama (en iyi adaylar)
def pi_shape(R, t, parts):
    bx = []
    m = App.Matrix(R[0][0], R[0][1], R[0][2], t[0], R[1][0], R[1][1], R[1][2], t[1], R[2][0], R[2][1], R[2][2], t[2], 0, 0, 0, 1)
    for (_, x0, x1, y0, y1, z0, z1) in parts:
        b = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
        b.transformShape(m)
        bx.append(b)
    return (bx[0].fuse(bx[1:]) if len(bx) > 1 else bx[0]), m


def yakin(bb1, bb2, d):
    b = App.BoundBox(bb1)
    b.enlarge(d)
    return bool(b.intersect(bb2))


adaylar = []
for sen in SENARYO:
    for dm in ("tabla", "herhangi"):
        for bolge in ("ust", "alt"):
            for e in ozet.get("%s/%s/%s" % (sen, dm, bolge), [])[:1]:
                for k in sonuclar[sen]:
                    if k["destek"] == dm and k["R"] == e["R"]:
                        adaylar.append((sen, dm, bolge, k, k["en_iyi"][0]))
                        break
log("kesin dogrulanacak aday", len(adaylar))
kesin = []
for (sen, dm, bolge, k, e) in adaylar:
    R = k["R"]
    perm, sg = tuple(k["perm"]), tuple(k["sg"])
    lop = lo_donus(perm, sg)
    i, j, kk = e["idx"]
    t = np.array([X0 + i * H, Y0 + j * H, Z0 + kk * H]) - lop
    body, m = pi_shape(R, t, GOVDE)
    kor, _ = pi_shape(R, t, SENARYO[sen])
    ovl = []
    mind, en_yakin = 1e9, ""
    for p in KAF:
        sh = p["shape"]
        if not yakin(body.BoundBox, sh.BoundBox, 12):
            continue
        v = body.common(sh).Volume if body.BoundBox.intersect(sh.BoundBox) else 0.0
        vk = kor.common(sh).Volume if kor.BoundBox.intersect(sh.BoundBox) else 0.0
        d = body.distToShape(sh)[0]
        if d < mind:
            mind, en_yakin = d, p["ad"]
        if v > 0.5 or vk > 0.5:
            ovl.append((p["ad"], round(v, 1), round(vk, 1)))
    tilt_cak = []
    for th in THS:
        bt = body.copy()
        bt.transformShape(KP.Ptilt(th).toMatrix())
        for p in PAN + GOV:
            sh = p["shape"]
            if bt.BoundBox.intersect(sh.BoundBox):
                v = bt.common(sh).Volume
                if v > 0.5:
                    tilt_cak.append((th, p["ad"], round(v, 1)))
    pcc = np.array(R).dot(np.array([42.5, 28.0, 0.65])) + t
    bb = body.BoundBox
    kesin.append(dict(sen=sen, destek=dm, bolge=bolge, R=R, t=[round(float(v), 2) for v in t], pcb_merkez=[round(float(v), 1) for v in pcc],
                      tork_tahmin=e["tork"], kafa_parca_cakisma=ovl, en_yakin_mm=round(mind, 2), en_yakin_parca=en_yakin,
                      tilt_cakisma=tilt_cak, bb=[round(v, 1) for v in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)]))
    log("KESIN", sen, dm, bolge, "pcb", kesin[-1]["pcb_merkez"], "cakisma", ovl, "en yakin %.1f %s" % (mind, en_yakin), "tilt", tilt_cak[:3])
SONUC["kesin"] = kesin

json.dump(SONUC, open(os.path.join(BU, "pi_kafada_sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("bitti")
