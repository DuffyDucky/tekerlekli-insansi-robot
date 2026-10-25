# K3: U cebi yeniden kurulumu (kabuk_parcalar kurali, u_pay 4,5 / 6,5 / 7,0) <-> kabuk-montaj.FCStd govde dilimi: sapma nerede.
import os, sys, math, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import FreeCAD as App
import Part
A, V, log = O.A, O.V, O.log
sys.path.insert(0, os.path.join(O.R, "dirsek"))
import kablo_yolu as KY
KK = A.KOL_KABLO
S1 = KK["s1"]
DU = S1["duvar"]
XC = 0.5 * sum(S1["kanal_x"])
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd", "K3C"))
G = {p["ad"]: p["shape"] for p in KAB}["S1 kaset govdesi sag"]
S1O = KY.s1_olcu(KK)
S1U = KY.s1_poz(KK, A.OMUZ["one_arka_aralik"][1], S1O)
u_ = [V(0, q.y, q.z) for q in S1U["u_nokta"]]
UF = Part.Face(Part.Wire(Part.makePolygon(u_ + [u_[0]])))
out = dict(u_uc_psi=S1U["u_uc_psi"], psi_U=S1U["psi_U"])
ws = G.slice(V(1, 0, 0), XC)
out["tel"] = [(round(w.BoundBox.DiagonalLength, 1), round(w.Length, 1)) for w in ws]
pts = []
for w in ws:
    for p in w.discretize(Distance=0.5):
        ps, r = O.yz_psi(p.y, p.z)
        pts.append((p, ps, r))
# U yuzune (offsetsiz) uzaklik: ic duvar yuzu = u_pay - 2 olmali (U ucu bolgesinde)
res = {}
for (lo, hi) in ((280, 300), (300, 315), (315, 322), (322, 330), (330, 345)):
    q = [(UF.distToShape(Part.Vertex(V(0, p.y, p.z)))[0], ps, r) for p, ps, r in pts if lo <= ps < hi and 46 < r < 77.1]
    q = [x for x in q if x[0] > 1e-6]
    res["psi %d-%d" % (lo, hi)] = sorted(set(round(x[0], 2) for x in q))[:6]
out["U_yuzune_uzaklik_en_kucuk"] = res
log(json.dumps(out, ensure_ascii=False, indent=0))
# U ucu (u_nokta en buyuk psi) -> en yakin duvar noktasi: FCStd dilimi ve yeniden kurulum (4,5 / 6,5 / 7,0)
T = max(u_, key=lambda q: O.yz_psi(q.y, q.z)[0])
out2 = dict(uc=[round(T.y, 2), round(T.z, 2)] + [round(x, 2) for x in O.yz_psi(T.y, T.z)])
TX = V(XC, T.y, T.z)
d, pp, _ = G.distToShape(Part.Vertex(TX))
out2["fcstd_govde"] = (round(d, 3), [round(x, 2) for x in O.yz_psi(pp[0][0].y, pp[0][0].z)])


def taban(up):
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
    pm = DU["pim"]
    u2 = [(q.y, q.z) for q in S1U["u_nokta"]]
    pp_ = S1U["u_uc_psi"]
    while True:
        c = KY.psi_yz(pp_, pm["r"])
        if min(math.hypot(c[0] - a_, c[1] - b_) for a_, b_ in u2) >= S1O["kalinlik"] / 2 + pm["bosluk"] + pm["post_r"] + 0.5:
            break
        pp_ += 0.5
    tb = yay(DU["flans_r_ic"], DU["r"][1], DU["psi0"], psi_a).fuse([UF.makeOffset2D(up, 0), daire(pm["post_r"] + 2.0, yz(pp_, pm["r"]))])
    tb = tb.common(daire(DU["r"][1]).cut(daire(DU["flans_r_ic"]))).removeSplitter()
    f = tb.Faces[0]
    return f, len(tb.Faces), pp_
for up in (4.5, 6.5, 7.0):
    f, nf, pp_ = taban(up)
    ic = f.makeOffset2D(-2.0, 0)
    ser = f.cut(ic)
    d, pp, _ = ser.distToShape(Part.Vertex(V(0, T.y, T.z)))
    out2["yeniden %.1f" % up] = dict(yuz=nf, pim_psi=pp_, uc_duvar=round(d, 3), nokta=[round(x, 2) for x in O.yz_psi(pp[0][0].y, pp[0][0].z)],
                                    taban_alan=round(f.Area, 1), ic_alan=round(ic.Area, 1))
# FCStd taban (arka plaka dilimi x 152,5) alanı: yeniden kurulumla kiyas
tb_f = G.slice(V(1, 0, 0), 152.5)
out2["fcstd_arka_dilim_uzunluk"] = [round(w.Length, 1) for w in tb_f]
out2["fcstd_arka_alan"] = round(Part.Face(Part.Wire(max(tb_f, key=lambda w: w.Length))).Area, 1)
log(json.dumps(out2, ensure_ascii=False))
# 2B: U ucu noktasi (x XC) -> FCStd govde dilim telleri; ve yeniden kurulum seridi (x XC'ye tasinmis)
out3 = {}
for xk in (154.0, XC, 157.9):
    best = (1e9, None)
    for w in G.slice(V(1, 0, 0), xk):
        d, pp, _ = w.distToShape(Part.Vertex(V(xk, T.y, T.z)))
        if d < best[0]:
            best = (round(d, 3), [round(x, 2) for x in O.yz_psi(pp[0][0].y, pp[0][0].z)], round(w.BoundBox.DiagonalLength, 1))
    out3["fcstd x %.1f" % xk] = best
# U ucu cevresinde psi 318...335 boyunca duvar ic yuzu yaricapi (FCStd x XC) vs yeniden 6,5 / 4,5
ws = G.slice(V(1, 0, 0), XC)
prof = []
for up in (None, 4.5, 6.5):
    if up is None:
        sh = Part.Compound(ws)
        xx = XC
    else:
        f, nf, pp_ = taban(up)
        sh = f.cut(f.makeOffset2D(-2.0, 0))
        xx = 0.0
    row = []
    for ps in (316, 320, 324, 326, 328, 330):
        # radyal isin r 46 -> 77: ilk kesisim (ic yuz)
        a = math.radians(ps)
        ln = Part.makeLine(V(xx, 46 * math.cos(a), -46 * math.sin(a)), V(xx, 77 * math.cos(a), -77 * math.sin(a)))
        cm = ln.common(sh) if up is not None else None
        if up is None:
            ip = []
            for w in ws:
                for e in w.Edges:
                    for v in ln.section(e).Vertexes:
                        ip.append(math.hypot(v.Y, v.Z))
            row.append((ps, sorted(round(x, 2) for x in ip)[:4]))
        else:
            row.append((ps, sorted(round(math.hypot(v.Y, v.Z), 2) for e in cm.Edges for v in e.Vertexes)[:4]))
    prof.append((up, row))
out3["radyal_profil"] = prof
log(json.dumps(out3, ensure_ascii=False))
