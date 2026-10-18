# K2 hizli taramalar (nokta bulutu + KD agaci on tarama, en kucuk pozlarda kesin distToShape). Yalniz okur. Cikti: K2-tarama.json
#   1) tambur <-> sabit parcalar (omuz govde, kabuk bant + isil gomme, kaset + civatalari), S1 -60...180 (1)
#   2) tambur <-> kol zinciri, S2 0...120 (ince alt uc)
#   3) kaset (+ civatalari) <-> kol zinciri, S1 -45...135 (2,5) x S2 5...30 (0,5) + 30...120 (5); ince komsuluk; S2 3...5 bilgi
#   4) gobek (tambur haric) <-> kaset + kabuk bant + isil gomme, S1 -60...180 (1)
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part
import MeshPart
from scipy.spatial import cKDTree

A, V, log, tasi = O.A, O.V, O.log, O.tasi
t0 = time.time()
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"), yontem="MeshPart MaxLength 0,6 nokta bulutu + cKDTree; en kucuk 6 poz kesin distToShape")
OMU = O.ac("omuz/omuz-montaj.FCStd")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd")


def sec(P, kosul):
    return [(p["ad"], p["shape"]) for p in P if kosul(p)]


GOV = sec(OMU, lambda p: p["grup"] == "Govde" and p["tur"] != "Referans")
GOB = sec(OMU, lambda p: p["grup"] == "Gobek")
TAMBUR = [(a, s) for a, s in GOB if a == "S1 kablo tamburu"]
GOB_D = [(a, s) for a, s in GOB if a != "S1 kablo tamburu"]
KOL = sec(OMU, lambda p: p["grup"] == "Kol") + sec(DIR, lambda p: p["grup"] == "UstKol")
KASET = sec(KAB, lambda p: p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi"))
BANT = sec(KAB, lambda p: p["ad"].startswith("Omuz bandi") or p["ad"].startswith("Gogus bandi") or "S1 kaseti" in p["ad"])


def bulut(lst, ml=0.6, kutu=None):
    """Yuzey nokta bulutu: tessellate(0,05) ucgenleri barisentrik izgarayla <= ml araliga bolunur (Mefisto MaxLength buyuk
    kabukta takiliyordu). kutu (App.BoundBox) verilirse noktalar kirpilir."""
    P, ad = [], []
    for i, (a, s) in enumerate(lst):
        if kutu is not None and not s.BoundBox.intersect(kutu):
            continue
        pts, tri = s.tessellate(0.05)
        X = np.array([[p.x, p.y, p.z] for p in pts])
        Tr = np.array(tri, dtype=int)
        if len(Tr) == 0:
            continue
        A0, B0, C0 = X[Tr[:, 0]], X[Tr[:, 1]], X[Tr[:, 2]]
        Lm = np.max(np.stack([np.linalg.norm(B0 - A0, axis=1), np.linalg.norm(C0 - B0, axis=1), np.linalg.norm(A0 - C0, axis=1)]), 0)
        nn = np.maximum(1, np.ceil(Lm / ml)).astype(int)
        q = [X]
        for n in np.unique(nn):
            m = nn == n
            ij = np.array([(u, v) for u in range(n + 1) for v in range(n + 1 - u)], float) / n
            q.append((A0[m][:, None, :] + (B0[m] - A0[m])[:, None, :] * ij[None, :, 0:1] + (C0[m] - A0[m])[:, None, :] * ij[None, :, 1:2]).reshape(-1, 3))
        Q = np.vstack(q)
        if kutu is not None:
            k = ((Q[:, 0] >= kutu.XMin) & (Q[:, 0] <= kutu.XMax) & (Q[:, 1] >= kutu.YMin) & (Q[:, 1] <= kutu.YMax) &
                 (Q[:, 2] >= kutu.ZMin) & (Q[:, 2] <= kutu.ZMax))
            Q = Q[k]
        if len(Q) == 0:
            continue
        _, ui = np.unique(np.floor(Q / (0.5 * ml)).astype(np.int64), axis=0, return_index=True)   # voksel seyreltme (0,5 ml)
        Q = Q[ui]
        P.append(Q)
        ad += [i] * len(Q)
    log("bulut", len(ad), "nokta", "%.0fs" % (time.time() - t0))
    return np.vstack(P), np.array(ad)


def mat(pl):
    m = pl.toMatrix()
    R = np.array([[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]])
    t = np.array([m.A14, m.A24, m.A34])
    return R, t


def tara(hareketli, sabit, pozlar, pl_f, ad_h, ad_s, ml=0.6, kutu=None, kesin=6):
    """hareketli parcalar pl_f(poz) ile tasinir, sabit KD agacina en yakin mesafe. Doner: (satirlar, kesin)."""
    Ps, Is = bulut(sabit, ml, kutu)
    tree = cKDTree(Ps)
    Ph, Ih = bulut(hareketli, ml)
    sat = []
    for poz in pozlar:
        R, t = mat(pl_f(poz))
        Q = Ph @ R.T + t
        d, j = tree.query(Q, distance_upper_bound=30.0)
        i = int(np.argmin(d))
        sat.append((poz, float(d[i]), ad_h[Ih[i]], ad_s[Is[j[i]]] if np.isfinite(d[i]) else None))
    sat.sort(key=lambda q: q[1])
    kes = []
    for poz, d, a, b in sat[:kesin]:
        pl = pl_f(poz)
        hs = [(x, tasi(s, pl)) for x, s in hareketli]
        dd, aa, bb = O.enaz(hs, sabit, pay=3)
        h = 0.0
        if dd < 1e-6:
            for x, s in hs:
                for y, q in sabit:
                    if s.BoundBox.intersect(q.BoundBox):
                        h += s.common(q).Volume
        kes.append((poz, round(dd, 3), aa, bb, round(h, 3)))
    return sat, kes


def ad(lst):
    return [a for a, _ in lst]


ADIM = os.environ.get("K2_ADIM", "hepsi")
JS = "K2-tarama-%s.json" % ADIM

if ADIM in ("hepsi", "tambur"):
    SAB = GOV + BANT + KASET
    pz = [float(p) for p in np.arange(-60, 180.01, 1.0)]
    KT = App.BoundBox(140, -60, -60, 175, 60, 60)
    sat, kes = tara(TAMBUR, SAB, pz, O.Pp, ad(TAMBUR), ad(SAB), kutu=KT)
    ic = [q for q in sat if -45 <= q[0] <= 135]
    OUT["tambur_sabit"] = dict(on_min_aralik=ic[0], kesin=kes, en_kucuk_10=sat[:10])
    log("tambur-sabit", ic[0], kes)
    CAPB = [(a, s) for a, s in GOV if a.startswith("Kapak civatasi")]
    sat, kes = tara(TAMBUR, CAPB, pz, O.Pp, ad(TAMBUR), ad(CAPB), ml=0.3, kutu=KT)
    OUT["tambur_kapak_civata"] = dict(kesin=kes, en_kucuk_10=sat[:10])
    log("tambur-civata", kes)
    pz2 = [0.0, 1.0, 2.0, 3.0, 3.5, 3.75, 4.0, 4.25, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 10.0] + [float(x) for x in np.arange(12.5, 120.01, 2.5)]
    Pt, It = bulut(TAMBUR, 0.4)
    tree = cKDTree(Pt)
    Pk, Ik = bulut(KOL, 0.4, kutu=App.BoundBox(125, -60, -50, 245, 60, 50))
    tk = []
    for th in pz2:
        R, t = mat(O.Pr(th))
        d, j = tree.query(Pk @ R.T + t, distance_upper_bound=40.0)
        i = int(np.argmin(d))
        tk.append((th, round(float(d[i]), 3), ad(KOL)[Ik[i]]))
    for th in (3.5, 3.75, 4.0, 4.25, 5.0):
        hs = [(x, tasi(s, O.Pr(th))) for x, s in KOL]
        dd, aa, bb = O.enaz(TAMBUR, hs, pay=3)
        tk.append(("kesin", th, round(dd, 3), bb))
    OUT["tambur_kol"] = tk
    log("tambur-kol", tk)
    O.kaydet(JS, OUT)

if ADIM in ("hepsi", "kaset"):
    PH = [float(x) for x in np.arange(-45, 135.01, 2.5)]
    TH = [float(x) for x in np.arange(5.0, 30.01, 0.5)] + [float(x) for x in np.arange(35, 120.01, 5)]
    pozlar = [(p, t) for p in PH for t in TH]

    def plf(pz):
        return O.Pp(pz[0]).multiply(O.Pr(pz[1]))
    KK_ = App.BoundBox(90, -95, -85, 280, 95, 85)          # kol cercevesinde kasetin ulasabilecegi bolge
    plfi = lambda pz: plf(pz).inverse()
    sat, kes = tara(KASET, KOL, pozlar, plfi, ad(KASET), ad(KOL), ml=0.6, kutu=KK_)
    OUT["kaset_kol"] = dict(kesin=kes, en_kucuk_15=sat[:15], poz_sayisi=len(pozlar))
    # her S2 icin en kucuk (on tarama)
    by_t = {}
    for (p, t), d, a, b in sat:
        if t not in by_t or d < by_t[t][0]:
            by_t[t] = (round(d, 3), p, a, b)
    OUT["kaset_kol_S2_basina"] = sorted([(t,) + v for t, v in by_t.items()])
    log("kaset-kol", kes)
    alt = [(p, t) for p in PH for t in (3.0, 3.5, 4.0, 4.5)]
    sat2, kes2 = tara(KASET, KOL, alt, plfi, ad(KASET), ad(KOL), ml=0.6, kesin=4, kutu=KK_)
    OUT["kaset_kol_alt_sinir_alti"] = dict(kesin=kes2, en_kucuk_8=sat2[:8])
    log("kaset-kol alt", kes2)
    O.kaydet(JS, OUT)

if ADIM in ("hepsi", "gobek"):
    SAB = KASET + BANT
    pz = [float(p) for p in np.arange(-60, 180.01, 1.0)]
    sat, kes = tara(GOB_D, SAB, pz, O.Pp, ad(GOB_D), ad(SAB), kutu=App.BoundBox(140, -110, -110, 200, 110, 110))
    ic = [q for q in sat if -45 <= q[0] <= 135]
    OUT["gobek_kaset_bant"] = dict(on_min_aralik=ic[0], kesin=kes, en_kucuk_10=sat[:10])
    log("gobek", ic[0], kes)
    dd, aa, bb = O.enaz(BANT + KASET, GOV, pay=3)
    OUT["bant_kaset_omuz_govde"] = (round(dd, 3), aa, bb)
    log("bant-govde", OUT["bant_kaset_omuz_govde"])
    O.kaydet(JS, OUT)

if ADIM in ("hepsi", "montaj"):
    M = {}
    # 1) kaset (govde + kapak) +x yonunden kaydirilirken (t: 0...120 mm) gobek + kol ile en kucuk mesafe
    kas2 = [(a, s) for a, s in KASET if a.startswith("S1 kaset")]
    Pk, Ik = bulut(kas2, 0.6)
    kay = []
    for phi in (-45.0, -20.0, 0.0, 45.0, 90.0, 135.0):
        for th in (5.0, 30.0, 90.0):
            hed = [(a, tasi(s, O.Pp(phi))) for a, s in GOB] + [(a, tasi(s, O.Pp(phi).multiply(O.Pr(th)))) for a, s in KOL]
            Ph, Ih = bulut(hed, 0.6, kutu=App.BoundBox(140, -90, -90, 290, 90, 90))
            tree = cKDTree(Ph)
            en = (1e9, None, None)
            for t in np.arange(0.5, 120.01, 0.5):
                d, j = tree.query(Pk + np.array([t, 0, 0]), distance_upper_bound=20.0)
                i = int(np.argmin(d))
                if d[i] < en[0]:
                    en = (float(d[i]), float(t), ad(hed)[Ih[j[i]]])
            kay.append(dict(phi=phi, th=th, en_kucuk=round(en[0], 3), t=en[1], parca=en[2]))
            log("kaydirma", kay[-1])
    M["kaydirma"] = kay
    # 2) kaset civatasi alet erisimi: bas ekseninde +x yonunde x 159,5 -> 330 dogru parcasi; gobek + kol en yakin (alet yaricapi icin)
    eris = []
    for a, s in KASET:
        if not a.startswith("Kaset civatasi"):
            continue
        c = s.BoundBox.Center
        line = Part.makeLine(V(s.BoundBox.XMax + 0.01, c.y, c.z), V(330.0, c.y, c.z))
        for phi in range(-45, 136, 5):
            for th in (5.0, 45.0, 90.0):
                hed = [(b, tasi(q, O.Pp(float(phi)))) for b, q in GOB] + [(b, tasi(q, O.Pp(float(phi)).multiply(O.Pr(th)))) for b, q in KOL]
                d, _, b = O.enaz([("l", line)], hed, pay=8)
                eris.append((a, phi, th, round(d, 2), b))
        log("erisim", a, max(eris, key=lambda q: q[3] if q[0] == a else -1))
    M["civata_erisim"] = eris
    # 3) tambur kablo bagi kayisi: halkanin altindan (r 36...37) iki yarik arasinda 1,0 mm kalin, 2,5 mm genis kayis
    TB = A.KOL_KABLO["s1"]["tambur"]
    bag = TB["bag_psi"]

    def sektor(r0, r1, x0, x1, p0, p1):
        n = 40
        dis = [V(x0, *O.psi_yz(p0 + (p1 - p0) * i / n, r1)) for i in range(n + 1)]
        ic = [V(x0, *O.psi_yz(p1 - (p1 - p0) * i / n, r0)) for i in range(n + 1)]
        return Part.Face(Part.makePolygon(dis + ic + [dis[0]])).extrude(V(x1 - x0, 0, 0))
    xm = (154.4 + 157.4) / 2
    ks0 = sektor(TB["r"][0] - 1.0, TB["r"][0], xm - 1.25, xm + 1.25, bag + 3.0 - 1.25, bag + 11.0 + 1.25)
    tb_c = ks0.common(TAMBUR[0][1]).Volume
    CAPB = [(a, s) for a, s in GOV if a.startswith("Kapak civatasi") or a == "Rulman kapagi"]
    sat = []
    for phi in np.arange(-45, 135.01, 1.0):
        ks = tasi(ks0, O.Pp(float(phi)))
        d, _, b = O.enaz([("k", ks)], CAPB, pay=5)
        sat.append((float(phi), round(d, 3), b))
    M["kayis"] = dict(model="r %.1f...%.1f, x %.2f...%.2f, psi_g %.2f...%.2f" % (TB["r"][0] - 1, TB["r"][0], xm - 1.25, xm + 1.25, bag + 1.75, bag + 12.25),
                      tambura_giris_mm3=round(tb_c, 3), en_az=min(sat, key=lambda q: q[1]), temas_phi=[q[0] for q in sat if q[1] < 1e-6])
    log("kayis", M["kayis"])
    OUT["montaj"] = M
    O.kaydet(JS, OUT)

O.kaydet(JS, OUT)
log("bitti %.0fs" % (time.time() - t0))
