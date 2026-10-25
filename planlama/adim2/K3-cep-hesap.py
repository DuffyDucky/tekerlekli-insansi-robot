# K3 (Y1b kontrol) K4 HESAP: U ucu payi hangi engelle sinirli, u_pay 7,0 ya da uc pimi kaydirmanin etkisi. Model dosyalarina dokunmaz.
# Engel (2B, x = kanal ortasi): kaset duvari seridi (kabuk_parcalar kurali: halka dilimi + U(phi 135) yuzu u_pay offset + pim diski,
# 2 mm ic serit) + ust uc pimi dikmesi (post_r diski, gerçek govdede dolu). Pim yeri kabuk_parcalar kurali: U merkez cizgisine
# >= kalinlik/2 + bosluk + post_r + 0,5 (bosluk degistirilerek). Kablo: K2-u bagimsiz cozucu (bag 145 + phi, duvar bagi 228,3, L).
# Dogrulama: (6,5 / bosluk 0,5) FCStd olcumuyle (K3-cep.json U_duvar) ayni esikleri vermeli. Cikti: K3-cep-hesap.json
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part
A, V, log = O.A, O.V, O.log
U = O.yukle("K2-u.py")
sys.path.insert(0, os.path.join(O.R, "dirsek"))
import kablo_yolu as KY
t0 = time.time()
KK = A.KOL_KABLO
S1 = KK["s1"]
DU = S1["duvar"]
TB = S1["tambur"]
KAL = S1["serit"] * KK["serit"][1]
RI = TB["r"][1] + KAL / 2
RO = DU["r"][0] - KAL / 2
L0 = S1["L"]
S1O = KY.s1_olcu(KK)
S1U = KY.s1_poz(KK, A.OMUZ["one_arka_aralik"][1], S1O)
u_ = [V(0, q.y, q.z) for q in S1U["u_nokta"]]
UF = Part.Face(Part.Wire(Part.makePolygon(u_ + [u_[0]])))
psi_a = S1U["psi_U"] + S1O["U"]["delta"]


def yz(psi, r):
    y, z = KY.psi_yz(psi, r)
    return V(0, y, z)


def yay(r0, r1, p0, p1, adim=1.0):
    n = max(2, int(abs(p1 - p0) / adim) + 1)
    dis = [yz(p0 + (p1 - p0) * i / n, r1) for i in range(n + 1)]
    ic = [yz(p1 - (p1 - p0) * i / n, r0) for i in range(n + 1)]
    return Part.Face(Part.makePolygon(dis + ic + [dis[0]]))


def daire(r, m=V(0, 0, 0)):
    return Part.Face(Part.Wire(Part.makeCircle(r, m, V(1, 0, 0))))


def engel(u_pay, bosluk):
    pm = DU["pim"]
    u2 = [(q.y, q.z) for q in S1U["u_nokta"]]
    pp = S1U["u_uc_psi"]
    while True:
        c = KY.psi_yz(pp, pm["r"])
        if min(math.hypot(c[0] - a_, c[1] - b_) for a_, b_ in u2) >= S1O["kalinlik"] / 2 + bosluk + pm["post_r"] + 0.5:
            break
        pp += 0.5
    tb = yay(DU["flans_r_ic"], DU["r"][1], DU["psi0"], psi_a).fuse([UF.makeOffset2D(u_pay, 0), daire(pm["post_r"] + 2.0, yz(pp, pm["r"]))])
    tb = tb.common(daire(DU["r"][1]).cut(daire(DU["flans_r_ic"]))).removeSplitter()
    f = tb.Faces[0]
    ser = f.cut(f.makeOffset2D(-2.0, 0)).cut(daire(DU["ic_kes_r"]))
    post = daire(pm["post_r"], yz(pp, pm["r"]))
    dis = [yz(ps, DU["r"][1]) for ps in np.arange(DU["psi0"], 360.0, 0.5)]
    return dict(serit=ser, post=post, pim_psi=pp, uc_psi=max(O.yz_psi(v.Y, v.Z)[0] for v in f.Vertexes),
                y_max=round(f.BoundBox.YMax, 2), z_max=round(f.BoundBox.ZMax, 2), alan=round(f.Area, 1), serit_alan=round(ser.Area, 1))


VAR = {"6.5/0.5 (mevcut)": (6.5, 0.5), "7.0/0.5": (7.0, 0.5), "6.5/1.0": (6.5, 1.0), "7.0/1.0": (7.0, 1.0), "6.5/1.5": (6.5, 1.5),
       "4.5/0.5 (eski)": (4.5, 0.5), "6.0/1.0": (6.0, 1.0), "5.75/1.0": (5.75, 1.0)}
E = {k: engel(*v) for k, v in VAR.items()}
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"), varyant={k: {kk: vv for kk, vv in e.items() if kk not in ("serit", "post")} for k, e in E.items()})
log(OUT["varyant"])


def coz(phi, L):
    c = U.coz(RI, RO, TB["bag_psi"] + phi, S1["bag_duvar_psi"], L, N=240)
    k = np.abs(c["k"])
    jm = int(np.argmax(k))
    pos = np.where(c["k"][:jm] >= 0)[0]
    i_inf = int(pos.max()) + 1 if len(pos) else 0
    dis = np.where(c["do"][jm + 1:] < 0.02)[0]
    i_dis = jm + 1 + int(dis.min()) if len(dis) else len(c["P"]) - 1
    n5 = int(5.0 / c["ds"])
    Ub = c["P"][i_inf:max(i_inf + 2, i_dis - n5)]
    return Part.makePolygon([V(0, q[0], -q[1]) for q in Ub]), U.ozet(c)


def olc(ub):
    r = {}
    for k, e in E.items():
        r[k] = dict(duvar=round(e["serit"].distToShape(ub)[0] - KAL / 2, 3), pim=round(e["post"].distToShape(ub)[0] - KAL / 2, 3))
        r[k]["en_az"] = min(r[k]["duvar"], r[k]["pim"])
    return r


SAT = []
for phi, dL in [(135.0, x) for x in np.arange(-5.0, 6.01, 0.5)] + [(x, 0.0) for x in np.arange(135.5, 143.01, 0.5)] + \
               [(x, 0.0) for x in (-45.0, 0.0, 45.0, 90.0, 120.0)]:
    ub, oz = coz(float(phi), L0 + float(dL))
    SAT.append(dict(phi=float(phi), dL=float(dL), u_uc_psi=round(oz["u_uc_psi"], 2), R_min=round(oz["R_min"], 3), olc=olc(ub)))
    log(phi, dL, {k: v["en_az"] for k, v in SAT[-1]["olc"].items()}, "%.0fs" % (time.time() - t0))
OUT["satir"] = SAT


def esik(seri, anahtar, k, alan):
    """en_az > 0 -> <= 0 gecisi (dogrusal ara deger)."""
    q = [(s[anahtar], s["olc"][k][alan]) for s in seri]
    for (a0, v0), (a1, v1) in zip(q[:-1], q[1:]):
        if v0 > 0 >= v1:
            return round(a0 + (a1 - a0) * v0 / (v0 - v1), 2)
    return None


Ls = [s for s in SAT if s["phi"] == 135.0 and s["dL"] >= 0]
Ps = [s for s in SAT if s["dL"] == 0.0 and s["phi"] >= 135.0]
Ps.sort(key=lambda s: s["phi"])
OUT["esik"] = {k: dict(L_en_az=esik(Ls, "dL", k, "en_az"), L_duvar=esik(Ls, "dL", k, "duvar"), L_pim=esik(Ls, "dL", k, "pim"),
                       S1_en_az=None if esik(Ps, "phi", k, "en_az") is None else round(esik(Ps, "phi", k, "en_az") - 135.0, 2),
                       S1_duvar=None if esik(Ps, "phi", k, "duvar") is None else round(esik(Ps, "phi", k, "duvar") - 135.0, 2),
                       S1_pim=None if esik(Ps, "phi", k, "pim") is None else round(esik(Ps, "phi", k, "pim") - 135.0, 2),
                       aralik_icinde_en_az=min(s["olc"][k]["en_az"] for s in SAT if s["dL"] == 0.0 and s["phi"] <= 135.0))
               for k in E}
log(json.dumps(OUT["esik"], indent=0))
json.dump(OUT, open(os.path.join(HERE, "K3-cep-hesap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("bitti %.0fs" % (time.time() - t0))
