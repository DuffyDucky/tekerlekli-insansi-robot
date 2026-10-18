# K2 kontrolu 1: kablo. S1 U lopu bagimsiz cozucuyle (K2-u.py) tam aralik + asim + duyarlilik; 3B demet (4,2 x 4,2 dikdortgen kesit)
# ile parcalar arasi bosluk ve giris hacmi; S2 lopu ve dirsek lopu bagimsiz serbest elastikayla; S2 lopu + gecis yolu <-> kaset / kabuk
# S1 x S2 izgarasinda; cikis yolu. Yalniz okur (FCStd gecici kopya). Cikti: planlama/adim2/K2-kablo.json
# Calistir: FC_SCRIPT=<bu dosya> "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
import os, sys, math, time, importlib.util
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
ADIM = os.environ.get("K2_ADIM", "hepsi")
JS = "K2-kablo.json" if ADIM == "hepsi" else "K2-kablo-%s.json" % ADIM

OMU = O.ac("omuz/omuz-montaj.FCStd")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd")
log("acildi %.1fs" % (time.time() - t0))


def sec(P, kosul):
    return [(p["ad"], p["shape"]) for p in P if kosul(p)]


GOV = sec(OMU, lambda p: p["grup"] == "Govde" and p["tur"] != "Referans")
GOB = sec(OMU, lambda p: p["grup"] == "Gobek")
TAMBUR = [(a, s) for a, s in GOB if a == "S1 kablo tamburu"]
GOB_D = [(a, s) for a, s in GOB if a != "S1 kablo tamburu"]
KOL = sec(OMU, lambda p: p["grup"] == "Kol") + sec(DIR, lambda p: p["grup"] == "UstKol")
ONK = sec(DIR, lambda p: p["grup"] in ("OnKol", "El"))
KASET = sec(KAB, lambda p: p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi"))
BANT = sec(KAB, lambda p: p["ad"].startswith("Omuz bandi") or p["ad"].startswith("Gogus bandi") or "S1 kaseti" in p["ad"])
log("parca: gov %d gob %d kol %d onk %d kaset %d bant %d" % (len(GOV), len(GOB), len(KOL), len(ONK), len(KASET), len(BANT)),
    [a for a, _ in KASET], [a for a, _ in BANT])

S1 = A.KOL_KABLO["s1"]
KK = A.KOL_KABLO
T = KK["serit"][1]
N_S = S1["serit"]
KAL = N_S * T                                   # demet kalinligi (radyal) 4,2
GEN = KK["serit"][0]                            # demet genisligi (eksenel) 4,2
RI = S1["tambur"]["r"][1] + KAL / 2             # 41,1
RO = S1["duvar"]["r"][0] - KAL / 2              # 73,1
XC = 0.5 * (S1["kanal_x"][0] + S1["kanal_x"][1])
L = S1["L"]
PSI_W = S1["bag_duvar_psi"]
BAG = S1["tambur"]["bag_psi"]
R_SIN = 7.5 * T + (N_S - 1) * T / 2             # 11,9
R_10 = 10 * T + (N_S - 1) * T / 2               # 15,4
OUT["s1_tanim"] = dict(ri=RI, ro=RO, xc=XC, L=L, psi_w=PSI_W, bag_psi=BAG, R_sinir=R_SIN, R_10d=R_10, demet=[GEN, KAL])


def demet_kati(P2, x0=None, x1=None, yari=KAL / 2):
    """2B merkez cizgisi (u = y, v = -z) -> dikdortgen kesitli demet katisi (x0...x1, radyal +-yari)."""
    x0 = XC - GEN / 2 if x0 is None else x0
    x1 = XC + GEN / 2 if x1 is None else x1
    P2 = np.asarray(P2)
    t = np.gradient(P2, axis=0)
    t /= np.linalg.norm(t, axis=1)[:, None]
    n = np.stack([-t[:, 1], t[:, 0]], 1)
    sol = P2 + yari * n
    sag = P2 - yari * n
    pts = [V(x0, q[0], -q[1]) for q in sol] + [V(x0, q[0], -q[1]) for q in sag[::-1]]
    pts.append(pts[0])
    f = Part.Face(Part.makePolygon(pts))
    return f.extrude(V(x1 - x0, 0, 0))


def mesafe_hacim(kati, hedef):
    """[(ad, mesafe, giris hacmi)] sinir kutusu on elemeli."""
    bb = App.BoundBox(kati.BoundBox)
    bb.enlarge(15)
    out = []
    for a, s in hedef:
        if not s.BoundBox.intersect(bb):
            continue
        d = kati.distToShape(s)[0]
        h = 0.0
        if d < 1e-6:
            try:
                h = kati.common(s).Volume
            except Exception:
                h = -1.0
        out.append((a, d, h))
    return out


def dilim_bosluk(P2, sekiller, xs=(154.0, XC, 157.9)):
    """Duzlem ici bosluk: sekiller x = sabit dilimlerinde; her kapali tel icin merkez cizgisine 2B mesafe - yari kalinlik.
    Doner [(ad, tel merkezi r, psi, bosluk)]."""
    out = []
    for xk in xs:
        tel = Part.makePolygon([V(xk, q[0], -q[1]) for q in P2])
        for a, s in sekiller:
            if not (s.BoundBox.XMin <= xk <= s.BoundBox.XMax):
                continue
            for w in s.slice(V(1, 0, 0), xk):
                c = w.BoundBox.Center
                ps, r = O.yz_psi(c.y, c.z)
                d = w.distToShape(tel)[0]
                out.append((a, round(xk, 2), round(r, 1), round(ps, 1), round(d - KAL / 2, 3), round(w.BoundBox.DiagonalLength, 1)))
    return out


# ============================================================ 1) S1 U lopu: tam aralik, 3B bosluk
if ADIM in ("hepsi", "s1"):
    PHIS = sorted(set(list(range(-45, 136, 5)) + [-44, -43, -42, 132, 133, 134]))
    TH_K = (5.0, 10.0, 20.0)
    KOL_TH = {th: [(a, tasi(s, O.Pr(th))) for a, s in KOL] for th in TH_K}
    sat = []
    for phi in PHIS:
        c = U.coz(RI, RO, BAG + phi, PSI_W, L, N=240)
        oz = U.ozet(c)
        P2 = c["P"]
        kat = demet_kati(P2)
        pp = O.Pp(phi)
        hedef_sabit = GOV + BANT + KASET
        hedef_gob = [(a + " (S1 %g)" % phi, tasi(s, pp)) for a, s in GOB]
        hedef_kol = []
        for th in TH_K:
            hedef_kol += [("%s (S1 %g, S2 %g)" % (a, phi, th), tasi(s, pp)) for a, s in KOL_TH[th]]
        m = mesafe_hacim(kat, hedef_sabit + hedef_gob + hedef_kol)
        # duzlem ici: kaset dilimleri (dikme, pim, duvar) + tambur dilimleri
        dl = dilim_bosluk(P2, KASET[:2] + [(a, s) for a, s in hedef_gob if a.startswith("S1 kablo tamburu")])
        sat.append(dict(phi=phi, ozet={k: round(v, 3) for k, v in oz.items()}, ok=c["ok"],
                        mesafe=sorted([(a, round(d, 3), round(h, 3)) for a, d, h in m], key=lambda q: q[1])[:12],
                        dilim=sorted(dl, key=lambda q: q[4])[:10]))
        en = sat[-1]["mesafe"][:4]
        log("S1 phi %4g R %.2f a_ic %.1f a_dis %.1f kalkma %.2f uc %.1f | %s | dilim %s  %.0fs" % (
            phi, oz["R_min"], oz["a_ic"], oz["a_dis"], oz["ic_kalkma"], oz["u_uc_psi"], en, sat[-1]["dilim"][:3], time.time() - t0))
    OUT["s1_tarama"] = sat
    # ozet: tasarim geregi temas (tambur, kaset duvari) disindaki en kucuk bosluk
    temas = ("S1 kablo tamburu", "S1 kaset govdesi sag")
    diger = [(q["phi"], a, d) for q in sat for a, d, h in q["mesafe"] if not a.startswith(temas)]
    giris = [(q["phi"], a, h) for q in sat for a, d, h in q["mesafe"] if h > 0.05]
    OUT["s1_ozet"] = dict(R_min=min(q["ozet"]["R_min"] for q in sat), R_max=max(q["ozet"]["R_min"] for q in sat),
                          a_ic_min=min(q["ozet"]["a_ic"] for q in sat), a_dis_min=min(q["ozet"]["a_dis"] for q in sat),
                          ic_kalkma_max=max(q["ozet"]["ic_kalkma"] for q in sat),
                          en_kucuk_bosluk_temas_disi=sorted(diger, key=lambda q: q[2])[:8], giris_hacmi=giris[:20])
    O.kaydet(JS, OUT)
    log("S1 ozet", OUT["s1_ozet"])

# ============================================================ 2) asim ve duyarlilik (yalniz cozucu)
if ADIM in ("hepsi", "duy"):
    asim = []
    for phi in [-70, -65, -60, -55, -50] + [137.5, 140, 142.5, 145, 147.5, 150, 155, 160, 170, 180]:
        c = U.coz(RI, RO, BAG + phi, PSI_W, L, N=240)
        oz = U.ozet(c)
        h = -1.0
        try:
            kat = demet_kati(c["P"])
            h = sum(kat.common(s).Volume for a, s in KASET[:2])
        except Exception:
            pass
        asim.append(dict(phi=phi, ok=c["ok"], kaset_giris_mm3=round(h, 2), **{k: round(v, 3) for k, v in oz.items()}))
        log("asim", asim[-1])
    OUT["s1_asim"] = asim
    duy = []

    def d_(ad, phi, **kw):
        ri, ro = kw.pop("ri", RI), kw.pop("ro", RO)
        Ld = kw.pop("L", L)
        c = U.coz(ri, ro, BAG + phi, PSI_W, Ld, N=240, **kw)
        oz = U.ozet(c)
        duy.append(dict(durum=ad, phi=phi, ok=c["ok"], **{k: round(v, 3) for k, v in oz.items()}))
        log("duy", ad, phi, round(oz["R_min"], 2), round(oz["a_ic"], 1), round(oz["a_dis"], 1), c["ok"])
    for phi in (-45, 45, 135):
        for dL in (-20, -15, -10, -5, 5, 10, 15, 20):
            d_("L %+d" % dL, phi, L=L + dL)
        for a in (5, 10, 15):
            d_("tambur bagi disari %d" % a, phi, sapma_i=a)
            d_("duvar bagi ice %d" % a, phi, sapma_o=a)
        d_("ro -1 (h 31)", phi, ro=RO - 1)
        d_("ro +1 (h 33)", phi, ro=RO + 1)
        for e in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            d_("duvar eksen kacikligi %s" % (e,), phi, co=e)
        d_("serit 1,8 (demet 5,4)", phi, ri=S1["tambur"]["r"][1] + 2.7, ro=S1["duvar"]["r"][0] - 2.7)
    OUT["s1_duyarlilik"] = duy
    O.kaydet(JS, OUT)

# ============================================================ 3) S2 lopu ve dirsek lopu (bagimsiz serbest elastika)
R_LOP2 = math.hypot(GEN, 2 * T) / 2


def lop3(lt, M, tM, F, tF, ph):
    (iu, iv), iw = {"x": ((2, 1), 0), "z": ((0, 1), 2)}[lt["duzlem"]]
    Ll, N = lt["L"], len(ph)
    ds = Ll / N
    uv = np.vstack([[M[iu], M[iv]], np.array([M[iu], M[iv]]) + ds * np.cumsum(np.stack([np.cos(ph), np.sin(ph)], 1), 0)])
    s = np.linspace(0, 1, len(uv))
    if lt.get("gecis"):
        s0 = max(0.0, 1.0 - lt["gecis"] / Ll)
        tt = np.clip((s - s0) / max(1e-9, 1 - s0), 0, 1)
        w = M[iw] + (F[iw] - M[iw]) * (tt * tt * (3 - 2 * tt))
    else:
        w = M[iw] + (F[iw] - M[iw]) * s
    out = []
    for i in range(len(uv)):
        q = [0.0, 0.0, 0.0]
        q[iu], q[iv], q[iw] = float(uv[i][0]), float(uv[i][1]), float(w[i])
        out.append(V(*q))
    return out


def kirp(pts, bas=4.0, son=4.0):
    uz = np.cumsum([0] + [(b - a).Length for a, b in zip(pts[:-1], pts[1:])])
    return Part.makePolygon([p for p, u in zip(pts, uz) if bas <= u <= uz[-1] - son])


def lop_coz(lt, rel, pozlar, N=150):
    (iu, iv), iw = {"x": ((2, 1), 0), "z": ((0, 1), 2)}[lt["duzlem"]]
    F, tF = V(*lt["F"]), V(*lt["F_teget"])
    onceki, k, out = None, None, []
    for poz in pozlar:
        pl = rel(poz)
        M, tM = pl.multVec(V(*lt["M"])), pl.Rotation.multVec(V(*lt["M_teget"]))
        a0 = math.atan2(tM[iv], tM[iu])
        a1 = math.atan2(tF[iv], tF[iu])
        if onceki is None:
            th, E, h, k = U.serbest((M[iu], M[iv]), a0, (F[iu], F[iv]), a1, lt["L"], N=N)
        else:
            k = round(((onceki[-1] - onceki[0]) + a0 - a1) / (2 * math.pi))
            th, E, h, k = U.serbest((M[iu], M[iv]), a0, (F[iu], F[iv]), a1, lt["L"], N=N, th0=onceki, k=k)
        onceki = th
        Rm = (lt["L"] / N) / np.abs(np.diff(th)).max()
        out.append(dict(poz=poz, R=float(Rm), E=E, hata=h, nokta=lop3(lt, M, tM, F, tF, th)))
    return out


if ADIM in ("hepsi", "lop"):
    # dirsek lopu: F UstKol, M OnKol (Pe)
    DL = KK["dirsek_lop"]
    ALS = [2.5 * i for i in range(43)]
    dl = lop_coz(DL, O.Pe, ALS)
    ONK_AL = {}
    sat = []
    for r in dl:
        al = r["poz"]
        hed = KOL + [(a, tasi(s, O.Pe(al))) for a, s in ONK]
        d, a, b = O.enaz([("lop", kirp(r["nokta"]))], hed, pay=20)
        sat.append(dict(dirsek=al, R=round(r["R"], 3), bosluk=round(d - R_LOP2, 3), en_yakin=b, hata=r["hata"]))
    OUT["dirsek_lop"] = dict(R_min=min(q["R"] for q in sat), bosluk_min=min(sat, key=lambda q: q["bosluk"]), satir=sat,
                             R_sinir_2serit=7.5 * T + T / 2)
    log("dirsek lopu", OUT["dirsek_lop"]["R_min"], OUT["dirsek_lop"]["bosluk_min"])
    O.kaydet(JS, OUT)

    # S2 lopu: F gobek (G2), M kol (Pr); gobek cercevesi. Sabit parcalar (omuz govde, kabuk bant, kaset) S1 pozunda Pp(phi)^-1
    SL = KK["s2_lop"]
    ya = A.OMUZ["yana_aralik"]
    THS = sorted(set([ya[0], 5.5, 6.0, 7.0] + list(range(9, 121, 3)) + [ya[1]]))
    s2 = lop_coz(SL, O.Pr, THS)
    PHIS2 = list(range(-45, 136, 5))
    SABIT = GOV + BANT + KASET
    sat = []
    for r in s2:
        th = r["poz"]
        ken = kirp(r["nokta"])
        d1, _, b1 = O.enaz([("lop", ken)], GOB + [(a, tasi(s, O.Pr(th))) for a, s in KOL], pay=20)
        best = (1e9, None, None)
        for phi in PHIS2:
            kf = tasi(ken, O.Pp(phi))
            d2, _, b2 = O.enaz([("lop", kf)], SABIT, pay=20)
            if d2 < best[0]:
                best = (d2, b2, phi)
        sat.append(dict(yana=th, R=round(r["R"], 3), bosluk_gobek_kol=round(d1 - R_LOP2, 3), en_yakin_gobek_kol=b1,
                        bosluk_sabit=round(best[0] - R_LOP2, 3), en_yakin_sabit=best[1], sabit_phi=best[2], hata=r["hata"]))
        log("S2 lopu yana %5.1f R %.2f bosluk gobek/kol %.2f (%s) sabit %.2f (%s, S1 %s)  %.0fs" % (
            th, r["R"], d1 - R_LOP2, b1, best[0] - R_LOP2, best[1], best[2], time.time() - t0))
    OUT["s2_lop"] = dict(R_min=min(q["R"] for q in sat), bosluk_gobek_kol_min=min(sat, key=lambda q: q["bosluk_gobek_kol"]),
                         bosluk_sabit_min=min(sat, key=lambda q: q["bosluk_sabit"]), satir=sat, r_lop=R_LOP2)
    O.kaydet(JS, OUT)

# ============================================================ 4) gecis (G2 -> tambur bagi) ve cikis (duvar bagi -> govde ici)
if ADIM in ("hepsi", "yol"):
    sys.path.insert(0, os.path.join(O.R, "dirsek"))
    import kablo_yolu as KY            # yalniz yol TANIMI (s1_gecis / s1_cikis nokta listesi); olcum burada
    KYO = KY.s1_olcu(KK)
    g = KY.s1_gecis(KK, KYO)
    cks = KY.s1_cikis(KK, KYO)

    def boy(p):
        return sum((b - a).Length for a, b in zip(p[:-1], p[1:]))
    gk = Part.makePolygon(g)
    ya = A.OMUZ["yana_aralik"]
    res_g = []
    for th in (ya[0], 10.0, 20.0, 45.0, 90.0, 120.0):
        d, _, b = O.enaz([("g", gk)], GOB_D + [(a, tasi(s, O.Pr(th))) for a, s in KOL], pay=20)
        res_g.append(("gobek/kol S2 %g" % th, round(d, 3), b))
    gk8 = kirp(g, 0.0, 8.0)
    d, _, b = O.enaz([("g", gk8)], TAMBUR, pay=20)
    res_g.append(("tambur (son 8 mm haric)", round(d, 3), b))
    best = (1e9, None, None)
    for phi in range(-45, 136, 5):
        d, _, b = O.enaz([("g", tasi(gk, O.Pp(phi)))], GOV + BANT + KASET, pay=20)
        if d < best[0]:
            best = (d, b, phi)
    res_g.append(("sabit (govde, bant, kaset) S1 -45...135", round(best[0], 3), best[1], best[2]))
    ck = Part.makePolygon(cks)
    ck4 = kirp(cks, 4.0, 0.0)
    res_c = []
    for grp, hed in (("kaset", KASET), ("bant", BANT), ("omuz govde", GOV)):
        d, _, b = O.enaz([("c", ck4)], hed, pay=20)
        res_c.append((grp, round(d, 3), b))
    best = (1e9, None, None)
    for phi in range(-45, 136, 5):
        d, _, b = O.enaz([("c", ck4)], [(a, tasi(s, O.Pp(phi))) for a, s in GOB], pay=20)
        if d < best[0]:
            best = (d, b, phi)
    res_c.append(("gobek + tambur S1 -45...135", round(best[0], 3), best[1], best[2]))
    # yarik kabuktan gercekten acilmis mi: yarik merkezinde x boyunca isin
    C = S1["cikis"]
    y_, z_ = O.psi_yz(C["psi"], C["r_don"])
    isin = Part.makeLine(V(130, y_, z_), V(160, y_, z_))
    kes = []
    for a, s in BANT + KASET:
        if s.BoundBox.intersect(isin.BoundBox):
            c_ = s.common(isin)
            if c_.Length > 1e-6:
                kes.append((a, round(c_.Length, 3)))
    OUT["s1_yol"] = dict(gecis=dict(boy=round(boy(g), 2), mesafe=res_g, yari_kalinlik=KAL / 2, cevrel=math.hypot(GEN, KAL) / 2),
                         cikis=dict(boy=round(boy(cks), 2), mesafe=res_c, yari_kalinlik=KAL / 2, yarik_isin_kesisim=kes,
                                    nokta=[[round(q.x, 2), round(q.y, 2), round(q.z, 2)] for q in cks]))
    log("gecis", OUT["s1_yol"]["gecis"])
    log("cikis", OUT["s1_yol"]["cikis"])
    O.kaydet(JS, OUT)

OUT["sure_s"] = round(time.time() - t0, 1)
O.kaydet(JS, OUT)
log("bitti %.0fs" % (time.time() - t0))
