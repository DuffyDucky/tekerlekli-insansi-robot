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
# tup ic yaricapi arayuzden (A.DIRSEK["tup_ri"] = A.TUP_PIM_R + A.GECME["tup_pim"]); omuzdaki gercek tup geometrisiyle de dogrulanir
r_tup_ic = A.DIRSEK["tup_ri"]
yar_tup = []
for w in TUP["shape"].slice(V(0, 1, 0), kes_y):
    for e in w.Edges:
        cv = e.Curve
        if hasattr(cv, "Radius") and math.hypot(cv.Center.x - DP.TX, cv.Center.z - DP.TZ) < 1e-6:
            yar_tup.append(cv.Radius)
r_tup_ic_geo = min(yar_tup)
KABUL = A.GECME["kabul_max"]
b_pim = r_tup_ic - r_pim
b_bil = r_bil - A.DIRSEK["tup_ro"]
ara.append(("tup ic yaricapi: omuz geometrisi = arayuz (A.GECME) %.3f mm" % r_tup_ic_geo,
            round(r_tup_ic_geo, 3), abs(r_tup_ic_geo - r_tup_ic) < 1e-6))
ara.append(("pim - tup ic yuzu radyal bosluk %.2f mm (sikma bilezigi tupu pime bastirir; kabul <= %.2f)" % (b_pim, KABUL),
            round(b_pim, 3), 0.0 < b_pim <= KABUL and abs(b_pim - A.GECME["tup_pim"]) < 1e-6))
ara.append(("bilezik ic yuzu - tup dis yuzu radyal bosluk %.2f mm (kabul <= %.2f)" % (b_bil, KABUL),
            round(b_bil, 3), 0.0 < b_bil <= KABUL and abs(b_bil - A.GECME["tup_bilezik"]) < 1e-6))
ara.append(("pim tupe giris boyu %.1f mm" % (catal.BoundBox.YMax - A.DIRSEK["tup_uc_y"]),
            round(catal.BoundBox.YMax - A.DIRSEK["tup_uc_y"], 2), catal.BoundBox.YMax - A.DIRSEK["tup_uc_y"] >= 20.0))

# --- sikma bilezigi kelepcesi (duzeltme plani 1. adim, G): tup pim ile bilezik arasinda sikisir. Yarik kapaninca bilezik ic yaricapi
#     ~ yarik/(2*pi) kadar iner; bu dusus toplam radyal bosluktan (pim-tup + bilezik-tup) en az on yuk kadar BUYUK olmali, yoksa kelepce
#     tupu pime bastiramaz. Yarik genisligi catal geometrisinden olculur (y = -128 kesiti, kulak ucundaki yarik koseleri).
tup_yaricap_arasi = r_pim < r_tup_ic < A.DIRSEK["tup_ro"] < r_bil          # tup duvari (r_ic...r_dis) pim ile bilezik arasinda
ara.append(("tup duvari (r %.2f...%.2f) pim (r %.2f) ile bilezik (r %.2f) arasinda; tup alin kapagina ve V oluga dayali" % (
    r_tup_ic, A.DIRSEK["tup_ro"], r_pim, r_bil), [round(r_pim, 3), round(r_tup_ic, 3), round(A.DIRSEK["tup_ro"], 3), round(r_bil, 3)],
    tup_yaricap_arasi))
xs_yarik = [v.X for w in catal.slice(V(0, 1, 0), kes_y) for v in w.Vertexes
            if abs(v.X - DP.TX) < 6.0 and v.Z < DP.TZ - 30.0]
yarik_w = max(xs_yarik) - min(xs_yarik)                                      # acik yarik genisligi (geometriden)
yay_acik = 2.0 * r_bil * math.asin(yarik_w / (2.0 * r_bil))                    # yariga denk gelen ic yuz yayi
r_kapali = (2.0 * math.pi * r_bil - yay_acik) / (2.0 * math.pi)               # yarik tam kapaninca (kulaklar degince) ic yaricap
dr_kapanma = r_bil - r_kapali
bosluk_toplam = b_pim + b_bil
on_yuk = dr_kapanma - bosluk_toplam
ON_YUK_MIN = A.DIRSEK["bilezik_on_yuk_min"]
ara.append(("yarik %.2f mm (arayuz %.2f): kapaninca ic yaricap %.3f -> %.3f mm (%.3f iner)" % (
    yarik_w, A.DIRSEK["bilezik_yarik"], r_bil, r_kapali, dr_kapanma), round(yarik_w, 3), abs(yarik_w - A.DIRSEK["bilezik_yarik"]) < 1e-3))
ara.append(("kelepce kapanma %.3f mm >= toplam radyal bosluk %.2f (pim-tup %.2f + bilezik-tup %.2f) + on yuk %.2f; kalan on yuk %.3f mm" % (
    dr_kapanma, bosluk_toplam, b_pim, b_bil, ON_YUK_MIN, on_yuk), round(on_yuk, 3), dr_kapanma >= bosluk_toplam + ON_YUK_MIN - 1e-9))
kelepce = dict(yarik_mm=round(yarik_w, 3), yay_acik_mm=round(yay_acik, 3), r_bilezik_acik=round(r_bil, 4), r_bilezik_kapali=round(r_kapali, 4),
               kapanma_mm=round(dr_kapanma, 4), bosluk_toplam_mm=round(bosluk_toplam, 4), on_yuk_mm=round(on_yuk, 4),
               on_yuk_min_mm=ON_YUK_MIN, eski_yarik_2mm_kapanma_mm=round(2.0 / (2 * math.pi), 3), kontrol_ok=bool(on_yuk >= ON_YUK_MIN - 1e-9))
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


# sikma bilezigi: civata yarigi kapatirken somun tarafi kulak (yarigin -X yani) +yarik kadar kayar; somun ve pul onunla gider
KUL_KUTU = Part.makeBox(DP.TX - yarik_w / 2 - 170.0, 25.0, 14.0, V(170.0, -139.0, DP.TZ - 45.0))     # x 170...yarik yuzu, z TZ-45...TZ-31
CATAL_KUL = catal.common(KUL_KUTU)
CATAL_KALAN = catal.cut(KUL_KUTU)
KUL_KAYMIS = CATAL_KUL.copy()
KUL_KAYMIS.translate(V(yarik_w, 0, 0))
kul_cakisma = kes(KUL_KAYMIS, CATAL_KALAN)
log("kelepce kulak kapanma cakismasi mm3", round(kul_cakisma, 4))

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
            if b["ad"].startswith("Sikma bilezigi"):
                # yarik kapanirken somun + pul +yarik kadar kafaya dogru kayar; civata (basi sabit kulakta) yerinde kalir
                t_yakin = t_aralik(som, n0, u)[0] - yarik_w     # somun yakin yuzu (kafa tarafi), kapali halde
                cik_k = t_uc - (t_aralik(som, n0, u)[1] - yarik_w)  # civata ucu - somun uzak yuzu, kapali halde
                DISLI = 2 * d_ + 6.0                          # DIN 912 / ISO 4762 en kisa dislik boy (2d+6, l <= 125)
                k.append(("yarik %.1f mm kapaninca civata ucu somundan %.1f mm tasir (>= 0,5): vida boyu yarigi kapatir" % (yarik_w, cik_k),
                          round(cik_k, 3), cik_k >= 0.5))
                k.append(("kapali halde somun dislik boy icinde (somun yakin yuzu uctan %.1f <= %.0f mm)" % (t_uc - t_yakin, DISLI),
                          round(t_uc - t_yakin, 3), t_uc - t_yakin <= DISLI))
                som_k = som.copy()
                som_k.translate(V(yarik_w, 0, 0))
                pul_k = S(b["pul_somun"]).copy()
                pul_k.translate(V(yarik_w, 0, 0))
                dk = min(mesafe(som_k, CATAL_KALAN), mesafe(pul_k, CATAL_KALAN))
                k.append(("kapali halde somun ve pul catalin kalanina %.2f mm (>= 1; kulak bosluga girer)" % dk, round(dk, 3), dk >= 1.0))
                k.append(("kayan kulak karsi kulak/halka ile cakismiyor (%.3f mm3 <= %.1f)" % (kul_cakisma, TOL), round(kul_cakisma, 4),
                          0.0 <= kul_cakisma <= TOL))
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


def _izgara(aralik, adim=5):
    """Eklem araligi (arayuz) ucta tam: alt/ust sinir + aradaki adim katlari (ornek yana 3...120 -> 3, 5, 10, ..., 120)."""
    lo, hi = int(math.ceil(aralik[0])), int(math.floor(aralik[1]))
    return sorted({lo, hi} | set(range(-(-lo // adim) * adim, hi + 1, adim)))


PHI_T = _izgara(A.OMUZ["one_arka_aralik"])      # S1 (omuz one-arka): arayuz.OMUZ, elle sinir yok
TH_T = _izgara(A.OMUZ["yana_aralik"])           # S2 (omuz yana acma): arayuz.OMUZ (alt sinir 3)
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
lim = [(phi, th) for phi in O.PHIS for th in O.THS if A.OMUZ["one_arka_aralik"][0] <= phi <= A.OMUZ["one_arka_aralik"][1] and A.OMUZ["yana_aralik"][0] <= th <= A.OMUZ["yana_aralik"][1]]
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


# ====================================================================== 8b) kol kablo yolu (duzeltme plani M1; arayuz.KOL_KABLO, kablo_yolu.py)
# Dirsek lopu (dirsek 0...105) ve S2 lopu (yana 3...120) duzlemsel elastikayla her pozda cozulur: en kucuk egrilik yaricapi
# (>= r_dinamik), kiris < L (gerilmez), demet cevrel zarfi ile parcalar arasi bosluk (>= pay_bosluk; ilk / son 4 mm baglama
# noktasi, haric). Sabit yollar: kose yaricapi (>= r_sabit), yassi yatan demet ile parcalar arasi bosluk (>= 0; servo cikisinin
# ilk 2 mm'si haric). Gecitler: disi JR'nin O10 delikten ve tup penceresinden gecisi, tup icinde iki eslesik JR. Boy: servo
# kablosu (300) birlesime ulasir mi. S1 gecisi: doner U-lop kaseti (arayuz KOL_KABLO["s1"], asagida s1_*).
import kablo_yolu as KY
KK = A.KOL_KABLO
R_DIN = {n: KY.r_sinir(KK, n)[0] for n in (1, 2)}
R_SAB = {n: KY.r_sinir(KK, n)[1] for n in (1, 2)}
PAY = KK["pay_bosluk"]
UC = 4.0


def grup_sekil(gruplar, pl=None, kaynak=None):
    kaynak = P if kaynak is None else kaynak
    return [(q["ad"], tasi(q["shape"], pl) if pl is not None else q["shape"]) for q in kaynak if q["grup"] in gruplar]


UST_S = grup_sekil(("UstKol",)) + grup_sekil(("Kol",), kaynak=O.P)        # ev pozu (omuz Kol grubu + dirsek catali): UstKol cercevesi
ONK_POZ = {}


def onkol_sekil(al):
    if al not in ONK_POZ:
        ONK_POZ[al] = grup_sekil(("OnKol", "El"), Pe(al))
    return ONK_POZ[al]


kablo = dict(kaynak="arayuz.KOL_KABLO + dirsek/kablo_yolu.py", serit=list(KK["serit"]),
             r_dinamik={str(n): round(v, 2) for n, v in R_DIN.items()}, r_sabit={str(n): round(v, 2) for n, v in R_SAB.items()},
             pay_bosluk=PAY, s1=KK["s1"])


def lop_degerlendir(ad, lt, rel_yer, pozlar, sekiller):
    dm = KY.demet(lt["serit"], KK["serit"])
    sonuc = KY.lop_coz(lt, rel_yer, pozlar)
    satir = []
    for r in sonuc:
        kenar, boy_ = KY.cokgen(r["nokta"], UC, UC)
        d, kim = KY.en_yakin(kenar, sekiller(r["poz"]))
        satir.append(dict(poz=r["poz"], r_min=round(r["r_min"], 2), kiris=round(r["kiris"], 2), bosluk=round(d - dm["r_lop"], 2),
                          en_yakin=kim, yakinsadi=r["yakinsadi"]))
    rmin = min(s["r_min"] for s in satir)
    bmin = min(satir, key=lambda s: s["bosluk"])
    kmax = max(s["kiris"] for s in satir)
    ok = (all(s["yakinsadi"] for s in satir) and rmin >= R_DIN[lt["serit"]] and bmin["bosluk"] >= PAY and kmax < lt["L"])
    log("kablo %s: L %.0f, R_min %.1f (>= %.1f), en kucuk bosluk %.2f (%s, poz %s), kiris %.1f...%.1f %s" % (
        ad, lt["L"], rmin, R_DIN[lt["serit"]], bmin["bosluk"], bmin["en_yakin"], bmin["poz"], min(s["kiris"] for s in satir), kmax,
        "OK" if ok else "HATA"))
    ornek = {str(sonuc[i]["poz"]): [vl(q) for q in sonuc[i]["nokta"][::6]] for i in (0, len(sonuc) // 2, len(sonuc) - 1)}
    return dict(L=lt["L"], serit=lt["serit"], demet=dm, r_min=rmin, r_sinir=round(R_DIN[lt["serit"]], 2), en_kucuk_bosluk=bmin["bosluk"],
                en_yakin=bmin["en_yakin"], en_yakin_poz=bmin["poz"], kiris=[min(s["kiris"] for s in satir), kmax], ok=bool(ok),
                pozlar=satir, ornek_nokta=ornek)


# --- dirsek lopu: M on kolda (Pe(al)), F catalda (UstKol); dirsek 0...105 (2,5 adim)
DL = KK["dirsek_lop"]
AL_K = [ar[0] + 2.5 * i for i in range(int(round((ar[1] - ar[0]) / 2.5)) + 1)]
kablo["dirsek_lop"] = lop_degerlendir("dirsek lopu", DL, lambda al: Pe(al), AL_K, lambda al: UST_S + onkol_sekil(al))

# --- S2 lopu: K kol catalinda (Pr(th)), G2 gobekte; yana 3...120 (3 adim). Gobek cercevesinde: omuz Gobek sabit, Kol + dirsek UstKol
#     Pr(th) ile; Govde parcalari S1 pozlarinda gobege gore -phi (kapak, yuva, kabuk referansi)
SL = KK["s2_lop"]
GOB_S = grup_sekil(("Gobek",), kaynak=O.P)
GOV_S = []
for _phi in (-45, 0, 45, 90, 135):
    GOV_S += [("%s (S1 %d)" % (a, _phi), s) for a, s in grup_sekil(("Govde",), Pp(_phi).inverse(), kaynak=O.P)]
yana = A.OMUZ["yana_aralik"]
TH_K = sorted(set([yana[0]] + list(range(int(math.ceil(yana[0] / 3.0)) * 3, int(yana[1]) + 1, 3)) + [yana[1]]))
KOL_POZ = {}


def kol_sekil(th):
    if th not in KOL_POZ:
        KOL_POZ[th] = grup_sekil(("Kol",), Pr(th), kaynak=O.P) + grup_sekil(("UstKol",), Pr(th))
    return KOL_POZ[th]


kablo["s2_lop"] = lop_degerlendir("S2 lopu", SL, lambda th: Pr(th), TH_K, lambda th: GOB_S + GOV_S + kol_sekil(th))


# --- sabit yollar
def yol_degerlendir(ad, yt, cerceve_sekil, pozlar, bas=0.0):
    n = yt["serit"]
    dm = KY.demet(n, KK["serit"])
    rk, ik, koseler = KY.kose_yaricap(yt["nokta"])
    bmin = (1e9, None, None)
    for poz in pozlar:
        pl, sekiller = cerceve_sekil(poz)
        q = [pl.multVec(V(*p)) for p in yt["nokta"]]
        kenar, _ = KY.cokgen(q, bas, 0.0)
        d, kim = KY.en_yakin(kenar, sekiller)
        if d - dm["r_sabit"] < bmin[0]:
            bmin = (d - dm["r_sabit"], kim, poz)
    _, boy_ = KY.cokgen(yt["nokta"])
    ok = rk >= R_SAB[n] - 1e-9 and bmin[0] >= -1e-6
    log("kablo yol %s: boy %.1f, kose yaricapi en fazla %.1f (>= %.1f), en kucuk bosluk %.2f (%s, poz %s) %s" % (
        ad, boy_, rk, R_SAB[n], bmin[0], bmin[1], bmin[2], "OK" if ok else "HATA"))
    return dict(grup=yt["grup"], serit=n, boy=round(boy_, 1), kose_r_max=round(rk, 2), r_sinir=round(R_SAB[n], 2),
                koseler=[[round(a, 2), i, round(b, 1)] for a, i, b in koseler], en_kucuk_bosluk=round(bmin[0], 2),
                en_yakin=bmin[1], en_yakin_poz=bmin[2], ok=bool(ok))


def ONK_KONTROL(al):        # on kol yolu: on kolla birlikte doner; catal, tup ve on kola gore
    return Pe(al), UST_S + onkol_sekil(al)


kablo["yol_dirsek_servo"] = yol_degerlendir("dirsek servosu", KK["yol_dirsek_servo"], ONK_KONTROL, AL_K[::2],
                                            bas=KK["yol_dirsek_servo"]["cikis"])
kablo["yol_bilek_servo"] = yol_degerlendir("bilek servosu", KK["yol_bilek_servo"], ONK_KONTROL, AL_K[::2],
                                           bas=KK["yol_bilek_servo"]["cikis"])
kablo["yol_ustkol"] = yol_degerlendir("catal + tup ici", KK["yol_ustkol"], lambda al: (App.Placement(), UST_S + onkol_sekil(al)), AL_K[::2])
GOB_KOL = {}


def kol_cerceve(th):        # Kol cercevesinde: gobek ve Govde (S1 0) Pr(th)^-1 ile
    if th not in GOB_KOL:
        inv = Pr(th).inverse()
        GOB_KOL[th] = grup_sekil(("Gobek",), inv, kaynak=O.P) + grup_sekil(("Govde",), inv, kaynak=O.P)
    return App.Placement(), UST_S + GOB_KOL[th]


kablo["yol_uzatma_kol"] = yol_degerlendir("tup penceresi -> K", KK["yol_uzatma_kol"], kol_cerceve, TH_K[::5])

# --- gecitler (montajda disi JR gecer mi; tup icinde birlesim sigar mi)
JR = KK["jr_disi"]
jr_diag = math.hypot(JR[0], JR[1])
gecit = []
r_del = min(e.Curve.Radius for w in catal.slice(V(0, 1, 0), -142.0) for e in w.Edges
            if hasattr(e.Curve, "Radius") and math.hypot(e.Curve.Center.x - DP.TX, e.Curve.Center.z - DP.TZ) < 1e-6)
gecit.append(dict(ad="catal kablo deligi (O%.1f) <- disi JR kosegeni %.2f" % (2 * r_del, jr_diag), deger=round(2 * r_del - jr_diag, 2),
                  ok=bool(2 * r_del >= jr_diag + 0.5)))
TP = KK["tup_pencere"]
jr_kutu = Part.makeBox(JR[0] + 0.4, JR[1] + 0.4, 15.0, V(DP.TX - (JR[0] + 0.4) / 2, -77.0 - (JR[1] + 0.4) / 2, -33.0))
v_jr = jr_kutu.common(tup).Volume
gecit.append(dict(ad="tup penceresi (%.0f x %.0f duz) <- disi JR %.1f x %.2f" % (TP["x"][1] - TP["x"][0], TP["y"][1] - TP["y"][0] - 2 * TP["uc"],
                                                                                JR[0], JR[1]), deger=round(v_jr, 4), ok=bool(v_jr < 1e-6)))
EJ = KK["jr_eslesik"]
bj = V(*KK["birlesim"])
bir_kutu = Part.makeBox(EJ[0], EJ[2], 2 * EJ[1], V(bj.x - EJ[0] / 2, bj.y - EJ[2] / 2, bj.z - EJ[1]))     # x 10,3, boy y yonunde, iki yan yana z
v_bir = sum(bir_kutu.common(s).Volume for a, s in UST_S if s.BoundBox.intersect(bir_kutu.BoundBox))
gecit.append(dict(ad="tup ici iki eslesik JR (%.1f x %.0f x %.0f)" % (EJ[0], 2 * EJ[1], EJ[2]), deger=round(v_bir, 4), ok=bool(v_bir < 1e-6)))
kablo["gecit"] = gecit
log("kablo gecit:", [(g["ad"], g["deger"], g["ok"]) for g in gecit])

# --- boy: servo kablosu (300) birlesime ulasir (sabit yol + lop + catal/tup yolu + pay)
boy = []
L_ust = kablo["yol_ustkol"]["boy"]
for ad, yk in (("dirsek servosu (MG996R) -> tup ici (y %.0f)" % KK["yol_ustkol"]["nokta"][-1][1], "yol_dirsek_servo"),
               ("bilek servosu (MG996R) -> tup ici (y %.0f)" % KK["yol_ustkol"]["nokta"][-1][1], "yol_bilek_servo")):
    gerek = kablo[yk]["boy"] + DL["L"] + L_ust
    boy.append(dict(ad=ad, gerekli_mm=round(gerek, 1), kablo_mm=KK["servo_kablo_boy"], artan_mm=round(KK["servo_kablo_boy"] - gerek, 1),
                    ok=bool(KK["servo_kablo_boy"] - gerek >= KK["boy_payi"])))
L_uz = kablo["yol_uzatma_kol"]["boy"] + SL["L"]
boy.append(dict(ad="uzatma (birlesim -> G2, S1 oncesi)", gerekli_mm=round(L_uz, 1),
                not_="S1 kaseti + govde ici + dagitim karti: kablo['s1_boy']"))
kablo["boy"] = boy
log("kablo boy:", [(b["ad"], b["gerekli_mm"], b.get("artan_mm"), b.get("ok")) for b in boy])
# --- S1 doner U-lop kaseti (15 Ekim 2026; arayuz KOL_KABLO["s1"], kablo_yolu.u_lop / s1_*; planlama/adim2/S1-kaset.md)
#     Tambur omuz Gobek grubunda (omuz_parcalar), kaset govdesi + kapagi kabuk modulunde (kabuk-montaj.FCStd'den okunur; once kabuk_montaj).
#     U temasli elastika (pozdan bagimsiz). Her S1 pozunda (-45...135, 5 derece): ic / dis kosu acisi >= alfa_min; kablonun (tambur bagi ->
#     ic kosu -> U -> dis kosu -> duvar bagi) demet cevrel zarfiyla bosluk: omuz Govde, gobek (tambur haric), kabuk (kaset haric), kol +
#     ust kol (S2 alt sinir ve 20). Tambur ve kaset tasarim geregi temas yuzeyi: ayrica kanal paylari raporlanir. Gecis (G2 -> tambur bagi,
#     gobek cercevesi) ve cikis (duvar bagi -> ped yarigi -> govde ici) sabit yol: kose yaricapi >= r_sabit (3 serit), bosluk >= 0.
import shutil, tempfile
S1 = KK["s1"]
S1O = KY.s1_olcu(KK)
U1 = S1O["U"]
N1 = S1["serit"]
R_DIN1, R_SAB1 = KY.r_sinir(KK, N1)
DM1 = KY.demet(N1, KK["serit"])
R_ON1 = 10.0 * KK["serit"][1] + (N1 - 1) * KK["serit"][1] / 2.0          # 10 x d (bilgi: K-kontrol onerisi)
OMUZ_Y = A.MODULLER["omuz_sag"]["konum"][1]


def kabuk_oku():
    yol = os.path.join(UST, "kabuk", "kabuk-montaj.FCStd")
    tmp = os.path.join(tempfile.gettempdir(), "dirsek_s1_kabuk.FCStd")
    shutil.copy2(yol, tmp)
    d = App.openDocument(tmp)
    out = []
    for o in d.Objects:
        if o.TypeId == "Part::Feature" and ("sag" in o.Label) and (o.Label.startswith("S1 kaset") or o.Label.startswith("Omuz bandi")
                                                                  or o.Label.startswith("Gogus bandi") or "Kaset civatasi" in o.Label):
            s_ = o.Shape.copy()
            s_.Placement = o.getGlobalPlacement()
            s_ = s_.copy()
            s_.translate(V(0, -OMUZ_Y, 0))
            out.append((o.Label, s_))
    App.closeDocument(d.Name)
    return out, datetime_mtime(yol)


def datetime_mtime(p):
    import datetime
    return datetime.datetime.fromtimestamp(os.stat(p).st_mtime).isoformat(timespec="seconds")


KAB1, KAB1_T = kabuk_oku()
KASET = [(a, s_) for a, s_ in KAB1 if a.startswith("S1 kaset")]
KAB_DIGER = [(a, s_) for a, s_ in KAB1 if not a.startswith("S1 kaset")]
TAMBUR = [(q["ad"], q["shape"]) for q in O.P if q["ad"] == "S1 kablo tamburu"]
GOB_DIGER = [(q["ad"], q["shape"]) for q in O.P if q["grup"] == "Gobek" and q["ad"] != "S1 kablo tamburu"]
GOV1 = [(q["ad"], q["shape"]) for q in O.P if q["grup"] == "Govde" and q["tur"] != "Referans"]
log("S1: kabuk-montaj.FCStd (%s) %d parca (kaset %d); U R_min %.2f (sinir %.2f, 10xd %.2f), l %.1f, delta %.1f, uc +%.1f" % (
    KAB1_T, len(KAB1), len(KASET), U1["R_min"], R_DIN1, R_ON1, U1["l"], U1["delta"], U1["pol_max"]))
PHI_S1 = list(range(int(A.OMUZ["one_arka_aralik"][0]), int(A.OMUZ["one_arka_aralik"][1]) + 1, 5))
TH_S1 = [yana[0], 20.0]
kol1 = {th: grup_sekil(("Kol",), Pr(th), kaynak=O.P) + grup_sekil(("UstKol",), Pr(th)) for th in TH_S1}
satir1 = []
for phi in PHI_S1:
    ps = KY.s1_poz(KK, phi, S1O)
    kenar, boy1 = KY.cokgen(ps["nokta"], UC, UC)
    pp = Pp(phi)
    hedef = GOV1 + KAB_DIGER + [(a + " (S1 %d)" % phi, tasi(s_, pp)) for a, s_ in GOB_DIGER]
    for th in TH_S1:
        hedef += [("%s (S2 %g)" % (a, th), tasi(s_, pp)) for a, s_ in kol1[th]]
    d, kim = KY.en_yakin(kenar, hedef)
    satir1.append(dict(phi=phi, psi_bag=round(ps["psi_bag"], 2), psi_U=round(ps["psi_U"], 2), a_i=round(ps["a_i"], 2), a_o=round(ps["a_o"], 2),
                       u_uc_psi=round(ps["u_uc_psi"], 2), bosluk=round(d - DM1["r_lop"], 2), en_yakin=kim))
b1 = min(satir1, key=lambda q: q["bosluk"])
a_min = min(min(q["a_i"], q["a_o"]) for q in satir1)
# duyarlilik: eksen kacikligi +-1 mm (h 31 / 33), serit kalinligi 1,8 (demet 5,4)
duy = []
for ad_, ri_, ro_ in (("eksen kacikligi -1 mm", S1O["ri"], S1O["ro"] - 1.0), ("eksen kacikligi +1 mm", S1O["ri"], S1O["ro"] + 1.0),
                      ("serit 1,8 mm (demet %.1f)" % (N1 * 1.8), S1["tambur"]["r"][1] + N1 * 0.9, S1["duvar"]["r"][0] - N1 * 0.9)):
    u_ = KY.u_lop(ri_, ro_)
    duy.append(dict(durum=ad_, ri=round(ri_, 2), ro=round(ro_, 2), R_min=round(u_["R_min"], 2)))
duy.append(dict(durum="serit 1,8: sinir 7,5 d + demet payi", R_sinir=round(7.5 * 1.8 + (N1 - 1) * 0.9, 2)))
kanal = dict(eksenel_arka=round(S1O["xc"] - (S1["duvar"]["x0"] + S1["duvar"]["arka_t"]) - KK["serit"][0] / 2, 2),
             eksenel_flans=round(S1["duvar"]["flans_x"][0] - S1O["xc"] - KK["serit"][0] / 2, 2),
             eksenel_tambur_dudak=round((S1["kanal_x"][1] - S1["kanal_x"][0] - KK["serit"][0]) / 2, 2),
             radyal_tambur=round(S1O["ri"] - S1O["kalinlik"] / 2 - S1["tambur"]["r"][1], 3),
             radyal_duvar=round(S1["duvar"]["r"][0] - S1O["ro"] - S1O["kalinlik"] / 2, 3))
ok_lop = bool(U1["gecerli"] and U1["R_min"] >= R_DIN1 and b1["bosluk"] >= PAY and a_min >= S1["alfa_min"] - 1e-6)
log("kablo S1 lopu: L %.1f, R_min %.2f (>= %.2f; 10xd %.2f %s), en kucuk bosluk %.2f (%s, phi %s), kosu acisi en az %.1f (>= %.0f) %s" % (
    S1["L"], U1["R_min"], R_DIN1, R_ON1, "saglar" if U1["R_min"] >= R_ON1 else "SAGLAMAZ", b1["bosluk"], b1["en_yakin"], b1["phi"], a_min,
    S1["alfa_min"], "OK" if ok_lop else "HATA"))
log("kablo S1 duyarlilik:", duy, "kanal paylari:", kanal)
kablo["s1_lop"] = dict(L=S1["L"], serit=N1, demet=DM1, r_min=round(U1["R_min"], 3), r_sinir=round(R_DIN1, 2), r_10d=round(R_ON1, 2),
                       r_10d_ok=bool(U1["R_min"] >= R_ON1), u=dict(ri=S1O["ri"], ro=S1O["ro"], l=round(U1["l"], 2), delta=round(U1["delta"], 2),
                                                                     uc=round(U1["pol_max"], 2), F=U1["F"], artik=U1["artik"]),
                       en_kucuk_bosluk=b1["bosluk"], en_yakin=b1["en_yakin"], en_yakin_poz=b1["phi"], kosu_aci_min=round(a_min, 2),
                       alfa_min=S1["alfa_min"], kanal_pay=kanal, duyarlilik=duy, pozlar=satir1, ok=ok_lop,
                       ornek_nokta={str(phi): [vl(q) for q in KY.s1_poz(KK, phi, S1O)["nokta"][::4]] for phi in (PHI_S1[0], 45, PHI_S1[-1])},
                       not_="U temasli elastika (ayrilma noktasinda egrilik surekli); yarim daire tahmini (h/2) R'yi ~%19 fazla verir")

# gecis: G2 -> tambur bagi (gobek cercevesi); son 8 mm tambura sarilir (tambur haric)
g1 = KY.s1_gecis(KK, S1O)
rk_g, _, kos_g = KY.kose_yaricap(g1)
ken_g, boy_g = KY.cokgen(g1, 0.0, 0.0)
ken_g8, _ = KY.cokgen(g1, 0.0, 8.0)
hedef_g = GOB_DIGER + kol1[yana[0]] + kol1[20.0]
for _phi in (-45, 0, 45, 90, 135):
    hedef_g += [("%s (S1 %d)" % (a, _phi), s_) for a, s_ in grup_sekil(("Govde",), Pp(_phi).inverse(), kaynak=O.P) if "referans" not in a]
d_g, kim_g = KY.en_yakin(ken_g, hedef_g)
d_gt, _ = KY.en_yakin(ken_g8, TAMBUR)
gecis_ok = bool(rk_g >= R_SAB1 - 1e-9 and d_g - DM1["r_sabit"] >= -1e-6 and d_gt - DM1["r_sabit"] >= -1e-6)
kablo["s1_gecis"] = dict(boy=round(boy_g, 1), kose_r_max=round(rk_g, 2), r_sinir=round(R_SAB1, 2), en_kucuk_bosluk=round(d_g - DM1["r_sabit"], 2),
                         en_yakin=kim_g, tambur_bosluk_son8haric=round(d_gt - DM1["r_sabit"], 2), ok=gecis_ok,
                         not_="G2'de yassi demet (kalinlik x, genislik z) bagda (kalinlik radyal, genislik x) olur: ~24 mm'de 90 derece serbest burulma + "
                              "silindir uzerinde helis (geodezik; yassi seritte duzlem ici bukulme yok)")
log("kablo S1 gecis: boy %.1f, kose R %.1f (>= %.1f), bosluk %.2f (%s), tambura (son 8 mm haric) %.2f %s" % (
    boy_g, rk_g, R_SAB1, d_g - DM1["r_sabit"], kim_g, d_gt - DM1["r_sabit"], "OK" if gecis_ok else "HATA"))

# cikis: duvar bagi -> duvar boyunca -> radyal ice -> ped yarigi -> govde ici (sabit cerceve); gobek tum S1 pozlarinda
c1 = KY.s1_cikis(KK, S1O)
rk_c, _, kos_c = KY.kose_yaricap(c1)
ken_c, boy_c = KY.cokgen(c1, 0.0, 0.0)
ken_c4, _ = KY.cokgen(c1, UC, 0.0)                     # duvar bagindaki kablo bagi (ilk 4 mm) haric: orada demet duvara yaslanir
hedef_c = GOV1 + KAB1
for _phi in (-45, 0, 45, 90, 135):
    hedef_c += [("%s (S1 %d)" % (a, _phi), tasi(s_, Pp(_phi))) for a, s_ in TAMBUR + GOB_DIGER]
d_c, kim_c = KY.en_yakin(ken_c4, hedef_c)
cikis_ok = bool(rk_c >= R_SAB1 - 1e-9 and d_c - DM1["r_sabit"] >= -1e-6)
kablo["s1_cikis"] = dict(boy=round(boy_c, 1), kose_r_max=round(rk_c, 2), r_sinir=round(R_SAB1, 2), koseler=[[round(a, 2), i, round(b, 1)] for a, i, b in kos_c],
                         en_kucuk_bosluk=round(d_c - DM1["r_sabit"], 2), en_yakin=kim_c, ok=cikis_ok,
                         yarik=list(S1["cikis"]["yarik"]), jr_erkek=list(KK["jr_erkek"][:2]),
                         jr_gecer=bool(S1["cikis"]["yarik"][0] >= KK["jr_erkek"][0] + 0.5 and S1["cikis"]["yarik"][1] >= KK["jr_erkek"][1] + 0.5))
log("kablo S1 cikis: boy %.1f, kose R %.1f (>= %.1f), bosluk %.2f (%s) %s" % (boy_c, rk_c, R_SAB1, d_c - DM1["r_sabit"], kim_c,
                                                                            "OK" if cikis_ok else "HATA"))

# hafif carpisma: tambur (gobek) <-> kol zinciri (yalniz S2'ye bagli); kaset govdesi/kapagi (sabit) <-> kol zinciri (S1 x S2 x dirsek);
# tambur <-> kaset ve kabuk (S1'e bagli). Sinir kutusu on elemesi + distToShape.
def _enaz(a_list, b_list):
    best = (1e9, None, None)
    for a, sa in a_list:
        bba = App.BoundBox(sa.BoundBox)
        bba.enlarge(10.0)
        for b, sb in b_list:
            if not bba.intersect(sb.BoundBox):
                continue
            dd = sa.distToShape(sb)[0]
            if dd < best[0]:
                best = (dd, a, b)
    return best


TH_C = [yana[0], 10.0, 20.0, 45.0, 90.0, 120.0]
AL_C = [ar[0], 52.5, ar[1]]
car = dict(tambur_kol=[], kaset_kol=[], tambur_kaset=[])
for th in TH_C:
    kz = grup_sekil(("Kol",), Pr(th), kaynak=O.P) + grup_sekil(("UstKol",), Pr(th))
    d_, a_, b_ = _enaz(TAMBUR, kz)
    car["tambur_kol"].append(dict(th=th, bosluk=round(d_, 2), parca=b_))
for phi in range(int(A.OMUZ["one_arka_aralik"][0]), int(A.OMUZ["one_arka_aralik"][1]) + 1, 15):
    pp = Pp(phi)
    tb = [(a, tasi(s_, pp)) for a, s_ in TAMBUR]
    d_, a_, b_ = _enaz(tb, KAB1 + GOV1)
    car["tambur_kaset"].append(dict(phi=phi, bosluk=round(d_, 2), parca=b_))
    for th in TH_C:
        for al in AL_C:
            kz = [(a, tasi(s_, pp.multiply(Pr(th)))) for a, s_ in grup_sekil(("Kol",), None, kaynak=O.P) + grup_sekil(("UstKol",))]
            kz += [(a, tasi(s_, pp.multiply(Pr(th)).multiply(Pe(al)))) for a, s_ in grup_sekil(("OnKol", "El"))]
            d_, a_, b_ = _enaz(KASET, kz)
            car["kaset_kol"].append(dict(phi=phi, th=th, al=al, bosluk=round(d_, 2), kaset=a_, parca=b_))
car_ok = all(q["bosluk"] >= PAY for k in car for q in car[k])
car_ozet = {k: min(car[k], key=lambda q: q["bosluk"]) for k in car}
kablo["s1_carpisma"] = dict(ozet=car_ozet, satir=car, ok=bool(car_ok), sart=PAY,
                            not_="omuz/kol x tambur x kaset; tam tarama (kafa, iki kol, el pozlari) carpisma.py 6. adimda")
log("S1 hafif tarama:", {k: (v["bosluk"], v.get("parca"), v.get("phi"), v.get("th")) for k, v in car_ozet.items()}, "OK" if car_ok else "HATA")

# boy: servo basina uzatma (birlesim / S2 servosu -> S1 -> govde ici -> dagitim karti A), tahmini konnektor payi dahil
_dik = [V(*p) for p in S1["govde_dikey"]]
try:
    _sd = A.TABAN["servo_dagitim"]["A"]
    _dik.append(V(_sd[0], A.Y_DECK1 + 10.0, _sd[1]))
    _sd_not = "dagitim karti A (arayuz.TABAN servo_dagitim, y ~ kat ustu + 10, tahmini)"
except Exception:
    _sd_not = "dagitim karti konumu okunamadi: govde_dikey sonu"
_, boy_dik = KY.cokgen(_dik)
_bag = V(*S1["govde_ici"][-1]) + V(0, OMUZ_Y, 0)
boy_bag = (_dik[0] - _bag).Length
L_cik_ici = boy_c                                    # duvar bagi -> govde ici sonu (travers arkasi, x 0)
L_s1_toplam = boy_g + S1["L"] + L_cik_ici + boy_bag + boy_dik
uzat = []
for ad in ("dirsek servosu (MG996R)", "bilek servosu (MG996R)"):
    toplam = L_uz + L_s1_toplam + S1["jr_pay"]
    uzat.append(dict(servo=ad, uzatma_mm=round(toplam, 0),
                     parca=dict(birlesim_G2=round(L_uz, 1), gecis=round(boy_g, 1), s1_lop=S1["L"], cikis_govde_ici=round(L_cik_ici, 1),
                                govde_ici_dikeye=round(boy_bag, 1), dikey_dagitim=round(boy_dik, 1), konnektor_payi=S1["jr_pay"])))
# S2 servosu (DS3218, kablosu 300): G2'ye s2_servo_kablo (tahmini) + gecis + S1 lopu + cikis -> govde icinde birlesim (kalan boy)
s2_gerek = S1["s2_servo_kablo"] + boy_g + S1["L"]
_c_pts = KY.s1_cikis(KK, S1O)
_c_yarik = KY.cokgen(_c_pts[:4])[1]                     # duvar bagi -> yarigin ic agzi (x_ic)
s2_yarik = s2_gerek + _c_yarik
s2_kalan = KK["servo_kablo_boy"] - s2_yarik
# kablo ucu (disi JR, 14 mm) ped ic yuzunu tamamen gecmeli: kalan + (ped ic yuzu - x_ic) >= JR boyu
s2_kalan_sart = KK["jr_disi"][2] - (A.OMUZ_DUVAR["x0"] - S1["cikis"]["x_ic"])
uzat.append(dict(servo="S2 servosu (DS3218, 300 mm kablo)", servo_kablo_yariga_mm=round(s2_yarik, 1), kalan_mm=round(s2_kalan, 1),
                 kalan_sart_mm=round(s2_kalan_sart, 1),
                 birlesim="kabuk icinde yarik arkasinda" if s2_kalan >= s2_kalan_sart else "KABLO YETMEZ: gobekte birlesim gerekir",
                 uzatma_mm=round(L_cik_ici - _c_yarik + boy_bag + boy_dik + S1["jr_pay"] - max(s2_kalan, 0.0), 0),
                 ok=bool(s2_kalan >= s2_kalan_sart)))
kablo["s1_boy"] = dict(uzatma=uzat, dagitim=_sd_not, kaynak="KOL_KABLO s1 govde_ici / govde_dikey (taban_parcalar YOL 'Servo 6 V A', 15 Ekim)",
                       not_="kol basina 3 kablo (dirsek, bilek uzatmasi + S2 servosu); sol kol ayni (B karti). Konnektor payi tahmini.")
log("kablo S1 boy:", [(u["servo"], u.get("uzatma_mm"), u.get("kalan_mm")) for u in uzat])

kablo["ok"] = bool(all(kablo[k]["ok"] for k in ("dirsek_lop", "s2_lop", "yol_dirsek_servo", "yol_bilek_servo", "yol_ustkol", "yol_uzatma_kol",
                                               "s1_lop", "s1_gecis", "s1_cikis", "s1_carpisma"))
                   and all(g["ok"] for g in gecit) and all(b.get("ok", True) for b in boy) and all(u.get("ok", True) for u in kablo["s1_boy"]["uzatma"]))
log("kablo kontrolu", "OK" if kablo["ok"] else "HATA", "(S1 doner U-lop kaseti dahil)")


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
    sikma_bilezigi=dict(kelepce, kulak_kapanma_cakisma_mm3=round(kul_cakisma, 4)),
    kablo=kablo,
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
