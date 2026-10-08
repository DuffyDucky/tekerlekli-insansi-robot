# Sag dirsek modulu - montaj, kontroller, dirsek ici tarama, tork, baski analizi, FCStd + STEP + BOM + analiz json
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
# Kontroller: her parca isValid + tek kati; ev pozunda modul ici cakisma (0,5 mm3); omuz Kol grubuyla arayuz (tup);
# baglantilar (dayanma, eksen hizasi, civata ucu payi / kavrama); dirsek ici tarama (dirsek acisi x bilek acisi x parca
# ciftleri); tork (gercek parca kutleleri + el ucunda 0,5 kg; dirsek, bilek, omuz S1/S2); X2D baski analizi.
# Moduller arasi carpisma ve ana montaj 2. asamada (carpisma.py, montaj/), bu betik onlara dokunmaz.
import os, sys, json, math, time, csv
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "omuz")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import dirsek_parcalar as DP
from dirsek_parcalar import V, P, BAG, MG, D, Pp, Pr, Pe, Pb, grup_yer, ALS, BES, YE, ZE, XW, XR
import dirsek_lib as L
import arayuz as A
import omuz_parcalar as O

t0 = time.time()
TOL = 0.5          # mm3
TEMAS = 0.01       # mm


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))


log("dirsek parca", len(P), "omuz parca", len(O.P))
# omuz arayuz olculeri degismemis olmali
assert abs(O.XR - A.DIRSEK["tup_x"]) < 1e-9 and abs(O.ZC - A.DIRSEK["tup_z"]) < 1e-9
TUP = next(q for q in O.P if q["ad"] == "Ust kol tupu")
assert abs(TUP["bb"].YMin - A.DIRSEK["tup_uc_y"]) < 1e-6, TUP["bb"].YMin
OMUZ_KOL = [q for q in O.P if q["grup"] == "Kol"]


def kes(a, b, abb=None, bbb=None):
    abb = abb or a.BoundBox
    bbb = bbb or b.BoundBox
    if not abb.intersect(bbb):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def tasi(shape, pl):
    s = shape.copy()
    s.transformShape(pl.toMatrix())
    return s


def mesafe(a, b):
    return a.distToShape(b)[0]


# ====================================================================== 1) gecerlilik + ev pozu modul ici cakisma
gecersiz = [p["ad"] for p in P if not p["shape"].isValid()]
coklu = [(p["ad"], p["kati"]) for p in P if p["kati"] != 1]
statik, n_cift = [], 0
for i in range(len(P)):
    for j in range(i + 1, len(P)):
        a, b = P[i], P[j]
        if not a["bb"].intersect(b["bb"]):
            continue
        n_cift += 1
        v = kes(a["shape"], b["shape"], a["bb"], b["bb"])
        if v > TOL or v < 0:
            statik.append((a["ad"], b["ad"], round(v, 3)))
log("gecersiz", len(gecersiz), "coklu", len(coklu), "ev pozu cakisma", len(statik), "cift", n_cift)

# ====================================================================== 2) omuz arayuzu (ev pozu): dirsek x omuz Kol grubu
arayuz_cak = []
for p in P:
    for q in OMUZ_KOL:
        v = kes(p["shape"], q["shape"], p["bb"], q["bb"])
        if v > TOL or v < 0:
            arayuz_cak.append((p["ad"], q["ad"], round(v, 3)))
catal = P[DP.I_CATAL]["shape"]
tup = TUP["shape"]
ara = []
d = mesafe(catal, tup)
ara.append(("tup ucu catalin alin kapagina dayali", round(d, 4), d <= TEMAS))
# radyal bosluklar: y = -128 kesitindeki daire yaylarinin yaricaplari (tup ekseni etrafinda)
kes_y = -128.0
yaricap = []
for w in catal.slice(V(0, 1, 0), kes_y):
    for e in w.Edges:
        cv = e.Curve
        if hasattr(cv, "Radius") and math.hypot(cv.Center.x - DP.TX, cv.Center.z - DP.TZ) < 1e-6:
            yaricap.append(cv.Radius)
r_pim = max(r for r in yaricap if r < 26.5)
r_bil = min(r for r in yaricap if 27.0 < r < 29.0)
ara.append(("pim - tup ic yuzu radyal bosluk %.2f mm (sikma bilezigi tupu pime bastirir)" % (A.DIRSEK["tup_ri"] - r_pim),
            round(A.DIRSEK["tup_ri"] - r_pim, 3), 0.0 < A.DIRSEK["tup_ri"] - r_pim <= 0.2))
ara.append(("bilezik ic yuzu - tup dis yuzu radyal bosluk %.2f mm" % (r_bil - A.DIRSEK["tup_ro"]),
            round(r_bil - A.DIRSEK["tup_ro"], 3), 0.0 < r_bil - A.DIRSEK["tup_ro"] <= 0.2))
ara.append(("pim tupe giris boyu %.1f mm" % (catal.BoundBox.YMax - A.DIRSEK["tup_uc_y"]),
            round(catal.BoundBox.YMax - A.DIRSEK["tup_uc_y"], 2), catal.BoundBox.YMax - A.DIRSEK["tup_uc_y"] >= 20.0))
log("omuz arayuzu cakisma", len(arayuz_cak), [x[:2] for x in ara])


# ====================================================================== 3) baglanti kontrolleri
def eksen_disi(sh, nokta, yon):
    c = sh.BoundBox.Center
    dd = c - V(*nokta)
    u = V(*yon)
    u.normalize()
    return (dd - u * dd.dot(u)).Length


def t_aralik(sh, nokta, yon):
    u = V(*yon)
    u.normalize()
    ts = [(v.Point - V(*nokta)).dot(u) for v in sh.Vertexes]
    return min(ts), max(ts)


def S(i):
    return P[i]["shape"]


bag_kontrol = []
for b in BAG:
    k = []
    civ = S(b["civata"])
    n0, u = b["nokta"], b["yon"]
    d_ = b["d"]
    ed = eksen_disi(civ, n0, u)
    k.append(("civata ekseni tasarim ekseninde", round(ed, 6), ed < 1e-6))
    _, t_uc = t_aralik(civ, n0, u)
    if b["tip"] in ("civata_somun", "servo_kulak"):
        som = S(b["somun"])
        ed2 = eksen_disi(som, n0, u)
        k.append(("somun ayni eksende", round(ed2, 6), ed2 < 1e-6))
        _, t_som = t_aralik(som, n0, u)
        cik = t_uc - t_som
        k.append(("civata ucu kontra somundan %.1f mm tasiyor (>= 0,5; naylon halka tam kavrar)" % cik, round(cik, 3), 0.5 <= cik <= 6.0))
        if b["tip"] == "civata_somun":
            dp1 = mesafe(S(b["pul_bas"]), S(b["govde"]))
            dp2 = mesafe(S(b["pul_somun"]), S(b["govde"]))
            dh = mesafe(civ, S(b["pul_bas"]))
            ds = mesafe(som, S(b["pul_somun"]))
            k += [("bas pulu kulaga dayali", round(dp1, 4), dp1 <= TEMAS), ("civata basi pula dayali", round(dh, 4), dh <= TEMAS),
                  ("somun pulu kulaga dayali", round(dp2, 4), dp2 <= TEMAS), ("somun pula dayali", round(ds, 4), ds <= TEMAS)]
            dg = mesafe(civ, S(b["govde"]))
            k.append(("civata govdesi delikte ortali (delik duvarina %.2f mm)" % dg, round(dg, 3),
                      abs(dg - (A.CLEAR[d_] - d_) / 2) < 0.02))
        else:
            dh = mesafe(civ, S(b["servo"]))
            dn = mesafe(som, S(b["govde"]))
            dsv = mesafe(S(b["servo"]), S(b["govde"]))
            k += [("civata basi servo kulagina dayali", round(dh, 4), dh <= TEMAS),
                  ("somun plakaya dayali", round(dn, 4), dn <= TEMAS),
                  ("servo kulagi plakaya dayali", round(dsv, 4), dsv <= TEMAS)]
            dg = mesafe(civ, S(b["govde"]))
            k.append(("civata plaka deliginde ortali (%.2f mm)" % dg, round(dg, 3), abs(dg - (A.CLEAR[d_] - d_) / 2) < 0.02))
    elif b["tip"] == "civata_horn":
        hrn = S(b["horn"])
        dh = mesafe(civ, S(b["govde"]))
        k.append(("civata basi parcaya dayali", round(dh, 4), dh <= TEMAS))
        ix = 0 if abs(u[0]) > 0.5 else 1

        def tp(duz):                              # eksen dogrultusunda duzlem konumu (bas alt yuzunden)
            return (duz - n0[ix]) * u[ix]
        t_yak, t_uzak = tp(b["horn_yuz"][0]), tp(b["horn_yuz"][1])
        kav = min(t_uc, t_uzak) - t_yak
        k.append(("horn disine kavrama %.1f mm (horn %.1f)" % (kav, t_uzak - t_yak), round(kav, 3), kav >= 2.5))
        t_kasa = tp(b["kasa"])
        k.append(("civata ucundan servo kasasina %.1f mm" % (t_kasa - t_uc), round(t_kasa - t_uc, 3), t_kasa - t_uc >= 1.0))
        dho = mesafe(hrn, S(b["govde"]))
        k.append(("horn parcaya dayali", round(dho, 4), dho <= TEMAS))
    elif b["tip"] == "pim":
        ins = S(b["insert"])
        L_ins = A.INSERT[d_][1]
        kav = t_uc - (b["agiz"] - n0[0])
        k.append(("M5 kavramasi %.1f mm (isil gomme somun %.1f)" % (kav, L_ins), round(kav, 3), d_ <= kav <= L_ins))
        for ad_, sh_ in (("625ZZ ic bilezik", S(b["rul_i"])), ("625ZZ dis bilezik", S(b["rul_d"])), ("isil gomme somun", ins),
                         ("pul", S(b["pul"]))):
            e_ = eksen_disi(sh_, n0, u)
            k.append(("%s dirsek ekseninde" % ad_, round(e_, 6), e_ < 1e-6))
        dl = [("pul 625ZZ ic bilezigine dayali", mesafe(S(b["pul"]), S(b["rul_i"]))),
              ("civata basi pula dayali", mesafe(civ, S(b["pul"]))),
              ("625ZZ ic bilezik on koldaki dayamaya dayali", mesafe(S(b["rul_i"]), S(b["govde"]))),
              ("625ZZ dis bilezik catal yuvasinda (dudaga dayali)", mesafe(S(b["rul_d"]), S(b["catal"]))),
              ("isil gomme somun yanakta oturuyor", mesafe(ins, S(b["govde"])))]
        k += [(a_, round(x_, 4), x_ <= TEMAS) for a_, x_ in dl]
        # bagil hareket: on kola bagli parcalar catala, catala bagli parcalar on kola degmemeli
        dx = [("pim civatasi catala degmiyor", mesafe(civ, S(b["catal"]))),
              ("pul catala degmiyor", mesafe(S(b["pul"]), S(b["catal"]))),
              ("625ZZ ic bilezik catala degmiyor", mesafe(S(b["rul_i"]), S(b["catal"]))),
              ("625ZZ dis bilezik on kola degmiyor", mesafe(S(b["rul_d"]), S(b["govde"]))),
              ("on kol catala degmiyor", mesafe(S(b["govde"]), S(b["catal"])))]
        k += [(a_ + " (%.2f mm)" % x_, round(x_, 3), x_ >= 0.3) for a_, x_ in dx]
    elif b["tip"] == "radyal":
        ins = S(b["insert"])
        L_ins = A.INSERT[d_][1]
        kav = t_uc                                 # nokta = isil gomme somun agzi (flans yuzu)
        k.append(("M3 kavramasi %.1f mm (isil gomme somun %.1f)" % (kav, L_ins), round(kav, 3), d_ <= kav <= L_ins))
        e_ = eksen_disi(ins, n0, u)
        k.append(("isil gomme somun civata ekseninde", round(e_, 6), e_ < 1e-6))
        dl = [("civata basi yakaya dayali", mesafe(civ, S(b["govde"]))), ("isil gomme somun flansta oturuyor", mesafe(ins, S(b["flans"])))]
        k += [(a_, round(x_, 4), x_ <= TEMAS) for a_, x_ in dl]
    bag_kontrol.append(dict(ad=b["ad"], tip=b["tip"], kontroller=k, tamam=all(x[2] for x in k)))

# eksen hizasi: servo milleri, yatak ve eklem eksenleri
eks = []
dome_e = next(p for p in P if p["ad"] == "Dirsek servosu cikis mili")["shape"]
dome_b = next(p for p in P if p["ad"] == "Bilek servosu cikis mili")["shape"]
e1 = eksen_disi(dome_e, A.DIRSEK["eksen_nokta"], A.DIRSEK["eksen_yon"])
e2 = eksen_disi(P[DP.I_RUL_D]["shape"], A.DIRSEK["eksen_nokta"], A.DIRSEK["eksen_yon"])
e3 = eksen_disi(dome_b, A.DIRSEK["bilek_nokta"], A.DIRSEK["bilek_yon"])
e4 = eksen_disi(P[DP.I_HORN_B]["shape"], A.DIRSEK["bilek_nokta"], A.DIRSEK["bilek_yon"])
eks += [("dirsek servosu mili = arayuz dirsek ekseni", round(e1, 6), e1 < 1e-6),
        ("625ZZ (karsi yatak) = dirsek ekseni (servo mili ile ayni eksen)", round(e2, 6), e2 < 1e-6),
        ("bilek servosu mili = arayuz bilek ekseni", round(e3, 6), e3 < 1e-6),
        ("bilek horn = bilek ekseni", round(e4, 6), e4 < 1e-6)]
dfl = mesafe(P[DP.I_FLANS]["shape"], P[DP.I_HORN_B]["shape"])
del_ = mesafe(P[DP.I_EL]["shape"], P[DP.I_FLANS]["shape"])
eks += [("bilek flansi horn'a dayali", round(dfl, 4), dfl <= TEMAS), ("el yakasi flansa oturmus", round(del_, 4), del_ <= TEMAS)]
bag_kontrol.append(dict(ad="Eksen hizasi ve oturmalar", tip="eksen", kontroller=eks, tamam=all(x[2] for x in eks)))
log("baglanti kontrol %d/%d tamam" % (sum(1 for s in bag_kontrol if s["tamam"]), len(bag_kontrol)))
for s in bag_kontrol:
    if not s["tamam"]:
        log("  HATA", s["ad"], [x for x in s["kontroller"] if not x[2]])

# ====================================================================== 4) dirsek ici tarama
UST_SET = [dict(ad=p["ad"], shape=p["shape"], bb=p["bb"], kaynak="dirsek") for p in P if p["grup"] == "UstKol"] + \
          [dict(ad=q["ad"] + " (omuz)", shape=q["shape"], bb=q["bb"], kaynak="omuz") for q in OMUZ_KOL]
ONK = [p for p in P if p["grup"] == "OnKol"]
ELP = [p for p in P if p["grup"] == "El"]


def carp(hareketli, pl, sabit):
    hits = []
    for a in hareketli:
        sa = tasi(a["shape"], pl)
        ba = sa.BoundBox
        for b in sabit:
            if not ba.intersect(b["bb"]):
                continue
            v = kes(sa, b["shape"], ba, b["bb"])
            if v > TOL or v < 0:
                hits.append((a["ad"], b["ad"], round(v, 1)))
    return hits


onkol_ust = {al: carp(ONK, Pe(al), UST_SET) for al in ALS}
log("on kol x ust kol bitti")
BES_K = [-90, -45, 0, 45, 90]
el_ust = {(al, be): carp(ELP, Pe(al).multiply(Pb(be)), UST_SET) for al in ALS for be in BES_K}
log("el x ust kol bitti")
ONK_SET = [dict(ad=p["ad"], shape=p["shape"], bb=p["bb"]) for p in ONK]
el_onkol = {be: carp(ELP, Pb(be), ONK_SET) for be in BES}
log("el x on kol bitti")


def serbest(al):
    return not onkol_ust[al] and all(not el_ust[(al, be)] for be in BES_K)


amax = 0
for al in [a for a in ALS if a >= 0]:
    if serbest(al):
        amax = al
    else:
        break
amin = 0
for al in sorted([a for a in ALS if a <= 0], reverse=True):
    if serbest(al):
        amin = al
    else:
        break
bilek_serbest = all(not v for v in el_onkol.values())
ilk_carpan = {}
for al in ALS:
    if al > amax and onkol_ust[al]:
        ilk_carpan["+"] = (al, onkol_ust[al][:4])
        break
for al in sorted(ALS, reverse=True):
    if al < amin and onkol_ust[al]:
        ilk_carpan["-"] = (al, onkol_ust[al][:4])
        break
ar = A.DIRSEK["aralik"]
log("dirsek serbest aralik %d...%d, arayuz %s, bilek serbest %s" % (amin, amax, ar, bilek_serbest), ilk_carpan)


# eklem ekseni uzerindeki es eksenli elemanlar (bagil donerken temas tasarim geregi): bosluk olcumune katilmaz
EKSENEL = {("Dirsek servosu cikis mili", "Dirsek horn merkez vidasi M3"), ("Dirsek servosu cikis mili", "Dirsek horn 25T aluminyum disk"),
           ("625ZZ rulman (ic bilezik)", "625ZZ rulman (dis bilezik)")}


def min_bosluk(al, be=0.0):
    best = (1e9, None, None)
    for grp, pl in ((ONK, Pe(al)), (ELP, Pe(al).multiply(Pb(be)))):
        for a in grp:
            sa = tasi(a["shape"], pl)
            ba = sa.BoundBox
            ba.enlarge(25)
            for b in UST_SET:
                if not ba.intersect(b["bb"]) or (a["ad"], b["ad"]) in EKSENEL:
                    continue
                dd = mesafe(sa, b["shape"])
                if dd < best[0]:
                    best = (dd, a["ad"], b["ad"])
    return [round(best[0], 2), best[1], best[2]]


bosluk = {str(al): min_bosluk(al) for al in sorted(set([0, int(ar[0]), int(ar[1]), amin, amax]))}
log("bosluklar", bosluk)
# bukulme boslugu: on kol + el ile ust kolun dirsek ekseninden uzak bolumu (catal koprusu/kapak/bilezik, y >= -149, ve tup)
UST_BOLGE = Part.makeBox(200, 60, 200, V(80, -149.0, -100))
UST_UST = []
for b in UST_SET:
    if b["bb"].YMax < -149.0:
        continue
    sh = b["shape"].common(UST_BOLGE) if b["bb"].YMin < -149.0 else b["shape"]
    if sh.Volume > 1e-6:
        UST_UST.append(dict(ad=b["ad"], shape=sh, bb=sh.BoundBox))


def bukulme_boslugu(al):
    best = (1e9, None, None)
    for grp, pl in ((ONK, Pe(al)), (ELP, Pe(al))):
        for a in grp:
            sa = tasi(a["shape"], pl)
            ba = sa.BoundBox
            ba.enlarge(30)
            for b in UST_UST:
                if not ba.intersect(b["bb"]):
                    continue
                dd = mesafe(sa, b["shape"])
                if dd < best[0]:
                    best = (dd, a["ad"], b["ad"])
    return [round(best[0], 2), best[1], best[2]]


bukulme = {str(al): bukulme_boslugu(al) for al in range(80, amax + 1, 5)}
log("bukulme boslugu", bukulme)
aralik_ok = amin <= ar[0] and ar[1] <= amax and bukulme.get(str(int(ar[1])), [0])[0] >= 3.0

# ====================================================================== 5) tork (kg*cm = g*mm / 10000)
GR = {}
for g in ("UstKol", "OnKol", "El"):
    m = sum(p["kutle"] for p in P if p["grup"] == g)
    c = V(0, 0, 0)
    for p in P:
        if p["grup"] == g:
            c = c + p["merkez"] * (p["kutle"] / m)
    GR[g] = (m, c)
for g in ("Gobek", "Kol"):
    m = sum(q["kutle"] for q in O.P if q["grup"] == g)
    c = V(0, 0, 0)
    for q in O.P:
        if q["grup"] == g:
            c = c + q["merkez"] * (q["kutle"] / m)
    GR["omuz_" + g] = (m, c)
YUK = A.DIRSEK["yuk_g"]


def tork(phi, th, al, be):
    """Isaretli torklar (g*mm): yuksuz ve 1 g'lik el ucu yuku icin [S1, S2, dirsek, bilek]."""
    T_g = Pp(phi)
    T_k = Pp(phi).multiply(Pr(th))
    T_o = T_k.multiply(Pe(al))
    T_e = T_o.multiply(Pb(be))
    pts = [("Gobek", GR["omuz_Gobek"][0], T_g.multVec(GR["omuz_Gobek"][1])),
           ("Kol", GR["omuz_Kol"][0], T_k.multVec(GR["omuz_Kol"][1])),
           ("Kol", GR["UstKol"][0], T_k.multVec(GR["UstKol"][1])),
           ("OnKol", GR["OnKol"][0], T_o.multVec(GR["OnKol"][1])),
           ("El", GR["El"][0], T_e.multVec(GR["El"][1]))]
    ax_r = T_g.Rotation.multVec(V(0, 0, 1))
    p_r = V(XR, 0, 0)
    ax_e = T_k.Rotation.multVec(V(*A.DIRSEK["eksen_yon"]))
    p_e = T_k.multVec(V(0, YE, ZE))
    ax_b = T_o.Rotation.multVec(V(*A.DIRSEK["bilek_yon"]))
    p_b = T_o.multVec(V(XW, 0, ZE))

    def tau(m, c, grp):
        f = V(0, -m, 0)
        t1 = m * c.z
        t2 = (c - p_r).cross(f).dot(ax_r) if grp in ("Kol", "OnKol", "El", "yuk") else 0.0
        t3 = (c - p_e).cross(f).dot(ax_e) if grp in ("OnKol", "El", "yuk") else 0.0
        t4 = (c - p_b).cross(f).dot(ax_b) if grp in ("El", "yukb") else 0.0
        return [t1, t2, t3, t4]
    t0_ = [0.0, 0.0, 0.0, 0.0]
    for g, m, c in pts:
        t0_ = [a + b for a, b in zip(t0_, tau(m, c, g))]
    uc = T_e.multVec(DP.YUK_UC)
    kanca = T_e.multVec(DP.YUK_KANCA)
    t1_ = tau(1.0, uc, "yuk")
    t1_[3] = tau(1.0, kanca, "yukb")[3]          # bilek: yuk kancada (el ucu bilek ekseninde)
    return t0_, t1_


PHI_T = list(range(-45, 136, 5))
TH_T = list(range(0, 121, 5))
AL_T = list(range(int(ar[0]), int(ar[1]) + 1, 5))
BE_T = [-90, 0, 90]
TK = []
for phi in PHI_T:
    for th in TH_T:
        for al in AL_T:
            for be in BE_T:
                t0_, t1_ = tork(phi, th, al, be)
                TK.append(((phi, th, al, be), t0_, t1_))
log("tork pozu", len(TK))
EKLEM = ["S1 (omuz one-arka)", "S2 (omuz yana acma)", "Dirsek", "Bilek"]
STALL = {"S1 (omuz one-arka)": ("DS3218MG", 20.0, "omuz raporundaki deger (datasheet 19 kg*cm @5 V, 21,5 @6,8 V)"),
         "S2 (omuz yana acma)": ("DS3218MG", 20.0, "omuz raporundaki deger"),
         "Dirsek": ("MG996R", 9.4, "datasheet 9,4 kg*cm @4,8 V (11 @6 V); 01-donanim-maliyet.md"),
         "Bilek": ("MG996R", 9.4, "datasheet 9,4 kg*cm @4,8 V")}


def en_kotu(j, m_yuk):
    best = (-1.0, None)
    for pose, t0_, t1_ in TK:
        t = abs(t0_[j] + m_yuk * t1_[j]) / 10000.0
        if t > best[0]:
            best = (t, pose)
    return best


tork_sonuc = []
for j, ad in enumerate(EKLEM):
    t_yuksuz, p_yuksuz = en_kotu(j, 0.0)
    t_yuklu, p_yuklu = en_kotu(j, YUK)
    servo, stall, kay = STALL[ad]
    # 2x pay icin izinli en buyuk yuk (ikiye bolme)
    lo, hi = 0.0, 5000.0
    if en_kotu(j, 0.0)[0] > stall / 2:
        izin = 0.0
    else:
        for _ in range(30):
            mid = (lo + hi) / 2
            if en_kotu(j, mid)[0] <= stall / 2:
                lo = mid
            else:
                hi = mid
        izin = lo
    tork_sonuc.append(dict(eklem=ad, servo=servo, stall_kgcm=stall, stall_kaynak=kay,
                           yuksuz_kgcm=round(t_yuksuz, 2), yuksuz_poz=p_yuksuz, yuksuz_pay=round(stall / max(t_yuksuz, 1e-9), 2),
                           yuklu_kgcm=round(t_yuklu, 2), yuklu_poz=p_yuklu, yuklu_pay=round(stall / max(t_yuklu, 1e-9), 2),
                           izinli_yuk_2x_g=round(izin, 0)))
    log("tork %-20s yuksuz %.2f (%s) yuklu %.2f (%s) stall %.1f -> pay %.2f / %.2f; 2x pay icin yuk <= %.0f g" % (
        ad, t_yuksuz, p_yuksuz, t_yuklu, p_yuklu, stall, stall / max(t_yuksuz, 1e-9), stall / max(t_yuklu, 1e-9), izin))
# omuz raporundaki eski hesap (alt kol 260 g tahmini) ile karsilastirma
omz = json.load(open(os.path.join(UST, "omuz", "omuz-analiz.json"), encoding="utf-8"))
lim = [(phi, th) for phi in O.PHIS for th in O.THS if -45 <= phi <= 135 and 0 <= th <= 120]
omuz_eski = dict(S1=max(omz["tork"]["%d,%d" % k][0] for k in lim), S2=max(omz["tork"]["%d,%d" % k][1] for k in lim),
                 alt_kol_g=omz["alt_kol"]["m"])
# dirsek ve bilek servosu: tork vs dirsek acisi (kol asagida, omuz 0/0 ve omuz one 90)
tork_egri = []
for al in range(int(ar[0]), int(ar[1]) + 1, 5):
    a0, a1 = tork(0, 0, al, 0)
    b0, b1 = tork(90, 0, al, 0)
    tork_egri.append(dict(al=al, dirsek_yuksuz=round(abs(a0[2]) / 1e4, 2), dirsek_yuklu=round(abs(a0[2] + YUK * a1[2]) / 1e4, 2),
                          s1_yuksuz_omuz0=round(abs(a0[0]) / 1e4, 2), s1_yuklu_omuz0=round(abs(a0[0] + YUK * a1[0]) / 1e4, 2),
                          s1_yuksuz_omuz90=round(abs(b0[0]) / 1e4, 2), s1_yuklu_omuz90=round(abs(b0[0] + YUK * b1[0]) / 1e4, 2)))

# ====================================================================== 6) baski analizi (X2D)
baski = []
IDX = {p["ad"]: k for k, p in enumerate(P)}
for ad, bd in DP.BASKI.items():
    r = L.baski_analiz(ad, P[IDX[ad]]["shape"], bd["yukari"], DP.DOLULUK)
    r["yon"] = bd["yon"]
    r["grup"] = P[IDX[ad]]["grup"]
    baski.append(r)
    log("baski %-16s %s sigar=%s cikinti %.3f destek sorunu %d" % (ad, r["olcu"], r["sigar"], r["cikinti_orani"], r["destek_sorun_sayi"]))

# ====================================================================== 7) kutle, agirlik merkezi
M = sum(p["kutle"] for p in P)
CG = V(0, 0, 0)
for p in P:
    CG = CG + p["merkez"] * (p["kutle"] / M)
kutle_grup = {g: round(GR[g][0], 1) for g in ("UstKol", "OnKol", "El")}
am_grup = {g: [round(GR[g][1].x, 2), round(GR[g][1].y, 2), round(GR[g][1].z, 2)] for g in ("UstKol", "OnKol", "El")}
kutle_tur = {}
for p in P:
    kutle_tur[p["tur"]] = kutle_tur.get(p["tur"], 0.0) + p["kutle"]
log("kutle %.1f g, AM (%.1f, %.1f, %.1f)" % (M, CG.x, CG.y, CG.z))

# ====================================================================== 8) kaydet: FCStd (Assembly) + STEP + BOM
doc = App.newDocument("DirsekMontaj")
asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
asm.Label = "Sag_Dirsek"
jg = asm.newObject("Assembly::JointGroup", "Joints")
jg.Label = "Eklemler"
groups = {}
for g, lab in (("UstKol", "Dirsek_ust_omuz_Kol_grubuna_sabit"), ("OnKol", "On_kol_dirsekte_doner"), ("El", "El_bilekte_doner")):
    gp = asm.newObject("App::Part", g)
    gp.Label = lab
    groups[g] = gp
feat = []
for k, p in enumerate(P):
    o = groups[p["grup"]].newObject("Part::Feature", "D%03d" % k)
    o.Label = p["ad"]
    o.Shape = p["shape"]
    for prop, val in (("Tur", p["tur"]), ("Malzeme", p["malzeme"]), ("Kod", p["kod"]), ("Renk", p["renk"]), ("Not", p["not_"])):
        o.addProperty("App::PropertyString", prop, "Robot")
        setattr(o, prop, val)
    o.addProperty("App::PropertyVector", "Patlat", "Robot")
    o.Patlat = V(*p["patlat"])
    o.addProperty("App::PropertyFloat", "Kutle_g", "Robot")
    o.Kutle_g = round(p["kutle"], 1)
    feat.append(o)
doc.recompute()
try:
    import JointObject
    gj = jg.newObject("App::FeaturePython", "Sabit")
    JointObject.GroundedJoint(gj, groups["UstKol"])
    first = {g: next(o for o, p in zip(feat, P) if p["grup"] == g and p["tur"] == "Baski") for g in groups}

    def revolute(name, label, ga, gb, point, rot, amin_, amax_):
        j = jg.newObject("App::FeaturePython", name)
        JointObject.Joint(j, 1)
        j.Label = label
        j.Reference1 = [groups[ga], [first[ga].Name + ".Face1", first[ga].Name + ".Vertex1"]]
        j.Reference2 = [groups[gb], [first[gb].Name + ".Face1", first[gb].Name + ".Vertex1"]]
        j.Detach1 = True
        j.Detach2 = True
        j.Placement1 = App.Placement(V(*point), rot)
        j.Placement2 = App.Placement(V(*point), rot)
        j.EnableAngleMin = True
        j.AngleMin = amin_
        j.EnableAngleMax = True
        j.AngleMax = amax_
        return j
    revolute("Dirsek", "Dirsek (MG996R)", "UstKol", "OnKol", A.DIRSEK["eksen_nokta"], App.Rotation(V(0, 1, 0), -90), ar[0], ar[1])
    revolute("Bilek", "Bilek (MG996R)", "OnKol", "El", A.DIRSEK["bilek_nokta"], App.Rotation(V(1, 0, 0), -90),
             A.DIRSEK["bilek_aralik"][0], A.DIRSEK["bilek_aralik"][1])
    asm.solve()
    doc.recompute()
    joints_ok = True
except Exception as e:
    joints_ok = repr(e)
for g in groups.values():
    g.Placement = App.Placement()
doc.recompute()
doc.saveAs(os.path.join(HERE, "dirsek-montaj.FCStd"))
App.closeDocument(doc.Name)
Part.Compound([p["shape"] for p in P]).exportStep(os.path.join(HERE, "dirsek-montaj.step"))
step_kati = len(Part.read(os.path.join(HERE, "dirsek-montaj.step")).Solids)
bom = {}
for p in P:
    if p["kod"].startswith("("):
        continue
    key = (p["tur"], p["kod"] if p["tur"] != "Baski" else p["ad"])
    bom.setdefault(key, dict(adet=0, kutle=0.0))
    bom[key]["adet"] += 1
    bom[key]["kutle"] += p["kutle"]
with open(os.path.join(HERE, "dirsek-bom.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Tur", "Kalem", "Adet (sag kol)", "Adet (iki kol)", "Toplam kutle sag (g)"])
    for (t, kod), v in sorted(bom.items()):
        w.writerow([t, kod, v["adet"], 2 * v["adet"], "%.1f" % v["kutle"]])
log("kayit: STEP kati", step_kati, "eklem", joints_ok)


# ====================================================================== 9) analiz json (2. asama bunu okur)
def vl(v):
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]


out = dict(
    modul="dirsek_sag", ayna_modul="dirsek_sol",
    koordinat="omuz yereli: orijin travers merkezi, X disari, Y yukari, Z ileri (mm); global = yerel + arayuz.MODULLER konumu",
    yerlesim=dict(sag=A.MODULLER["dirsek_sag"], sol=A.MODULLER["dirsek_sol"]),
    parca_sayisi=len(P), baski_sayisi=len(DP.BASKI),
    parcalar=[dict(i=k, ad=p["ad"], grup=p["grup"], tur=p["tur"], malzeme=p["malzeme"], kod=p["kod"], kutle_g=round(p["kutle"], 2),
                   hacim_mm3=round(p["hacim"], 1), merkez=vl(p["merkez"]),
                   bb=[round(x, 2) for x in (p["bb"].XMin, p["bb"].XMax, p["bb"].YMin, p["bb"].YMax, p["bb"].ZMin, p["bb"].ZMax)],
                   patlat=p["patlat"], not_=p["not_"]) for k, p in enumerate(P)],
    gruplar=dict(
        UstKol=dict(hareket="omuz Kol grubuyla birlikte: Pp(phi) * Pr(th) (omuz_parcalar)", baglanti="omuz 'Ust kol tupu' ucuna sikma bilezigi",
                    parca=[p["ad"] for p in P if p["grup"] == "UstKol"]),
        OnKol=dict(hareket="UstKol * Pe(dirsek)", parca=[p["ad"] for p in P if p["grup"] == "OnKol"]),
        El=dict(hareket="OnKol * Pb(bilek)", parca=[p["ad"] for p in P if p["grup"] == "El"])),
    eklemler=[
        dict(ad="Dirsek", tip="revolute", ust="UstKol", alt="OnKol", nokta=list(A.DIRSEK["eksen_nokta"]), yon=list(A.DIRSEK["eksen_yon"]),
             aralik=list(ar), ev=0.0, serbest_aralik=[amin, amax], servo=A.DIRSEK["servo"],
             not_="+aci on kolu one buker; servo 180 derece: horn, servo orta konumu (90) = dirsek %d derece olacak sekilde takilir" % round((ar[0] + ar[1]) / 2)),
        dict(ad="Bilek", tip="revolute", ust="OnKol", alt="El", nokta=list(A.DIRSEK["bilek_nokta"]), yon=list(A.DIRSEK["bilek_yon"]),
             aralik=list(A.DIRSEK["bilek_aralik"]), ev=0.0, servo="MG996R (180 derece)", not_="on kol ekseni; ev 0 = avuc ice (-X)")],
    kinematik="T_UstKol = Pp(phi)*Pr(th); T_OnKol = T_UstKol*Pe(al); T_El = T_OnKol*Pb(be); Pp/Pr omuz_parcalar ile ayni, "
              "Pe = Rotation((-1,0,0), al) merkez (0, %.1f, %.2f); Pb = Rotation((0,1,0), be) merkez (%.1f, 0, %.2f)" % (YE, ZE, XW, ZE),
    tarama_onerisi=dict(dirsek=list(range(int(ar[0]), int(ar[1]) + 1, 10)), bilek=[-90, 0, 90],
                        not_="2. asama: omuz pozlari (phi, th) x dirsek acilari; bilek yalniz el (El grubu) icin; sol kol aynali"),
    gecersiz=gecersiz, coklu_kati=coklu, statik=statik, cift_sayisi=n_cift, tolerans_mm3=TOL,
    omuz_arayuzu=dict(cakisma=arayuz_cak, kontroller=ara),
    baglanti_kontrol=bag_kontrol,
    tarama=dict(als=ALS, bes=BES, bes_kol=BES_K,
                onkol_ust={str(k): v for k, v in onkol_ust.items()},
                el_ust={"%d,%d" % k: v for k, v in el_ust.items()},
                el_onkol={str(k): v for k, v in el_onkol.items()},
                serbest=[amin, amax], bilek_serbest=bilek_serbest, ilk_carpan=ilk_carpan, bosluk=bosluk,
                bukulme=bukulme, aralik=list(ar), aralik_ok=aralik_ok,
                not_="bosluk: es eksenli eklem elemanlari haric en kucuk mesafe (pimdeki 1 mm eksenel bosluk); "
                     "bukulme: on kol + el ile ust kolun eksenden uzak bolumu (y >= -149) arasi"),
    tork=dict(sonuc=tork_sonuc, yuk_g=YUK, yuk_noktasi=vl(DP.YUK_UC), kanca_noktasi=vl(DP.YUK_KANCA),
              tarama=dict(phi=[PHI_T[0], PHI_T[-1], 5], th=[TH_T[0], TH_T[-1], 5], al=[AL_T[0], AL_T[-1], 5], be=BE_T),
              omuz_eski=omuz_eski, egri=tork_egri,
              grup={k: dict(m=round(v[0], 1), am=vl(v[1])) for k, v in GR.items()}),
    baski=baski, doluluk=DP.DOLULUK, yazici=dict(A.YAZICI),
    kutle_g=round(M, 1), kutle_grup=kutle_grup, am_grup=am_grup, kutle_tur={k: round(v, 1) for k, v in kutle_tur.items()},
    agirlik_merkezi=vl(CG),
    bom=[[t, kod, v["adet"], round(v["kutle"], 1)] for (t, kod), v in sorted(bom.items())],
    step_kati=step_kati, joints_ok=joints_ok,
    arayuz=dict((k, (list(v) if isinstance(v, tuple) else v)) for k, v in A.DIRSEK.items()),
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "dirsek-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("bitti")
