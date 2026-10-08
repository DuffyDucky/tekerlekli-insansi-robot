# Kafa modulu - montaj, kontroller, modul ici tarama (pan x tilt), R62 uyumu, tork, baski analizi, FCStd + STEP + BOM + json
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
# Kontroller: her parca isValid + tek kati; ev pozunda modul ici cakisma (0,5 mm3); baglantilar (dayanma, eksen hizasi,
# civata ucu payi / kavrama); bagil hareket bosluklari (gruplar arasi); pan x tilt taramasi; kabuk R62 boyun acikligina
# uyum (analitik halka); tork (gercek parca kutleleri; tilt yercekimi + ivme, pan atalet + surtunme, tahmini profil);
# rulman yukleri; X2D baski analizi. Moduller arasi carpisma ve ana montaj 2. asamada (carpisma.py, montaj/), dokunulmaz.
import os, sys, json, math, time, csv
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import kafa_parcalar as KP
from kafa_parcalar import V, P, BAG, MG, K, YT, ZT, Ppan, Ptilt, grup_yer
import kafa_lib as L
from kafa_lib import cyl
import arayuz as A

t0 = time.time()
TOL = 0.5          # mm3
TEMAS = 0.01       # mm
BOSLUK_MIN = 0.3   # bagil hareketli parcalar arasi en kucuk bosluk (mm)


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))


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


def S(i):
    return P[i]["shape"]


IDX = {}
for k, p in enumerate(P):
    IDX.setdefault(p["ad"], k)
GERCEK = [p for p in P if p["tur"] != "Referans"]
log("kafa parca", len(P), "(gercek %d)" % len(GERCEK))

# ====================================================================== 1) gecerlilik + ev pozu modul ici cakisma
gecersiz = [p["ad"] for p in P if not p["shape"].isValid()]
coklu = [(p["ad"], p["kati"]) for p in P if p["kati"] != 1]
statik, n_cift = [], 0
for i in range(len(P)):
    for j in range(i + 1, len(P)):
        a, b = P[i], P[j]
        if a["tur"] == "Referans" or b["tur"] == "Referans" or not a["bb"].intersect(b["bb"]):
            continue
        n_cift += 1
        v = kes(a["shape"], b["shape"], a["bb"], b["bb"])
        if v > TOL or v < 0:
            statik.append((a["ad"], b["ad"], round(v, 3)))
log("gecersiz", len(gecersiz), "coklu", len(coklu), "ev pozu cakisma", len(statik), "cift", n_cift, statik[:5])


# ====================================================================== 2) baglanti kontrolleri
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


def eksen_disi_g(sh, nokta, yon):
    """Hacim merkezi ile (rulman/halka gibi simetrik parcalar icin)."""
    c = sh.Solids[0].CenterOfMass if len(sh.Solids) == 1 else sh.BoundBox.Center
    dd = c - V(*nokta)
    u = V(*yon)
    u.normalize()
    return (dd - u * dd.dot(u)).Length


bag_kontrol = []
for b in BAG:
    k = []
    civ = S(b["civata"])
    n0, u = b["nokta"], b["yon"]
    d_ = b["d"]
    ed = eksen_disi(civ, n0, u)
    k.append(("civata ekseni tasarim ekseninde", round(ed, 6), ed < 1e-6))
    _, t_uc = t_aralik(civ, n0, u)
    if b["tip"] == "cekic":
        som = S(b["somun"])
        ed2 = eksen_disi(som, n0, u)
        k.append(("cekic somun ayni eksende", round(ed2, 6), ed2 < 1e-6))
        y_uc = n0[1] - t_uc                                     # civata ucu (yerel y; traverse ust yuzu y = 0)
        y_somun_alt = -A.LIP - A.CEKIC_SOMUN["T"]
        k.append(("cekic somun ust yuzu dudak altinda (y = -%.1f)" % A.LIP, round(som.BoundBox.YMax + A.LIP, 4),
                  abs(som.BoundBox.YMax + A.LIP) < 1e-6))
        k.append(("civata ucu somunu %.1f mm geciyor (>= 0,5)" % (y_somun_alt - y_uc), round(y_somun_alt - y_uc, 3),
                  y_somun_alt - y_uc >= 0.5))
        k.append(("civata ucundan kanal tabanina %.1f mm (>= 1)" % (y_uc + A.KANAL_TABAN), round(y_uc + A.KANAL_TABAN, 3),
                  y_uc + A.KANAL_TABAN >= 1.0))
        dp = mesafe(S(b["pul"]), S(b["govde"]))
        dh = mesafe(civ, S(b["pul"]))
        dpl = mesafe(S(b["govde"]), S(b["plaka"]))
        k += [("pul servo yuvasi kulagina dayali", round(dp, 4), dp <= TEMAS), ("civata basi pula dayali", round(dh, 4), dh <= TEMAS),
              ("servo yuvasi plakaya dayali", round(dpl, 4), dpl <= TEMAS),
              ("plaka alt yuzu traverse ust yuzunde (y = 0)", round(S(b["plaka"]).BoundBox.YMin, 6),
               abs(S(b["plaka"]).BoundBox.YMin) < 1e-9)]
        dg = mesafe(civ, S(b["plaka"]))
        k.append(("civata plaka deliginde ortali (%.2f mm)" % dg, round(dg, 3), abs(dg - (A.CLEAR[d_] - d_) / 2) < 0.02))
    elif b["tip"] == "servo_kulak":
        som = S(b["somun"])
        ed2 = eksen_disi(som, n0, u)
        k.append(("somun ayni eksende", round(ed2, 6), ed2 < 1e-6))
        _, t_som = t_aralik(som, n0, u)
        cik = t_uc - t_som
        k.append(("civata ucu kontra somundan %.1f mm tasiyor (0,5...6)" % cik, round(cik, 3), 0.5 <= cik <= 6.0))
        dh = mesafe(civ, S(b["servo"]))
        dn = mesafe(som, S(b["govde"]))
        dsv = mesafe(S(b["servo"]), S(b["govde"]))
        k += [("civata basi servo kulagina dayali", round(dh, 4), dh <= TEMAS), ("somun plakaya dayali", round(dn, 4), dn <= TEMAS),
              ("servo kulagi plakaya dayali", round(dsv, 4), dsv <= TEMAS)]
        dg = mesafe(civ, S(b["govde"]))
        k.append(("civata plaka deliginde ortali (%.2f mm)" % dg, round(dg, 3), abs(dg - (A.CLEAR[d_] - d_) / 2) < 0.02))
    elif b["tip"] == "civata_horn":
        hrn = S(b["horn"])
        dh = mesafe(civ, S(b["govde"]))
        k.append(("civata basi parcaya dayali", round(dh, 4), dh <= TEMAS))
        ix = max(range(3), key=lambda i_: abs(u[i_]))

        def tp(duz):
            return (duz - n0[ix]) * u[ix]
        t_yak, t_uzak = tp(b["horn_yuz"][0]), tp(b["horn_yuz"][1])
        kav = min(t_uc, t_uzak) - t_yak
        k.append(("horn disine kavrama %.1f mm (horn %.1f)" % (kav, t_uzak - t_yak), round(kav, 3), kav >= 2.5))
        t_kasa = tp(b["kasa"])
        k.append(("civata ucundan servo kasasina %.1f mm" % (t_kasa - t_uc), round(t_kasa - t_uc, 3), t_kasa - t_uc >= 1.0))
        dho = mesafe(hrn, S(b["govde"]))
        k.append(("horn parcaya dayali", round(dho, 4), dho <= TEMAS))
    elif b["tip"] == "insert":
        ins = S(b["insert"])
        L_ins = A.INSERT[d_][1]
        kav = t_uc - b["agiz_t"]
        k.append(("M%d kavramasi %.1f mm (isil gomme somun %.1f)" % (d_, kav, L_ins), round(kav, 3), d_ <= kav <= L_ins))
        e_ = eksen_disi(ins, n0, u)
        k.append(("isil gomme somun civata ekseninde", round(e_, 6), e_ < 1e-6))
        ust = S(b["pul"]) if b.get("pul") is not None else S(b["bas_parca"])
        dl = [("civata basi %s dayali" % ("pula" if b.get("pul") is not None else "parcaya"), mesafe(civ, ust)),
              ("isil gomme somun yuvasinda", mesafe(ins, S(b["govde"]))),
              ("bagli parca govdeye dayali", mesafe(S(b["bas_parca"]), S(b["govde"])))]
        if b.get("pul") is not None:
            dl.append(("pul parcaya dayali", mesafe(S(b["pul"]), S(b["bas_parca"]))))
        k += [(a_, round(x_, 4), x_ <= TEMAS) for a_, x_ in dl]
        _, t_ins = t_aralik(ins, n0, u)
        k.append(("civata ucu isil gomme somun icinde (uc payi %.1f mm)" % (t_ins - t_uc), round(t_ins - t_uc, 3), t_uc <= t_ins + 1e-6))
    elif b["tip"] == "pt":
        kav = t_uc - b["agiz_t"]
        k.append(("M2 PT vida boss'a %.1f mm girer (>= 5, tahmini)" % kav, round(kav, 3), kav >= 5.0))
        dl = [("civata basi PCB'ye dayali", mesafe(civ, S(b["bas_parca"]))), ("PCB boss'a dayali", mesafe(S(b["bas_parca"]), S(b["govde"])))]
        k += [(a_, round(x_, 4), x_ <= TEMAS) for a_, x_ in dl]
    elif b["tip"] == "pim":
        ins = S(b["insert"])
        L_ins = A.INSERT[d_][1]
        kav = t_uc - (b["agiz"] - n0[0])
        k.append(("M5 kavramasi %.1f mm (isil gomme somun %.1f)" % (kav, L_ins), round(kav, 3), d_ <= kav <= L_ins))
        for ad_, sh_ in (("625ZZ ic bilezik", S(b["rul_i"])), ("625ZZ dis bilezik", S(b["rul_d"])), ("isil gomme somun", ins),
                         ("pul", S(b["pul"]))):
            e_ = eksen_disi(sh_, n0, u)
            k.append(("%s tilt ekseninde" % ad_, round(e_, 6), e_ < 1e-6))
        dl = [("pul 625ZZ ic bilezigine dayali", mesafe(S(b["pul"]), S(b["rul_i"]))),
              ("civata basi pula dayali", mesafe(civ, S(b["pul"]))),
              ("625ZZ ic bilezik catal dayamasina dayali", mesafe(S(b["rul_i"]), S(b["govde"]))),
              ("625ZZ dis bilezik sol yanak yuvasinda", mesafe(S(b["rul_d"]), S(b["catal"]))),
              ("isil gomme somun catal duvarinda", mesafe(ins, S(b["govde"])))]
        k += [(a_, round(x_, 4), x_ <= TEMAS) for a_, x_ in dl]
        dx = [("pim civatasi yanaga degmiyor", mesafe(civ, S(b["catal"]))),
              ("pul yanaga degmiyor", mesafe(S(b["pul"]), S(b["catal"]))),
              ("625ZZ ic bilezik yanaga degmiyor", mesafe(S(b["rul_i"]), S(b["catal"]))),
              ("625ZZ dis bilezik catala degmiyor", mesafe(S(b["rul_d"]), S(b["govde"]))),
              ("sol yanak catala degmiyor", mesafe(S(b["govde"]), S(b["catal"])))]
        k += [(a_ + " (%.2f mm)" % x_, round(x_, 3), x_ >= BOSLUK_MIN) for a_, x_ in dx]
    bag_kontrol.append(dict(ad=b["ad"], tip=b["tip"], kontroller=k, tamam=all(x[2] for x in k)))

# eksen hizasi ve oturmalar
PN, PY = K["pan_nokta"], K["pan_yon"]
TN, TY = K["tilt_nokta"], K["tilt_yon"]
eks = []
for ad_ in ("Pan servosu cikis mili", "Pan horn 25T aluminyum disk", "6808-2RS alt rulman (dis bilezik)", "6808-2RS alt rulman (ic bilezik)",
            "6808-2RS ust rulman (dis bilezik)", "6808-2RS ust rulman (ic bilezik)", "Boyun mili"):
    e_ = eksen_disi(S(IDX[ad_]), PN, PY) if ad_ == "Boyun mili" else eksen_disi_g(S(IDX[ad_]), PN, PY)
    eks.append(("%s pan ekseninde" % ad_, round(e_, 4), e_ < 0.05))
for ad_ in ("Tilt servosu cikis mili", "Tilt horn 25T aluminyum disk", "625ZZ rulman (ic bilezik)", "625ZZ rulman (dis bilezik)"):
    e_ = eksen_disi_g(S(IDX[ad_]), TN, TY)
    eks.append(("%s tilt ekseninde" % ad_, round(e_, 4), e_ < 0.05))
otur = [("boyun mili diski pan horn'una dayali", "Boyun mili", "Pan horn 25T aluminyum disk"),
        ("6808 alt dis bilezik yuvada", "6808-2RS alt rulman (dis bilezik)", "Rulman yuvasi"),
        ("6808 ust dis bilezik tablaya dayali", "6808-2RS ust rulman (dis bilezik)", "Rulman yuvasi"),
        ("6808 alt ic bilezik milde", "6808-2RS alt rulman (ic bilezik)", "Boyun mili"),
        ("6808 ust ic bilezik milde (omuz ustunde)", "6808-2RS ust rulman (ic bilezik)", "Boyun mili"),
        ("rulman yuvasi servo yuvasina dayali", "Rulman yuvasi", "Servo yuvasi"),
        ("egme catali mil flansina dayali", "Egme catali", "Boyun mili"),
        ("LCD paneli ekran yuvasi kenarina dayali", "Yuz ekrani Waveshare 7in HDMI LCD (C)", "Yuz kabugu (on)"),
        ("vizor on yuze dayali", "Vizor (siyah akrilik)", "Yuz kabugu (on)"),
        ("on kabuk kafa tablasi boss'una dayali", "Yuz kabugu (on)", "Kafa iskeleti"),
        ("arka kabuk kafa tablasi boss'una dayali", "Arka kafa kabugu", "Kafa iskeleti"),
        ("arka kabuk dikis dili on kabuga oturuyor", "Arka kafa kabugu", "Yuz kabugu (on)")]
for ad_, a_, b_ in otur:
    d_ = mesafe(S(IDX[a_]), S(IDX[b_]))
    eks.append((ad_, round(d_, 4), d_ <= TEMAS))
# eksenel yuk yolu: ust rulman ic bileziginin ust yuzu = mil omzu alt yuzu; dis bilezigin alt yuzu = yuva tablasi
r2i = S(IDX["6808-2RS ust rulman (ic bilezik)"]).BoundBox
omuz_kesit = KP.P[KP.I_MIL]["shape"].common(cyl(22.2, (0, KP.Y_OMUZ[0], 0), (0, KP.Y_OMUZ[0] + 0.2, 0)).cut(
    cyl(20.1, (0, KP.Y_OMUZ[0] - 1, 0), (0, KP.Y_OMUZ[0] + 1, 0)))).Volume
eks.append(("mil omzu ust 6808 ic bilezigine basar (eksenel yuk)", round(omuz_kesit, 3), omuz_kesit > 0.5 and abs(r2i.YMax - KP.Y_OMUZ[0]) < 1e-6))
tabla_kesit = KP.P[KP.I_RY]["shape"].common(cyl(25.9, (0, KP.Y_R2[0] - 0.2, 0), (0, KP.Y_R2[0], 0)).cut(
    cyl(24.5, (0, KP.Y_R2[0] - 1, 0), (0, KP.Y_R2[0] + 1, 0)))).Volume
eks.append(("ust 6808 dis bilezigi yuva tablasina oturur", round(tabla_kesit, 3), tabla_kesit > 0.5))
bag_kontrol.append(dict(ad="Eksen hizasi ve oturmalar", tip="eksen", kontroller=eks, tamam=all(x[2] for x in eks)))
log("baglanti kontrol %d/%d tamam" % (sum(1 for s in bag_kontrol if s["tamam"]), len(bag_kontrol)))
for s in bag_kontrol:
    if not s["tamam"]:
        log("  HATA", s["ad"], [x for x in s["kontroller"] if not x[2]])

# ====================================================================== 3) bagil hareket bosluklari (ev pozu, gruplar arasi)
EKSENEL = {frozenset(x) for x in (("Pan servosu cikis mili", "Pan horn 25T aluminyum disk"),
                                   ("Pan servosu cikis mili", "Pan horn merkez vidasi M3"),
                                   ("Tilt servosu cikis mili", "Tilt horn 25T aluminyum disk"),
                                   ("Tilt servosu cikis mili", "Tilt horn merkez vidasi M3"),
                                   ("6808-2RS alt rulman (dis bilezik)", "6808-2RS alt rulman (ic bilezik)"),
                                   ("6808-2RS ust rulman (dis bilezik)", "6808-2RS ust rulman (ic bilezik)"),
                                   ("625ZZ rulman (ic bilezik)", "625ZZ rulman (dis bilezik)"))}
bagil = []
GRUPLAR = ("Govde", "Pan", "Kafa")
for i in range(len(P)):
    for j in range(i + 1, len(P)):
        a, b = P[i], P[j]
        if a["tur"] == "Referans" or b["tur"] == "Referans" or a["grup"] == b["grup"]:
            continue
        if frozenset((a["ad"], b["ad"])) in EKSENEL:
            continue
        ba, bb = App.BoundBox(a["bb"]), b["bb"]
        ba.enlarge(3.0)
        if not ba.intersect(bb):
            continue
        d_ = mesafe(a["shape"], b["shape"])
        bagil.append((round(d_, 3), a["ad"], b["ad"]))
bagil.sort()
bagil_hata = [x for x in bagil if x[0] < BOSLUK_MIN]
log("bagil bosluk: en kucuk", bagil[:4], "hata", len(bagil_hata))

# ====================================================================== 4) modul ici tarama: pan x tilt
GOV = [p for p in P if p["grup"] == "Govde" and p["tur"] != "Referans"]
PAN = [p for p in P if p["grup"] == "Pan"]
KAF = [p for p in P if p["grup"] == "Kafa"]


def carp(hareketli, pl, sabit, sabit_pl=None):
    hits = []
    for a in hareketli:
        sa = tasi(a["shape"], pl)
        ba = sa.BoundBox
        for b in sabit:
            if frozenset((a["ad"], b["ad"])) in EKSENEL:
                continue
            sb = b["shape"] if sabit_pl is None else tasi(b["shape"], sabit_pl)
            bbb = sb.BoundBox
            if not ba.intersect(bbb):
                continue
            v = kes(sa, sb, ba, bbb)
            if v > TOL or v < 0:
                hits.append((a["ad"], b["ad"], round(v, 1)))
    return hits


def en_yakin(hareketli, pl, sabit, esik=8.0):
    best = (1e9, None, None)
    for a in hareketli:
        sa = tasi(a["shape"], pl)
        ba = App.BoundBox(sa.BoundBox)
        ba.enlarge(esik)
        for b in sabit:
            if frozenset((a["ad"], b["ad"])) in EKSENEL or not ba.intersect(b["bb"]):
                continue
            d_ = mesafe(sa, b["shape"])
            if d_ < best[0]:
                best = (d_, a["ad"], b["ad"])
    return best


# 4a) pan grubu x govde (yalniz pan acisina bagli; +-180 bilgi icin)
PSI_TUM = list(range(-180, 181, 15))
pan_gov = {psi: carp(PAN, Ppan(psi), GOV) for psi in PSI_TUM}
log("pan x govde bitti", {k: v for k, v in pan_gov.items() if v})
# 4b) kafa x pan grubu (yalniz tilt acisina bagli)
kaf_pan = {th: carp(KAF, Ptilt(th), PAN) for th in KP.THS}
log("kafa x pan bitti", {k: v[:2] for k, v in kaf_pan.items() if v})
# 4c) kafa x govde: pan x tilt
kaf_gov = {}
for psi in KP.PSIS:
    for th in KP.THS:
        kaf_gov[(psi, th)] = carp(KAF, Ppan(psi).multiply(Ptilt(th)), GOV)
log("kafa x govde bitti", {k: v[:2] for k, v in kaf_gov.items() if v})


def serbest_th(th):
    return not kaf_pan[th] and all(not kaf_gov[(psi, th)] for psi in KP.PSIS)


tmax = 0
for th in [t for t in KP.THS if t >= 0]:
    if serbest_th(th):
        tmax = th
    else:
        break
tmin = 0
for th in sorted([t for t in KP.THS if t <= 0], reverse=True):
    if serbest_th(th):
        tmin = th
    else:
        break
pmax = 0
for psi in [p_ for p_ in PSI_TUM if p_ >= 0]:
    if not pan_gov[psi]:
        pmax = psi
    else:
        break
pmin = 0
for psi in sorted([p_ for p_ in PSI_TUM if p_ <= 0], reverse=True):
    if not pan_gov[psi]:
        pmin = psi
    else:
        break
ilk_carpan = {}
for th in KP.THS:
    if th > tmax and (kaf_pan[th] or any(kaf_gov[(psi, th)] for psi in KP.PSIS)):
        ilk_carpan["+"] = (th, (kaf_pan[th] or [x for psi in KP.PSIS for x in kaf_gov[(psi, th)]])[:4])
        break
for th in sorted(KP.THS, reverse=True):
    if th < tmin and (kaf_pan[th] or any(kaf_gov[(psi, th)] for psi in KP.PSIS)):
        ilk_carpan["-"] = (th, (kaf_pan[th] or [x for psi in KP.PSIS for x in kaf_gov[(psi, th)]])[:4])
        break
TAR = K["tilt_aralik"]
aralik_ok = tmin <= TAR[0] and tmax >= TAR[1]
log("tilt serbest %d...%d (arayuz %s, ok %s), pan serbest %d...%d" % (tmin, tmax, TAR, aralik_ok, pmin, pmax), ilk_carpan)
# en kucuk bosluklar (kafa x pan, tilt araliginda 5 derece) ve kafa x govde (pan +-90, tilt sinirlari)
bosluk = {}
for th in [t for t in KP.THS if TAR[0] <= t <= TAR[1]]:
    d_, a_, b_ = en_yakin(KAF, Ptilt(th), PAN)
    bosluk[str(th)] = (round(d_, 2), a_, b_)
bosluk_gov = {}
for psi in (-90, 0, 90):
    for th in (TAR[0], 0, TAR[1]):
        d_, a_, b_ = en_yakin(KAF, Ppan(psi).multiply(Ptilt(th)), GOV, esik=40.0)
        bosluk_gov["%d,%d" % (psi, th)] = (round(d_, 2), a_, b_)
log("bosluk kafa x pan", min(bosluk.values()), "kafa x govde", min(bosluk_gov.values()))

# ====================================================================== 5) kabuk R62 boyun acikligi (analitik)
# Kabuk ust kapagi global y 982...985 (yerel 7...10), R62 delik (yerel y -10...30 arasi bosaltilmis: kabuk_parcalar).
# Kapak halkasi = r >= 62, yerel y 7...10. Sabit parcalar bu halkaya, hareketli parcalar tum pozlarda.
Y0_KABUK = A.KAFA["taban_y"]
y_kapak = (A.GOVDE_Y1 - A.KABUK_T - Y0_KABUK, A.GOVDE_Y1 - Y0_KABUK)          # 7, 10
halka = cyl(400.0, (0, y_kapak[0], 0), (0, y_kapak[1], 0)).cut(cyl(A.BOYUN_ACIKLIK_R, (0, y_kapak[0] - 1, 0), (0, y_kapak[1] + 1, 0)))
r62 = []
for p in GOV:
    if p["bb"].YMin > y_kapak[1] + 30 or p["bb"].YMax < y_kapak[0] - 30:
        continue
    r62.append((round(mesafe(p["shape"], halka), 2), p["ad"]))
r62.sort()
# en buyuk yaricap (kapak seviyesinde, y 7...10)
dilim = cyl(300.0, (0, y_kapak[0], 0), (0, y_kapak[1], 0))
r_max = 0.0
for p in GOV:
    c = p["shape"].common(dilim)
    if c.Volume > 1e-6:
        r_max = max(r_max, max(math.hypot(v.Point.x, v.Point.z) for v in c.Vertexes))
        for e in c.Edges:
            for q in e.discretize(24):
                r_max = max(r_max, math.hypot(q.x, q.z))
# hareketli parcalarin en alt noktasi (tum pozlar) ve o pozda yaricapi
alt = (1e9, None)
for psi in KP.PSIS:
    for th in KP.THS:
        if not (TAR[0] <= th <= TAR[1]):
            continue
        pl = Ppan(psi).multiply(Ptilt(th))
        for p in KAF:
            yb = tasi(p["shape"], pl).BoundBox.YMin
            if yb < alt[0]:
                alt = (yb, (psi, th, p["ad"]))
y_pan_min = min(p["bb"].YMin for p in PAN)
log("R62: sabit parcalarin kapak halkasina en kucuk mesafesi", r62[:3], "kapak seviyesinde en buyuk yaricap %.1f" % r_max,
    "kafa en alt y %.1f" % alt[0], alt[1], "pan grubu en alt y %.1f" % y_pan_min)

# ====================================================================== 6) kutle, agirlik merkezi, tork
GR = {}
for g in GRUPLAR:
    m = sum(p["kutle"] for p in P if p["grup"] == g)
    c = V(0, 0, 0)
    for p in P:
        if p["grup"] == g:
            c = c + p["merkez"] * (p["kutle"] / m)
    GR[g] = (m, c)
G = 9.81


def atalet(gruplar, pl_map, eksen_n, eksen_u):
    """Eksene gore kutle atalet momenti (kg*m2): parca kutlesi uniform dagitilmis (MatrixOfInertia hacim icin)."""
    u = V(*eksen_u)
    u.normalize()
    n = V(*eksen_n)
    I_ = 0.0
    for p in P:
        if p["grup"] not in gruplar or p["kutle"] <= 0:
            continue
        sh = tasi(p["shape"], pl_map[p["grup"]])
        rho = p["kutle"] / max(sh.Volume, 1e-9)          # g/mm3
        sols = sh.Solids
        for s in sols:
            Mi = s.MatrixOfInertia                          # mm5 (birim yogunluk, kutle merkezine gore)
            Iuu = (Mi.A11 * u.x * u.x + Mi.A22 * u.y * u.y + Mi.A33 * u.z * u.z + 2 * Mi.A12 * u.x * u.y + 2 * Mi.A13 * u.x * u.z
                   + 2 * Mi.A23 * u.y * u.z)
            c = s.CenterOfMass - n
            r2 = (c - u * c.dot(u)).Length ** 2
            I_ += rho * (Iuu + s.Volume * r2)              # g*mm2
    return I_ * 1e-9                                         # kg*m2


# tilt: kafa grubunun yercekimi momenti (pan acisindan bagimsiz) + ivme momenti
mK, cK = GR["Kafa"]
I_tilt = atalet(("Kafa",), {"Kafa": App.Placement()}, (0, YT, ZT), K["tilt_yon"])
ALFA = 4 * math.radians(60) / 0.4 ** 2       # 60 derece 0,4 s'de, ucgen hiz profili (tahmini): 26,2 rad/s2
OMEGA = 2 * math.radians(60) / 0.4           # tepe hiz 5,2 rad/s (MG996R bossta ~6,2 rad/s @4,8 V)
STALL = 9.4                                  # kg*cm MG996R @4,8 V (dirsek ile ayni kaynak)
tilt_egri = []
for th in range(int(TAR[0]), int(TAR[1]) + 1, 5):
    c = Ptilt(th).multVec(cK)
    tg = mK * (c.z - ZT) / 1e4               # g*mm -> kg*cm  (+: one dogru devirir)
    tilt_egri.append(dict(th=th, yercekimi_kgcm=round(tg, 3)))
tg_max = max(abs(e["yercekimi_kgcm"]) for e in tilt_egri)
th_tg = max(tilt_egri, key=lambda e: abs(e["yercekimi_kgcm"]))["th"]
ti = I_tilt * ALFA / 9.81 * 100              # N*m -> kg*cm
tilt_t = tg_max + ti
# tum acilarda en kotu (tam tur, bilgi): kutle merkezinin eksene uzakligi
r_cg = math.hypot(cK.y - YT, cK.z - ZT)
tilt_tork = dict(kutle_g=round(mK, 1), am=[round(cK.x, 2), round(cK.y, 2), round(cK.z, 2)], eksen=[YT, ZT],
                 am_eksen_mm=round(r_cg, 1), yercekimi_max_kgcm=round(tg_max, 2), yercekimi_max_th=th_tg,
                 tam_tur_max_kgcm=round(mK * r_cg / 1e4, 2), I_kgm2=round(I_tilt, 6), alfa_rad_s2=round(ALFA, 1),
                 ivme_kgcm=round(ti, 3), toplam_kgcm=round(tilt_t, 2), stall_kgcm=STALL, pay=round(STALL / tilt_t, 2),
                 egri=tilt_egri)
# pan: atalet (Pan + Kafa, tilt 0 ve sinirlar) x ivme + surtunme (6808 cifti, kablo) - tahmini
I_pan = {}
for th in (TAR[0], 0, TAR[1]):
    I_pan[str(th)] = atalet(("Pan", "Kafa"), {"Pan": App.Placement(), "Kafa": Ptilt(th)}, (0, 0, 0), K["pan_yon"])
I_pmax = max(I_pan.values())
mPK = GR["Pan"][0] + mK
cPK = (GR["Pan"][1] * GR["Pan"][0] + cK * mK) * (1.0 / mPK)
F_ax = mPK / 1000 * G                                          # N, ust rulmanda eksenel
M_dev = mPK / 1000 * G * math.hypot(cPK.x, cPK.z) / 1000        # N*m devirme (kutle merkezi eksenden kacik)
ARA_RUL = (KP.Y_R2[0] + KP.Y_R2[1]) / 2 - (KP.Y_R1[0] + KP.Y_R1[1]) / 2   # 11 mm rulman merkezleri arasi
F_rad = M_dev / (ARA_RUL / 1000)                                # N, her rulmanda radyal (cift kuvvet)
MU = 0.0015                                                     # bilyali rulman surtunme katsayisi (tahmini, tipik)
T_rul = MU * (F_ax + 2 * F_rad) * 0.023                         # N*m (ortalama yaricap 23 mm)
T_kablo = 0.03                                                  # N*m kablo halkasi direnci (tahmini, ~0,3 kg*cm)
T_ivme = I_pmax * ALFA
pan_t = (T_ivme + T_rul + T_kablo) / 9.81 * 100
pan_tork = dict(kutle_g=round(mPK, 1), am=[round(cPK.x, 2), round(cPK.y, 2), round(cPK.z, 2)],
                I_kgm2={k: round(v, 6) for k, v in I_pan.items()}, alfa_rad_s2=round(ALFA, 1),
                ivme_kgcm=round(T_ivme / 9.81 * 100, 3), rulman_kgcm=round(T_rul / 9.81 * 100, 4),
                kablo_kgcm=round(T_kablo / 9.81 * 100, 2), toplam_kgcm=round(pan_t, 2), stall_kgcm=STALL, pay=round(STALL / pan_t, 1),
                rulman=dict(eksenel_N=round(F_ax, 2), devirme_Nm=round(M_dev, 4), rulman_arasi_mm=ARA_RUL, radyal_N=round(F_rad, 1),
                            not_="6808: eksenel yuk ust rulmanda (mil omzu -> ic bilezik -> dis bilezik -> yuva tablasi); "
                                 "devirme momenti iki rulmanda kuvvet cifti; pan servosu mili yalniz dondurur"))
# tilt servosu milindeki radyal pay (horn tarafi): kafa agirligi iki mesnet arasinda (625ZZ ve horn)
x_625 = (KP.X_RUL[0] + KP.X_RUL[1]) / 2
x_horn = (KP.X_TH[0] + KP.X_TH[1]) / 2
pay_horn = (cK.x - x_625) / (x_horn - x_625)
tilt_tork["mesnet"] = dict(x_625=x_625, x_horn=x_horn, horn_payi=round(pay_horn, 3), horn_N=round(mK / 1000 * G * pay_horn, 2),
                           pim_N=round(mK / 1000 * G * (1 - pay_horn), 2))
log("tork tilt %.2f kg*cm (yercekimi %.2f @%d, ivme %.3f) pay %.1f; pan %.2f kg*cm pay %.1f; rulman eksenel %.1f N radyal %.1f N" % (
    tilt_t, tg_max, th_tg, ti, STALL / tilt_t, pan_t, STALL / pan_t, F_ax, F_rad))

# ====================================================================== 7) baski analizi (X2D)
baski = []
for ad, bd in KP.BASKI.items():
    p = P[IDX[ad]]
    r = L.baski_analiz(ad, p["shape"], bd["yukari"], p["doluluk_baski"])
    r["yon"] = bd["yon"]
    r["grup"] = p["grup"]
    baski.append(r)
    log("baski %-18s %s sigar=%s cikinti %.3f destek sorunu %d" % (ad, r["olcu"], r["sigar"], r["cikinti_orani"], r["destek_sorun_sayi"]),
        r["destek_sorun"][:2])

# ====================================================================== 8) kutle, AM
M = sum(p["kutle"] for p in P)
CG = V(0, 0, 0)
for p in P:
    CG = CG + p["merkez"] * (p["kutle"] / M)
kutle_tur = {}
for p in P:
    kutle_tur[p["tur"]] = kutle_tur.get(p["tur"], 0.0) + p["kutle"]
log("kutle %.1f g, AM (%.1f, %.1f, %.1f)" % (M, CG.x, CG.y, CG.z))

# ====================================================================== 9) kaydet: FCStd (Assembly) + STEP + BOM
doc = App.newDocument("KafaMontaj")
asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
asm.Label = "Kafa"
jg = asm.newObject("Assembly::JointGroup", "Joints")
jg.Label = "Eklemler"
groups = {}
for g, lab in (("Govde", "Boyun_traverse_sabit"), ("Pan", "Pan_dikey_eksende_doner"), ("Kafa", "Kafa_tilt_ekseninde_doner"),
               ("Referans", "Kablo_yolu_gosterim")):
    gp_ = asm.newObject("App::Part", g)
    gp_.Label = lab
    groups[g] = gp_
feat = []
for k, p in enumerate(P):
    o = groups[p["grup"]].newObject("Part::Feature", "K%03d" % k)
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
    JointObject.GroundedJoint(gj, groups["Govde"])
    first = {g: next(o for o, p in zip(feat, P) if p["grup"] == g and p["tur"] == "Baski") for g in ("Govde", "Pan", "Kafa")}

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
    revolute("Pan", "Pan (MG996R)", "Govde", "Pan", K["pan_nokta"], App.Rotation(V(1, 0, 0), -90), K["pan_aralik"][0], K["pan_aralik"][1])
    revolute("Tilt", "Tilt (MG996R)", "Pan", "Kafa", K["tilt_nokta"], App.Rotation(V(0, 1, 0), 90), TAR[0], TAR[1])
    asm.solve()
    doc.recompute()
    joints_ok = True
except Exception as e:
    joints_ok = repr(e)
for g in groups.values():
    g.Placement = App.Placement()
doc.recompute()
doc.saveAs(os.path.join(HERE, "kafa-montaj.FCStd"))
App.closeDocument(doc.Name)
Part.Compound([p["shape"] for p in GERCEK]).exportStep(os.path.join(HERE, "kafa-montaj.step"))
step_kati = len(Part.read(os.path.join(HERE, "kafa-montaj.step")).Solids)
bom = {}
for p in GERCEK:
    if p["kod"].startswith("("):
        continue
    key = (p["tur"], p["kod"] if p["tur"] not in ("Baski",) else p["ad"])
    bom.setdefault(key, dict(adet=0, kutle=0.0))
    bom[key]["adet"] += 1
    bom[key]["kutle"] += p["kutle"]
with open(os.path.join(HERE, "kafa-bom.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Tur", "Kalem", "Adet", "Toplam kutle (g)"])
    for (t, kod), v in sorted(bom.items()):
        w.writerow([t, kod, v["adet"], "%.1f" % v["kutle"]])
log("kayit: STEP kati", step_kati, "eklem", joints_ok)


# ====================================================================== 10) analiz json (2. asama bunu okur)
def vl(v):
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]


def bbl(b):
    return [round(x, 2) for x in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]


out = dict(
    modul="kafa",
    koordinat="kafa yereli: orijin traversin ust yuzu ortasi (global 0, %.1f, 0), X sag, Y yukari, Z ileri (mm); "
              "global = yerel + arayuz.MODULLER['kafa'] konumu" % A.KAFA["taban_y"],
    yerlesim=A.MODULLER["kafa"],
    parca_sayisi=len(GERCEK), referans_sayisi=len(P) - len(GERCEK), baski_sayisi=len(KP.BASKI),
    parcalar=[dict(i=k, ad=p["ad"], grup=p["grup"], tur=p["tur"], malzeme=p["malzeme"], kod=p["kod"], kutle_g=round(p["kutle"], 2),
                   hacim_mm3=round(p["hacim"], 1), merkez=vl(p["merkez"]), bb=bbl(p["bb"]), patlat=p["patlat"], not_=p["not_"])
              for k, p in enumerate(P)],
    gruplar=dict(
        Govde=dict(hareket="sabit (traverse)", baglanti="traversin ust kanalina 2x M6 + cekic somun (x = +-40, z = 0)",
                   parca=[p["ad"] for p in P if p["grup"] == "Govde"]),
        Pan=dict(hareket="Ppan(psi)", parca=[p["ad"] for p in P if p["grup"] == "Pan"]),
        Kafa=dict(hareket="Ppan(psi) * Ptilt(th)", parca=[p["ad"] for p in P if p["grup"] == "Kafa"]),
        Referans=dict(hareket="kablo gosterimi; carpisma taramasina girmez", parca=[p["ad"] for p in P if p["grup"] == "Referans"])),
    eklemler=[
        dict(ad="Pan", tip="revolute", ust="Govde", alt="Pan", nokta=list(K["pan_nokta"]), yon=list(K["pan_yon"]),
             aralik=list(K["pan_aralik"]), ev=0.0, serbest_aralik=[pmin, pmax], servo="MG996R (180 derece)",
             not_="+aci yuz robotun sagina; servo orta konumu (90) = pan 0 olacak sekilde horn takilir; kablo halkasi +-90 icin"),
        dict(ad="Tilt", tip="revolute", ust="Pan", alt="Kafa", nokta=list(K["tilt_nokta"]), yon=list(K["tilt_yon"]),
             aralik=list(TAR), ev=0.0, serbest_aralik=[tmin, tmax], servo="MG996R (180 derece)",
             not_="+aci basi one eger (yuz asagi); karsi yatak 625ZZ sol yanakta")],
    kinematik="T_Pan = Ppan(psi); T_Kafa = Ppan(psi) * Ptilt(th); Ppan = Rotation((0,1,0), psi) merkez (0,0,0); "
              "Ptilt = Rotation((1,0,0), th) merkez (0, %.1f, %.1f) (kafa_parcalar.grup_yer)" % (YT, ZT),
    tarama_onerisi=dict(pan=list(range(-90, 91, 15)), tilt=[int(TAR[0]), -10, 0, 10, 20, int(TAR[1])],
                        hedefler="iskelet (traverse ust yuzu ve omuz yuvalari), kabuk (ust kapak R62 halkasi, gogus bandi), "
                                 "omuz (sag/sol; kol one 135 derece kalkinca kafa yanina yaklasir), dirsek (kol zinciri, el kafaya)",
                        haric="kafa 'Referans' grubu (kablo gosterimi); traverse ust kanalindaki cekic somunlar iskelet profiline "
                              "temasli (tasarim geregi, kanal icinde)",
                        not_="kafa grubu en genis: x +-105, z -65...85 (pan donunce r 135); omuz/kol taramasinda pan +-90 sinirlari"),
    gecersiz=gecersiz, coklu_kati=coklu, statik=statik, cift_sayisi=n_cift, tolerans_mm3=TOL,
    baglanti_kontrol=bag_kontrol,
    bagil_bosluk=dict(en_kucuk=bagil[:12], hata=bagil_hata, esik_mm=BOSLUK_MIN),
    tarama=dict(psi=KP.PSIS, psi_tum=PSI_TUM, th=KP.THS,
                pan_govde={str(k): v for k, v in pan_gov.items()},
                kafa_pan={str(k): v for k, v in kaf_pan.items()},
                kafa_govde={"%d,%d" % k: v for k, v in kaf_gov.items()},
                serbest_tilt=[tmin, tmax], serbest_pan=[pmin, pmax], ilk_carpan=ilk_carpan, aralik=list(TAR), aralik_ok=aralik_ok,
                bosluk_kafa_pan=bosluk, bosluk_kafa_govde=bosluk_gov,
                not_="kafa x pan yalniz tilt acisina, pan x govde yalniz pan acisina bagli; kafa x govde pan x tilt"),
    r62=dict(aciklik_r=A.BOYUN_ACIKLIK_R, kapak_y_yerel=list(y_kapak), sabit_en_kucuk=r62[:6], kapak_seviyesi_r_max=round(r_max, 2),
             kafa_en_alt_y=round(alt[0], 2), kafa_en_alt_poz=alt[1], pan_en_alt_y=round(y_pan_min, 2),
             not_="kapak seviyesinde yalniz sabit boyun (servo yuvasi + plaka kulaklari) var; hareketli parcalar y >= %.1f" % y_pan_min),
    tork=dict(tilt=tilt_tork, pan=pan_tork, profil="60 derece 0,4 s'de ucgen hiz profili (tahmini): alfa %.1f rad/s2, tepe hiz %.1f rad/s" % (ALFA, OMEGA),
              stall_kaynak="MG996R datasheet 9,4 kg*cm @4,8 V (11 @6 V); dirsek ile ayni"),
    grup={k: dict(m=round(v[0], 1), am=vl(v[1])) for k, v in GR.items()},
    baski=baski, doluluk=KP.DOLULUK, doluluk_kabuk=A.KABUK_DOLULUK, yazici=dict(A.YAZICI),
    kutle_g=round(M, 1), kutle_tur={k: round(v, 1) for k, v in kutle_tur.items()}, agirlik_merkezi=vl(CG),
    bom=[[t, kod, v["adet"], round(v["kutle"], 1)] for (t, kod), v in sorted(bom.items())],
    step_kati=step_kati, joints_ok=joints_ok,
    arayuz=dict((k, (list(v) if isinstance(v, tuple) else v)) for k, v in A.KAFA.items()),
    olcu=dict(Y_PK=KP.Y_PK, Y_R1=KP.Y_R1, Y_R2=KP.Y_R2, Y_FL=KP.Y_FL, Y_CB=KP.Y_CB, Y_TABLA=KP.Y_TABLA, Z_DIKIS=KP.Z_DIKIS,
              Z_LCD=KP.Z_LCD, Y_LCD=KP.Y_LCD, Y_CAM=KP.Y_CAM, Z_CAM=KP.Z_CAM, ACIKLIK=KP.ACIKLIK, kafa=[KP.KX, KP.KY0, KP.KY1, KP.KZ0, KP.KZ1]),
    kablo_yolu=[list(p) for p in KP.YOL],
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "kafa-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("bitti")
