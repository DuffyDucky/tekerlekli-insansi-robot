# K2 (2. ajan): (1) demet tutma: tambur dudaklari + kaset flans / arka plaka + kabuk ped arasindaki kanalin (x, r) haritasi; kanaldan
# eksenel kacis acikligi (r bandi, x). (2) ic kosunun tamburdan kalktigi yer (sabit psi), o noktada dudak kavramasi ve flans var mi.
# (3) S2 lopu <-> kaset kapagi: flans ic kenarina pah onerisinin etkisi (gecici kesimle, dosya yazilmaz). Yalniz okur. Cikti: K2-dudak.json
# Calistir: FC_SCRIPT=<bu dosya> "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part

A, V, log, tasi = O.A, O.V, O.log, O.tasi
U = O.yukle("K2-u.py")
t0 = time.time()
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
OMU = O.ac("omuz/omuz-montaj.FCStd")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
GOV = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Govde" and p["tur"] != "Referans"]
TAMBUR = [p["shape"] for p in OMU if p["ad"] == "S1 kablo tamburu"][0]
KG = {p["ad"]: p["shape"] for p in KAB}
GV, KP = KG["S1 kaset govdesi sag"], KG["S1 kaset kapagi sag"]
BANT = KG["Omuz bandi sag"]
S1 = A.KOL_KABLO["s1"]
KK = A.KOL_KABLO
T = KK["serit"][1]
KAL = S1["serit"] * T
RI = S1["tambur"]["r"][1] + KAL / 2
RO = S1["duvar"]["r"][0] - KAL / 2
BAG = S1["tambur"]["bag_psi"]
PSI_W = S1["bag_duvar_psi"]


def kaydet():
    OUT["sure_s"] = round(time.time() - t0, 1)
    O.kaydet("K2-dudak.json", OUT)


# ---------------------------------------------------------------- (1) kanal haritasi: sabit psi'de r satirlari boyunca x isinlari
def satir(sekiller, psi, r, x0=148.0, x1=164.0):
    y, z = O.psi_yz(psi, r)
    ln = Part.makeLine(V(x0, y, z), V(x1, y, z))
    dolu = []
    for ad, s in sekiller:
        bb = s.BoundBox
        if not (bb.YMin - 1 <= y <= bb.YMax + 1 and bb.ZMin - 1 <= z <= bb.ZMax + 1):
            continue
        c = s.common(ln)
        for e in c.Edges:
            xs = sorted(v.Point.x for v in e.Vertexes)
            if xs[-1] - xs[0] > 1e-4:
                dolu.append((round(xs[0], 2), round(xs[-1], 2), ad))
    return sorted(dolu)


def kanal(dolu, xm=155.9):
    """xm'yi iceren bos aralik [lo, hi] (dolu araliklar disinda)."""
    lo, hi = -1e9, 1e9
    for a, b, _ in dolu:
        if b <= xm:
            lo = max(lo, b)
        elif a >= xm:
            hi = min(hi, a)
        else:
            return None                      # xm dolu (kanal yok / tambur govdesi)
    return [lo if lo > -1e8 else None, hi if hi < 1e8 else None]


harita = {}
for phi in (-45.0, 45.0, 135.0):
    tb = tasi(TAMBUR, O.Pp(phi))
    sek = [("tambur", tb), ("kaset govde", GV), ("kaset kapak", KP), ("bant", BANT)] + GOV
    for psi in (110.0, 150.0, 185.0, 200.0, 215.0, 240.0, 280.0, 320.0):
        rows = []
        for r in np.arange(38.5, 50.01, 0.25):
            d = satir(sek, psi, float(r))
            rows.append((round(float(r), 2), kanal(d), [q for q in d if 150 <= q[1] and q[0] <= 162]))
        harita["%g/%g" % (phi, psi)] = rows
    log("harita phi", phi, "%.0fs" % (time.time() - t0))
OUT["kanal"] = {k: [(r, k_) for r, k_, _ in v] for k, v in harita.items()}
OUT["kanal_dolu_ornek"] = {k: [(r, d) for r, _, d in v if r in (39.0, 41.0, 43.5, 44.0, 44.5, 46.0, 48.0)] for k, v in harita.items()}
kaydet()

# ---------------------------------------------------------------- (2) ic kosu kalkmasi: yer ve kavrama
kalk = []
for phi in (-70.0, -45.0, -30.0, 0.0, 45.0):
    c = U.coz(RI, RO, BAG + phi, PSI_W, S1["L"], N=240)
    oz = U.ozet(c)
    k = c["k"]
    jm = int(np.argmax(np.abs(k)))
    pos = np.where(k[:jm] >= 0)[0]
    i_inf = int(pos.max()) + 1 if len(pos) else 0
    di = c["di"][:i_inf + 1]
    j = int(np.argmax(di))
    psi_s = float(c["psi"][j])
    ic_kenar = RI + float(di[j]) - KAL / 2
    # kalkan bolgenin (di > 0,5) sabit psi kapsami
    m = np.where(di > 0.5)[0]
    kap = [float(c["psi"][m.min()]), float(c["psi"][m.max()])] if len(m) else None
    kalk.append(dict(phi=phi, kalkma=round(float(di[j]), 3), psi_sabit=round(psi_s, 1), psi_gobek=round((psi_s - phi) % 360, 1),
                     demet_ic_kenar_r=round(ic_kenar, 2), dis_kenar_r=round(ic_kenar + KAL, 2),
                     dudak_kavrama=round(S1["tambur"].get("dudak_r", 43.7) - ic_kenar, 2),
                     kaset_kapsaminda=bool(190.0 <= psi_s <= 335.0), kalkma_05_psi=kap, R_min=round(oz["R_min"], 3)))
    log("kalkma", kalk[-1])
OUT["ic_kalkma"] = kalk
kaydet()

# ---------------------------------------------------------------- (3) S2 lopu <-> kapak, flans ic kenarina pah onerisi
SL = KK["s2_lop"]
W = KK["serit"][0]
R_C = math.hypot(W, 2 * T) / 2
F, tF = V(*SL["F"]), V(*SL["F_teget"])
onceki, kk = None, None
LOP = {}
for th in [5.0, 6.0] + list(np.arange(9.0, 120.01, 3.0)):
    pl = O.Pr(float(th))
    M, tM = pl.multVec(V(*SL["M"])), pl.Rotation.multVec(V(*SL["M_teget"]))
    a0, a1 = math.atan2(tM.y, tM.x), math.atan2(tF.y, tF.x)
    if onceki is None:
        ph, E, h, kk = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150)
    else:
        kk = round(((onceki[-1] - onceki[0]) + a0 - a1) / (2 * math.pi))
        ph, E, h, kk = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150, th0=onceki, k=kk)
    onceki = ph
    if th >= 108:
        N = len(ph)
        ds = SL["L"] / N
        uv = np.vstack([[M.x, M.y], np.array([M.x, M.y]) + ds * np.cumsum(np.stack([np.cos(ph), np.sin(ph)], 1), 0)])
        s = np.linspace(0, 1, len(uv))
        s0 = 1.0 - SL["gecis"] / SL["L"]
        tt = np.clip((s - s0) / (1 - s0), 0, 1)
        w = M.z + (F.z - M.z) * tt * tt * (3 - 2 * tt)
        pts = [V(float(uv[i][0]), float(uv[i][1]), float(w[i])) for i in range(len(uv))]
        uz = np.cumsum([0] + [(b - a).Length for a, b in zip(pts[:-1], pts[1:])])
        LOP[float(th)] = Part.makePolygon([pts[i] for i in range(len(pts)) if 4.0 <= uz[i] <= uz[-1] - 4.0])


def pah_kes(sh, dx, dr, r0=44.2, x_dis=159.5):
    """Flans ic kenari (r0, x_dis) koşesine dx (eksenel) x dr (radyal) pah: ucgen kesitli halka cikarilir."""
    pr = Part.makePolygon([V(x_dis + 0.01, r0 - 0.01, 0), V(x_dis + 0.01, r0 + dr, 0), V(x_dis - dx, r0 - 0.01, 0), V(x_dis + 0.01, r0 - 0.01, 0)])
    f = Part.Face(pr)
    halka = f.revolve(V(0, 0, 0), V(1, 0, 0), 360)
    return sh.cut(halka)


pah = []
for ad, dx, dr in (("mevcut", 0, 0), ("pah 1,2 x 1,2 (tam kalinlik)", 1.2, 1.2), ("pah 1,2 x 2,0", 1.2, 2.0), ("pah 0,8 x 0,8", 0.8, 0.8)):
    kp = KP if dx == 0 else pah_kes(KP, dx, dr)
    for th, ken in LOP.items():
        best = (1e9, None)
        for phi in (115.0, 120.0, 125.0, 130.0, 135.0):
            d = kp.distToShape(tasi(ken, O.Pp(phi)))[0]
            if d < best[0]:
                best = (d, phi)
        pah.append(dict(durum=ad, yana=th, d=round(best[0], 3), cevrel=round(best[0] - R_C, 3), S1=best[1],
                        kapak_hacim=round(kp.Volume, 1)))
    log("pah", ad, [(q["yana"], q["cevrel"]) for q in pah if q["durum"] == ad])
OUT["s2_lop_pah"] = pah
OUT["r_cevrel"] = R_C
kaydet()
log("bitti %.0fs" % (time.time() - t0))
