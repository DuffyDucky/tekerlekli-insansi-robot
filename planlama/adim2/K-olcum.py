# K kontrolu (2. adim): tasarim ajaninin (G + M1) bildirdigi degerleri MEVCUT URETILMIS GEOMETRIDEN bagimsiz olcer.
# Yalniz okur: FCStd dosyalari gecici kopyadan acilir, modul uretilmez, hicbir tasarim dosyasina yazilmaz.
# Cikti: planlama/adim2/K-olcum.json
# Calistir: FC_SCRIPT=<bu dosya> "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
# Kablo loplari: ajanin cozucusunden (kablo_yolu.elastika, Gauss-Newton) BAGIMSIZ bir cozucuyle (scipy SLSQP, farkli N,
# dal secimi enerjiyle) yeniden cozulur; bosluk FCStd'deki parcalara + (S2 lopu icin) gercek kabuk omuz bandina olculur.
import os, sys, json, math, time, shutil, tempfile, datetime
import FreeCAD as App
import Part
import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(HERE, "..", ".."))
R = os.path.join(KOK, "tasarim", "freecad")
sys.path.insert(0, R)
import arayuz as A

V = App.Vector
t0 = time.time()
OUT = dict(tarih=datetime.datetime.now().isoformat(timespec="seconds"), girdi={})


def log(*a):
    print(*a, flush=True)


def ac(rel):
    src = os.path.join(R, rel)
    for _ in range(40):
        st = os.stat(src)
        if time.time() - st.st_mtime > 5:
            break
        time.sleep(5)
    dst = os.path.join(tempfile.gettempdir(), "K_" + os.path.basename(rel))
    shutil.copy2(src, dst)
    OUT["girdi"][rel] = datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")
    d = App.openDocument(dst)
    parca = []
    for o in d.Objects:
        if o.TypeId == "Part::Feature":
            par = o.getParentGeoFeatureGroup()
            s = o.Shape.copy()
            s.Placement = o.getGlobalPlacement()
            parca.append(dict(ad=o.Label, grup=par.Name if par else "-", shape=s, kod=getattr(o, "Kod", ""), tur=getattr(o, "Tur", "")))
    App.closeDocument(d.Name)
    return parca


def bul(P, ad):
    return [p for p in P if p["ad"] == ad or p["ad"].startswith(ad)]


DIR = ac("dirsek/dirsek-montaj.FCStd")
OMU = ac("omuz/omuz-montaj.FCStd")
ISK = ac("iskelet/iskelet-montaj.FCStd")
KAB = ac("kabuk/kabuk-montaj.FCStd")
log("acildi %.1fs" % (time.time() - t0))
D = A.DIRSEK
TX, TZ = D["tup_x"], D["tup_z"]

# ====================================================================== 1) kelepce
catal = bul(DIR, "Dirsek catali")[0]["shape"]
tup = bul(OMU, "Ust kol tupu")[0]["shape"]
kel = dict()
for yk in (-118.0, -127.0, -136.0):
    ws = catal.slice(V(0, 1, 0), yk)
    yay, cizgi = {}, []
    for w in ws:
        for e in w.Edges:
            c = e.Curve
            if hasattr(c, "Radius") and math.hypot(c.Center.x - TX, c.Center.z - TZ) < 1e-3:
                yay.setdefault(round(c.Radius, 3), 0.0)
                yay[round(c.Radius, 3)] += e.Length
            elif "Line" in c.TypeId:
                p0, p1 = e.Vertexes[0].Point, e.Vertexes[-1].Point
                if abs(p0.x - p1.x) < 1e-6 and abs(p0.x - TX) < 4 and min(p0.z, p1.z) < TZ - 25:
                    cizgi.append(round(p0.x, 4))
    r_bil = min(r for r in yay if 27.5 < r < 29.5)
    acik_yay = 2 * math.pi * r_bil - yay[r_bil]
    kel[str(yk)] = dict(yarik_duz_kenar_x=sorted(set(cizgi)), yarik_mm=round(max(cizgi) - min(cizgi), 4) if len(set(cizgi)) >= 2 else None,
                        r_bilezik_ic=r_bil, ic_yay_bosluk_mm=round(acik_yay, 4), r_pim=min((r for r in yay if 24 < r < 26), default=None))
r_tup = sorted(set(round(f.Surface.Radius, 3) for f in tup.Faces if "Cylinder" in f.Surface.TypeId and
                   math.hypot(f.Surface.Center.x - TX, f.Surface.Center.z - TZ) < 1e-3 and abs(abs(f.Surface.Axis.y) - 1) < 1e-6))
k0 = kel["-127.0"]
r_to, r_ti = max(r for r in r_tup if r < 30), min(r for r in r_tup if r > 25)
g = k0["yarik_mm"]
kapanma = g / (2 * math.pi)
bosluk = (k0["r_bilezik_ic"] - r_to) + (r_ti - k0["r_pim"])
# yarik kokte (y = -140, alin kapagina bagli) kapanamaz: dogrusal kapanma dagilimi varsayimi (konsol halka) ile pime degen boy
uc_y, kok_y = -114.0, -140.0
oran_pim = bosluk / kapanma
oran_tup = (k0["r_bilezik_ic"] - r_to) / kapanma
kel_ozet = dict(kesitler=kel, r_tup_dis=r_to, r_tup_ic=r_ti, yarik_mm=g, kapanma_mm=round(kapanma, 4), toplam_bosluk_mm=round(bosluk, 4),
                on_yuk_mm=round(kapanma - bosluk, 4), sart=A.DIRSEK["bilezik_on_yuk_min"], gecti=bool(kapanma - bosluk >= A.DIRSEK["bilezik_on_yuk_min"] - 1e-6),
                dogrusal_dagilim=dict(not_="yarik y -140'ta alin kapagina bagli: kapanma kokte 0, uc (y -114) 0,637 varsayimi",
                                      tupe_degme_basi_y=round(kok_y + oran_tup * (uc_y - kok_y), 1),
                                      pime_bastirma_basi_y=round(kok_y + oran_pim * (uc_y - kok_y), 1),
                                      pime_bastiran_boy_mm=round((1 - oran_pim) * (uc_y - kok_y), 1), bilezik_boy_mm=uc_y - kok_y,
                                      civata_y=[-121.0, -132.0]))
OUT["kelepce"] = kel_ozet
log("kelepce", json.dumps(kel_ozet)[:400])


# ====================================================================== 2) M6 civata ucu: cekic somun ve kanal tabani (geometriden)
def civata_eksen(sh):
    cy = [f for f in sh.Faces if "Cylinder" in f.Surface.TypeId]
    rs = sorted(set(round(f.Surface.Radius, 3) for f in cy))
    govde = [f for f in cy if abs(f.Surface.Radius - rs[0]) < 1e-3]
    bas = [f for f in cy if abs(f.Surface.Radius - rs[-1]) < 1e-3]
    ax = V(govde[0].Surface.Axis)
    ax.normalize()
    cb = bas[0].CenterOfMass
    cg = sum((f.CenterOfMass for f in govde), V()) * (1.0 / len(govde))
    if (cg - cb).dot(ax) < 0:
        ax = ax * -1
    uc = max((v.Point - cb).dot(ax) for v in sh.Vertexes)
    p_uc = cb + ax * uc
    p_uc = p_uc + ax * 0  # eksen uzerine izdusum
    c0 = V(govde[0].Surface.Center)
    p_uc = c0 + ax * ((p_uc - c0).dot(ax))
    return p_uc, ax, cb


def isin(p, ax, sekiller, boy=30.0):
    """p'den ax yonunde ilk kati giris mesafesi (mm) ve kim."""
    e = Part.makeLine(p + ax * 0.001, p + ax * boy)
    best = (None, None)
    for ad, s in sekiller:
        if not s.BoundBox.intersect(e.BoundBox):
            continue
        c = s.common(e)
        for ed in c.Edges:
            d = min((v.Point - p).dot(ax) for v in ed.Vertexes)
            if best[0] is None or d < best[0]:
                best = (d, ad)
    return best


def m6_kontrol(civatalar, somunlar, profiller):
    out = []
    for c in civatalar:
        p, ax, cb = civata_eksen(c["shape"])
        # eslesen somun: eksene en yakin
        en = min(somunlar, key=lambda s: ((s["shape"].BoundBox.Center - p) - ax * (s["shape"].BoundBox.Center - p).dot(ax)).Length +
                 0.01 * abs((s["shape"].BoundBox.Center - p).dot(ax)))
        somun_alt = max((v.Point - cb).dot(ax) for v in en["shape"].Vertexes)
        uc = (p - cb).dot(ax)
        taban, kim = isin(p, ax, profiller)
        # civatanin profile girdigi yuz: bastan uca dogru ilk profil kesismesi
        out.append(dict(civata=c["ad"], somun=en["ad"], somun_gecme_mm=round(uc - somun_alt, 3),
                        kanal_tabani_pay_mm=None if taban is None else round(taban, 3), taban_parca=kim))
    return out


sig_omu = [(p["ad"], p["shape"]) for p in OMU if "sigma" in p["ad"].lower() or "Sigma" in p["kod"]]
m6_omu = m6_kontrol(bul(OMU, "Yuva baglanti civatasi M6"), bul(OMU, "Cekic somun M6"), sig_omu)
sig_isk = [(p["ad"], p["shape"]) for p in ISK if "sigma" in p["kod"].lower() or "sigma" in p["ad"].lower()]
m6_isk = m6_kontrol([p for p in ISK if p["ad"].startswith("Civata M6x16")], bul(ISK, "Cekic somun M6"), sig_isk)
m6_kab = m6_kontrol([p for p in KAB if p["ad"].startswith("Civata M6")], bul(KAB, "Cekic somun M6"), sig_isk)
OUT["m6"] = dict(omuz=m6_omu, iskelet=m6_isk, kabuk=m6_kab, sart_mm=0.5, profil_sayisi=dict(omuz=len(sig_omu), iskelet=len(sig_isk)))
for k, L_ in (("omuz", m6_omu), ("iskelet", m6_isk), ("kabuk", m6_kab)):
    log("M6 %s: somun gecme %s, taban %s" % (k, sorted(set(x["somun_gecme_mm"] for x in L_)), sorted(set(x["kanal_tabani_pay_mm"] for x in L_))))

# ====================================================================== 3) kabuk cam - duvar
nx = bul(KAB, "Nextion")[0]["shape"]
duz = sorted([f for f in nx.Faces if "Plane" in f.Surface.TypeId], key=lambda f: -f.Area)
# en buyuk iki paralel duzlem: on (cam) ve arka (PCB) yuzu; PCB arka yuzu: alani daha buyuk (258x152) olan
arka = max(duz[:6], key=lambda f: f.Area)
n_ic = arka.normalAt(0, 0) * -1                      # arka yuzden govdeye dogru
pcb = arka.extrude(n_ic * (A.NEXTION["pcb"][2] + 0.05))
cam = nx.cut(pcb)
bantlar = [p for p in KAB if p["ad"].startswith("Omuz bandi") or p["ad"].startswith("Gogus bandi") or p["ad"].startswith("Govde")]
camd = sorted([(round(cam.distToShape(p["shape"])[0], 4), p["ad"]) for p in bantlar if p["shape"].BoundBox.intersect(cam.BoundBox) or True])[:4]
nxd = sorted([(round(nx.distToShape(p["shape"])[0], 4), p["ad"]) for p in bantlar])[:4]
OUT["kabuk_cam"] = dict(cam_en_yakin=camd, nextion_tum_en_yakin=nxd, pcb_arka_alan=round(arka.Area, 1), cam_hacim=round(cam.Volume, 1))
log("cam", camd, "nextion", nxd)

# ====================================================================== 4) gecitler
ws = catal.slice(V(0, 1, 0), -142.0)
r_del = min((e.Curve.Radius for w in ws for e in w.Edges if hasattr(e.Curve, "Radius") and math.hypot(e.Curve.Center.x - TX, e.Curve.Center.z - TZ) < 1e-3),
            default=None)
JR = A.KOL_KABLO["jr_disi"]
# tup penceresi: tupun arka duvarinda (z < -20) x-y duzleminde delik; pencereyi z = -26,9 (duvar ortasi) kesitinden olc
pw = tup.slice(V(0, 0, 1), TZ - 26.8)
pen = []
for w in pw:
    bb = w.BoundBox
    if bb.XLength < 20 and bb.YLength < 40:
        pen.append([round(bb.XMin, 2), round(bb.XMax, 2), round(bb.YMin, 2), round(bb.YMax, 2)])
# pencerenin duz bolumunde en dar x genisligi
duz_g = None
if pen:
    x0, x1, y0, y1 = pen[0]
    w_ = [w for w in pw if w.BoundBox.XLength < 20 and w.BoundBox.YLength < 40][0]
    f_ = Part.Face(w_)
    ys = np.linspace(y0 + 0.2, y1 - 0.2, 60)
    gen = []
    for yy in ys:
        l = Part.makeLine(V(x0 - 1, yy, TZ - 26.8), V(x1 + 1, yy, TZ - 26.8)).common(f_)
        gen.append((round(yy, 2), round(sum(e.Length for e in l.Edges), 3)))
    duz = [y for y, gg in gen if gg >= JR[0] + 0.5]
    duz_g = dict(jr_gecen_boy_mm=round(max(duz) - min(duz), 2) if duz else 0.0, en_genis_mm=max(gg for _, gg in gen))
tup_ic = r_ti * 2
EJ = A.KOL_KABLO["jr_eslesik"]
OUT["gecit"] = dict(catal_delik_cap=None if r_del is None else round(2 * r_del, 3), jr_kosegen=round(math.hypot(JR[0], JR[1]), 3),
                    delik_pay=None if r_del is None else round(2 * r_del - math.hypot(JR[0], JR[1]), 3), tup_pencere_kutusu=pen, tup_pencere=duz_g,
                    tup_ic_cap=tup_ic, iki_eslesik_jr_kosegen=round(math.hypot(EJ[0], 2 * EJ[1]), 2))
log("gecit", OUT["gecit"])

# ====================================================================== 5) kablo loplari (bagimsiz cozucu)
KK = A.KOL_KABLO
XR = 185.0


def Pp(phi):
    return App.Placement(V(0, 0, 0), App.Rotation(V(-1, 0, 0), phi), V(0, 0, 0))


def Pr(th):
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th), V(XR, 0, 0))


def Pe(al):
    return App.Placement(V(0, 0, 0), App.Rotation(V(*D["eksen_yon"]), al), V(0, D["eksen_y"], D["eksen_z"]))


def tasi(s, pl):
    s = s.copy()
    s.transformShape(pl.toMatrix(), True)
    return s


def coz(p0, a0, p1, a1, L, N, phi0=None, k=None):
    """Bagimsiz ayrik elastika: N parca acisi phi; phi[0] = a0, phi[N-1] = a1 + 2 pi k; enerji sum dphi^2; uc kisiti."""
    ds = L / N
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]

    def tam(x, b):
        return np.concatenate([[a0], x, [b]])

    def cozk(kk, x0):
        b = a1 + 2 * math.pi * kk

        def f(x):
            ph = tam(x, b)
            d = np.diff(ph)
            return float(d @ d)

        def gf(x):
            ph = tam(x, b)
            d = np.diff(ph)
            gr = np.zeros(N)
            gr[:-1] -= 2 * d
            gr[1:] += 2 * d
            return gr[1:-1]

        cons = [dict(type="eq", fun=lambda x: ds * np.cos(tam(x, b)).sum() - dx, jac=lambda x: -ds * np.sin(tam(x, b))[1:-1]),
                dict(type="eq", fun=lambda x: ds * np.sin(tam(x, b)).sum() - dy, jac=lambda x: ds * np.cos(tam(x, b))[1:-1])]
        r = minimize(f, x0, jac=gf, constraints=cons, method="SLSQP", options=dict(maxiter=2000, ftol=1e-12))
        ph = tam(r.x, b)
        hata = math.hypot(ds * np.cos(ph).sum() - dx, ds * np.sin(ph).sum() - dy)
        return ph, r.fun, hata < 1e-6
    if phi0 is not None:
        b = a1 + 2 * math.pi * k
        x0 = phi0[1:-1] + np.linspace(0, 1, N)[1:-1] * (b - phi0[-1]) + (a0 - phi0[0]) * (1 - np.linspace(0, 1, N)[1:-1])
        ph, E, ok = cozk(k, x0)
        return ph, E, ok, k
    best = None
    for kk in (-1, 0, 1):
        b = a1 + 2 * math.pi * kk
        for bombe in (-2.5, -1.2, 0.0, 1.2, 2.5):
            s = np.linspace(0, 1, N)
            x0 = (a0 + (b - a0) * s + bombe * np.sin(math.pi * s))[1:-1]
            ph, E, ok = cozk(kk, x0)
            if ok and (best is None or E < best[1]):
                best = (ph, E, ok, kk)
    return best


def nokta3(lt, M, F, ph, L, N):
    (iu, iv), iw = {"x": ((2, 1), 0), "z": ((0, 1), 2)}[lt["duzlem"]]
    ds = L / N
    uv = np.vstack([[M[iu], M[iv]], np.array([M[iu], M[iv]]) + ds * np.cumsum(np.stack([np.cos(ph), np.sin(ph)], 1), 0)])
    s = np.linspace(0, 1, len(uv))
    if lt.get("gecis"):
        s0 = max(0.0, 1.0 - lt["gecis"] / L)
        t = np.clip((s - s0) / max(1e-9, 1 - s0), 0, 1)
        w = M[iw] + (F[iw] - M[iw]) * (t * t * (3 - 2 * t))
    else:
        w = M[iw] + (F[iw] - M[iw]) * s
    out = []
    for i in range(len(uv)):
        q = [0.0, 0.0, 0.0]
        q[iu], q[iv], q[iw] = float(uv[i][0]), float(uv[i][1]), float(w[i])
        out.append(V(*q))
    return out


def kirp(pts, bas, son):
    uz = np.cumsum([0] + [(b - a).Length for a, b in zip(pts[:-1], pts[1:])])
    q = [p for p, u in zip(pts, uz) if bas <= u <= uz[-1] - son]
    return Part.makePolygon(q)


def lop(ad, lt, rel, pozlar, sekiller, N=150, L=None, M_aci=0.0, olc=True):
    (iu, iv), iw = {"x": ((2, 1), 0), "z": ((0, 1), 2)}[lt["duzlem"]]
    L = L or lt["L"]
    F, tF = V(*lt["F"]), V(*lt["F_teget"])
    r_lop = math.hypot(KK["serit"][0], lt["serit"] * KK["serit"][1]) / 2
    sat, onceki = [], None
    for poz in pozlar:
        pl = rel(poz)
        M, tM = pl.multVec(V(*lt["M"])), pl.Rotation.multVec(V(*lt["M_teget"]))
        a0 = math.atan2(tM[iv], tM[iu]) + math.radians(M_aci)
        a1 = math.atan2(tF[iv], tF[iu])
        if onceki is None:
            ph, E, ok, k = coz((M[iu], M[iv]), a0, (F[iu], F[iv]), a1, L, N)
        else:
            # dal surekliligi: toplam donus onceki pozdakine en yakin k
            d_on = onceki[-1] - onceki[0]
            k = round(((d_on + a0) - a1) / (2 * math.pi))
            ph, E, ok, k = coz((M[iu], M[iv]), a0, (F[iu], F[iv]), a1, L, N, phi0=onceki, k=k)
        onceki = ph
        dph = np.abs(np.diff(ph)).max()
        r_min = (L / N) / dph if dph > 1e-12 else 1e9
        rec = dict(poz=poz, r_min=round(r_min, 2), enerji=round(E, 4), yakinsadi=bool(ok), k=int(k), toplam_donus_derece=round(math.degrees(ph[-1] - ph[0]), 1))
        if olc:
            pts = nokta3(lt, M, F, ph, L, N)
            kenar = kirp(pts, 4.0, 4.0)
            bb = App.BoundBox(kenar.BoundBox)
            bb.enlarge(30)
            best = (1e9, None)
            for a_, s_ in sekiller(poz):
                if not s_.BoundBox.intersect(bb):
                    continue
                dd = s_.distToShape(kenar)[0]
                if dd < best[0]:
                    best = (dd, a_)
            rec.update(bosluk=round(best[0] - r_lop, 2), en_yakin=best[1])
            rec["uzak_mm"] = round(max(((p - F).Length) for p in pts), 1)
        sat.append(rec)
    r = dict(ad=ad, L=L, M_aci_sapma=M_aci, N=N, r_min=min(s["r_min"] for s in sat), r_min_poz=min(sat, key=lambda s: s["r_min"])["poz"],
             yakinsadi=all(s["yakinsadi"] for s in sat), pozlar=sat)
    if olc:
        b = min(sat, key=lambda s: s["bosluk"])
        r.update(en_kucuk_bosluk=b["bosluk"], en_yakin=b["en_yakin"], en_yakin_poz=b["poz"])
    return r


def grup(P, g):
    return [(p["ad"], p["shape"]) for p in P if p["grup"] == g]


UST = grup(DIR, "UstKol") + grup(OMU, "Kol")
ONK = grup(DIR, "OnKol") + grup(DIR, "El")
_onk = {}


def onk(al):
    if al not in _onk:
        _onk[al] = [(a, tasi(s, Pe(al))) for a, s in ONK]
    return _onk[al]


DL = KK["dirsek_lop"]
ar = D["aralik"]
AL = [ar[0] + 2.5 * i for i in range(int(round((ar[1] - ar[0]) / 2.5)) + 1)]
lop_d = lop("dirsek lopu", DL, Pe, AL, lambda al: UST + onk(al))
log("dirsek lopu: R_min %.2f (poz %s), bosluk %.2f (%s, %s)" % (lop_d["r_min"], lop_d["r_min_poz"], lop_d["en_kucuk_bosluk"], lop_d["en_yakin"], lop_d["en_yakin_poz"]))

# S2 lopu: gobek cercevesi. Govde (omuz + GERCEK kabuk omuz bandi sag) S1 pozlarinda Pp(phi)^-1
SL = KK["s2_lop"]
GOB = grup(OMU, "Gobek")
govde_omu = [(a, s) for a, s in grup(OMU, "Govde") if "referans" not in a.lower()]
oy = A.MODULLER["omuz_sag"]["konum"] if "omuz_sag" in A.MODULLER else (0.0, 955.0, 0.0)
kab_yer = [(p["ad"], tasi(p["shape"], App.Placement(V(-oy[0], -oy[1], -oy[2]), App.Rotation()))) for p in KAB
           if p["ad"].startswith("Omuz bandi sag") or p["ad"].startswith("Gogus bandi sag")]
GOV = []
for phi in range(-45, 136, 15):
    inv = Pp(phi).inverse()
    GOV += [("%s (S1 %d)" % (a, phi), tasi(s, inv)) for a, s in govde_omu + kab_yer]
KOLG = grup(OMU, "Kol") + grup(DIR, "UstKol")
_kol = {}


def kolp(th):
    if th not in _kol:
        _kol[th] = [(a, tasi(s, Pr(th))) for a, s in KOLG]
    return _kol[th]


ya = A.OMUZ["yana_aralik"]
TH = sorted(set([ya[0]] + list(range(6, int(ya[1]) + 1, 3)) + [ya[1]]))
lop_s2 = lop("S2 lopu", SL, Pr, TH, lambda th: GOB + GOV + kolp(th))
log("S2 lopu: R_min %.2f (poz %s), bosluk %.2f (%s, %s)" % (lop_s2["r_min"], lop_s2["r_min_poz"], lop_s2["en_kucuk_bosluk"], lop_s2["en_yakin"], lop_s2["en_yakin_poz"]))

# duyarlilik (yalniz R_min): L +-10, M cikis tegeti +-15 derece
duy = []
for ad, lt, rel, poz in (("dirsek", DL, Pe, AL[::2]), ("S2", SL, Pr, TH[::2])):
    for dL, da in ((-10, 0), (10, 0), (0, -15), (0, 15)):
        r = lop(ad, lt, rel, poz, None, L=lt["L"] + dL, M_aci=da, olc=False)
        duy.append(dict(lop=ad, L=lt["L"] + dL, M_aci=da, r_min=r["r_min"], poz=r["r_min_poz"], yakinsadi=r["yakinsadi"]))
        log("duyarlilik", duy[-1])
t_ = KK["serit"][1]
OUT["kablo"] = dict(
    dirsek_lop=lop_d, s2_lop=lop_s2, duyarlilik=duy,
    sinir=dict(r_7_5d_2serit=7.5 * t_ + t_ / 2, r_10d_2serit=10 * t_ + t_ / 2, r_7_5d_kalin_1_8=7.5 * 1.8 + 0.9,
               not_="2 serit demet: merkez cizgisi sinir = kat x t + (n-1) t / 2"),
    kabuk_gercek_dahil="S2 lopu govde listesinde kabuk omuz bandi sag + gogus bandi sag (global -> omuz yereli), S1 -45...135 (15)")

# ====================================================================== 6) boy (arayuz yol noktalari + uclarin geometriye oturmasi)
def boy(nokta):
    return sum((V(*b) - V(*a)).Length for a, b in zip(nokta[:-1], nokta[1:]))


ds_ = boy(KK["yol_dirsek_servo"]["nokta"])
bs_ = boy(KK["yol_bilek_servo"]["nokta"])
us_ = boy(KK["yol_ustkol"]["nokta"])
serv = {p["ad"]: p["shape"] for p in DIR if p["ad"] in ("Dirsek servosu MG996R", "Bilek servosu MG996R")}
cik_d = serv["Dirsek servosu MG996R"].distToShape(Part.Vertex(V(*KK["yol_dirsek_servo"]["nokta"][0])))[0]
cik_b = serv["Bilek servosu MG996R"].distToShape(Part.Vertex(V(*KK["yol_bilek_servo"]["nokta"][0])))[0]
OUT["boy"] = dict(dirsek_gerek=round(ds_ + DL["L"] + us_, 1), bilek_gerek=round(bs_ + DL["L"] + us_, 1),
                  dirsek_artan=round(300 - (ds_ + DL["L"] + us_), 1), bilek_artan=round(300 - (bs_ + DL["L"] + us_), 1),
                  jr_govde_dusulunce=dict(dirsek=round(300 - 14 - (ds_ + DL["L"] + us_), 1), bilek=round(300 - 14 - (bs_ + DL["L"] + us_), 1)),
                  cikis_noktasi_servoya_uzaklik=dict(dirsek=round(cik_d, 2), bilek=round(cik_b, 2)))
log("boy", OUT["boy"])
OUT["sure_s"] = round(time.time() - t0, 1)
json.dump(OUT, open(os.path.join(HERE, "K-olcum.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("bitti %.1fs" % (time.time() - t0))
