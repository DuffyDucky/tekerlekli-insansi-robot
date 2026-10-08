# Kabuk modulu (V3) - PARCALAR: govde kabugu (4 bant x sag/sol + arka kapak), taban etegi (3 bant x sag/sol), Nextion
# gogus ekrani, iskelete baglanti braketleri ve tum baglanti elemanlari. Import edilebilir: kabuk_montaj.py (kontroller
# + kayit), ../carpisma.py ve ../montaj/moduller.py kullanir. Koordinat = global (arayuz.py), mm.
#
# Yapi
# - Kabuk = dis zarf - ic zarf (cizgisel loft, arayuz.GOVDE_KESIT / ETEK_KESIT). Orta zarf (T/2) duvari dis ve ic
#   yariya ayirir. Parca = (dis yari  kesisim  dis hucre) + (ic yari  kesisim  ic hucre). Ic hucrenin siniri dikisten
#   KABUK_BINDIRME kadar kaydirilinca bir parcanin ic yarisi komsusunun dis yarisinin arkasina "dil" olarak uzanir
#   (bindirme). Dilde isil gomme somunlu boss, komsunun dudagindan M3 ISO 7380 civata.
# - Yatay plakalarda (govde ust kapagi, etek ust plakasi) dil yok (alin birlesim): duz basilan plakada dil 12 mm
#   havada kalirdi.
# - Baski yonu parca basina (BASKI): boss'lar baski asagi yonune damla (teardrop) sekilli.
import os, sys, math, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from kabuk_lib import *   # noqa
import arayuz as A

t0 = time.time()
UP, DOWN = V(0, 1, 0), V(0, -1, 0)
T = A.KABUK_T
H = T / 2
W = A.KABUK_BINDIRME
BIG = 3000.0
P = []          # parcalar
BAG = []        # iskelete baglantilar (kontroller icin)
VIDA = []       # bindirme ve ekran civatalari (kontroller icin)
BASKI = {}      # baski parcasi adi -> dict(yukari=V (robot koordinatinda baski yukari yonu), yon=aciklama)


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))


def kutu(x0=-BIG, x1=BIG, y0=-BIG, y1=BIG, z0=-BIG, z1=BIG):
    return box(x0, x1, y0, y1, z0, z1)


def add(ad, grup, shape, tur, malzeme, kod=None, renk="gri", patlat=(0, 0, 0), not_="", kutle=None):
    P.append(dict(ad=ad, grup=grup, shape=shape, tur=tur, malzeme=malzeme, kod=kod or ad, renk=renk,
                  patlat=list(patlat), not_=not_, kutle_sabit=kutle))
    return len(P) - 1


GK, EK = A.GOVDE_KESIT, A.ETEK_KESIT
YK = [-BIG] + list(A.GOVDE_DIKIS) + [BIG]                  # dis hucre siniri (dikis)
YKI = [-BIG] + [y + W for y in A.GOVDE_DIKIS] + [BIG]      # ic hucre siniri (dil kadar yukarida)
Y_KAPAK_PLAKA = A.GOVDE_Y1 - T - 3.0                       # bunun ustunde (ust kapak) dil yok
Y_ETEK_PLAKA = A.Y_COV1 - T - 4.0                          # etek ust plakasi bolgesi

# ====================================================================== GOVDE KABUGU
O = zarf(GK, 0.0)
M = zarf(GK, H)
I = zarf(GK, T)
S = O.cut(I)
OD = A.OMUZ_DUVAR
for sx in (1, -1):        # omuz bolgesinde 5 mm duz yan duvar (omuz referansi x 147...152) + O84 delik
    x0 = OD["x0"] if sx > 0 else -OD["x1"]
    S = S.fuse(Part.makeCylinder(OD["ped_r"], OD["x1"] - OD["x0"], V(x0, A.S3, 0), V(1, 0, 0)).common(O))
for sx in (1, -1):        # O84 + asagida 45 derece damla ucu: omuz bandi ters basilinca deligin tavani desteksiz
    S = S.cut(damla(V(145.0 if sx > 0 else -160.0, A.S3, 0), V(1, 0, 0), OD["delik_r"], 15.0, V(0, -1, 0)))
S = S.cut(Part.makeCylinder(A.BOYUN_ACIKLIK_R, 40.0, V(0, A.GOVDE_Y1 - 20, 0), V(0, 1, 0)))
for sx in (1, -1):        # omuz yuvasi ust civatasinin basi ust kapaga girer: erisim deligi (anahtar da buradan)
    S = S.cut(Part.makeCylinder(A.UST_KAPAK_ERISIM["r"], 20.0, V(sx * A.UST_KAPAK_ERISIM["x"], A.GOVDE_Y1 - 10, 0), V(0, 1, 0)))
EKM = ekran_matris()
EO = ekran_olculeri()
pw = EO["pencere"]
PENCERE_TAM = yerlestir(box(pw[0], pw[1], pw[2], 90.0, -3.0, 8.0), EKM)       # pencere prizmasi (ust sinirsiz)
Y_PEN = A.GOVDE_DIKIS[2]                                                      # pencere ust kenari = dikis 883
S = S.cut(PENCERE_TAM.common(kutu(y1=Y_PEN)))
S = S.removeSplitter()
S_dis = S.cut(M)
S_ic = S.common(M)
log("govde zarf: kabuk hacmi %.0f cm3" % (S.Volume / 1000))

AK = A.ARKA_KAPAK
KAPAK = rrect_prizma_z(-AK["x"], AK["x"], AK["y0"], AK["y1"], AK["r"], AK["z0"], AK["z1"])
KAPAK_IC = rrect_prizma_z(-AK["x"] + W, AK["x"] - W, AK["y0"] + W, AK["y1"], AK["r"] - W + 0.0 if AK["r"] > W else 1.0,
                          AK["z0"], AK["z1"])
KAPAK_DIKIS = kutu(-AK["x"], AK["x"], A.GOVDE_DIKIS[1], A.GOVDE_DIKIS[1] + W, -BIG, AK["z1"])   # kapak ust kenari: alin
PEN_DIL = kutu(pw[0], pw[1], Y_PEN, Y_PEN + W, 0.0, BIG)                    # pencere ustunde dil yok (alin)


def x_ic(sag, y_plaka):
    if sag:
        return kutu(-W, BIG, -BIG, y_plaka).fuse(kutu(0, BIG, y_plaka, BIG))
    return kutu(-BIG, -W, -BIG, y_plaka).fuse(kutu(-BIG, 0, y_plaka, BIG))


GOVDE_BANT = ["alt", "orta", "gogus", "omuz"]
GOVDE_AD = {"alt": "Govde alt bandi", "orta": "Govde orta bandi", "gogus": "Gogus bandi", "omuz": "Omuz bandi"}
y_ic = [kutu(y1=YKI[1]),
        kutu(y0=YKI[1], y1=YKI[2]).cut(KAPAK_DIKIS),
        kutu(y0=YKI[2], y1=YKI[3]).fuse(KAPAK_DIKIS).cut(PEN_DIL),
        kutu(y0=YKI[3]).fuse(PEN_DIL)]
GOVDE = {}
for k, bant in enumerate(GOVDE_BANT):
    for sag in (True, False):
        r_dis = kutu(*((0, BIG) if sag else (-BIG, 0))).common(kutu(y0=YK[k], y1=YK[k + 1])).cut(KAPAK)
        r_ic = x_ic(sag, Y_KAPAK_PLAKA).common(y_ic[k]).cut(KAPAK_IC)
        sh = S_dis.common(r_dis).fuse(S_ic.common(r_ic)).removeSplitter()
        GOVDE[(bant, sag)] = sh
GOVDE[("kapak", None)] = S_dis.common(KAPAK).fuse(S_ic.common(KAPAK_IC)).removeSplitter()
log("govde parcalari:", {("%s %s" % (b, {True: "sag", False: "sol", None: ""}[s])): len(v.Solids) for (b, s), v in GOVDE.items()})

# ====================================================================== TABAN ETEGI
Oe = zarf(EK, 0.0)
Me = zarf(EK, H)
Ie = zarf(EK, T)
Se = Oe.cut(Ie)
EA = A.ETEK_ACIKLIK
Se = Se.cut(Part.Face(rrect_wire(A.Y_COV1 - 15, EA["a"], EA["b"], EA["b"], EA["r"])).extrude(V(0, 30, 0)))
ES = A.ACIL_STOP
Se = Se.cut(Part.makeCylinder(ES["delik_d"] / 2, 30.0, V(ES["x"], ES["y"] - 15, ES["z"]), V(0, 1, 0)))
SN = A.SONAR
for x in SN["x"]:
    for dx in (-SN["dx"], SN["dx"]):
        Se = Se.cut(Part.makeCylinder(SN["delik_r"], 30.0, V(x + dx, SN["y"], A.ETEK_B - 15), V(0, 0, 1)))
Se = Se.removeSplitter()
Se_dis = Se.cut(Me)
Se_ic = Se.common(Me)
log("etek zarf: kabuk hacmi %.0f cm3" % (Se.Volume / 1000))
ZD = A.ETEK_DIKIS_Z
ETEK_BANT = ["arka", "orta", "on"]
ETEK_AD = {"arka": "Etek arka", "orta": "Etek orta", "on": "Etek on"}
z_dis = {"arka": kutu(z1=-ZD), "orta": kutu(z0=-ZD, z1=ZD), "on": kutu(z0=ZD)}
z_ic = {"arka": kutu(z1=-ZD - W, y1=Y_ETEK_PLAKA).fuse(kutu(z1=-ZD, y0=Y_ETEK_PLAKA)),
        "orta": kutu(z0=-ZD - W, z1=ZD + W, y1=Y_ETEK_PLAKA).fuse(kutu(z0=-ZD, z1=ZD, y0=Y_ETEK_PLAKA)),
        "on": kutu(z0=ZD + W, y1=Y_ETEK_PLAKA).fuse(kutu(z0=ZD, y0=Y_ETEK_PLAKA))}
ETEK = {}
for bant in ETEK_BANT:
    for sag in (True, False):
        r_dis = kutu(*((0, BIG) if sag else (-BIG, 0))).common(z_dis[bant])
        r_ic = x_ic(sag, Y_ETEK_PLAKA).common(z_ic[bant])
        ETEK[(bant, sag)] = Se_dis.common(r_dis).fuse(Se_ic.common(r_ic)).removeSplitter()
log("etek parcalari:", {("%s %s" % (b, "sag" if s else "sol")): len(v.Solids) for (b, s), v in ETEK.items()})

# ====================================================================== baski yonleri
_n_arka = yuzey(GK, "arka", 0.5 * (AK["y0"] + AK["y1"]), 0.0)[1]
PARCA = {}      # ad -> dict(shape, yukari, yon, renk, patlat)
for (bant, sag), sh in GOVDE.items():
    if bant == "kapak":
        ad, yuk, yon = "Arka servis kapagi", _n_arka * -1, "dis yuzu tablada"
        pat = (0, -40, -170)
    else:
        ad = "%s %s" % (GOVDE_AD[bant], "sag" if sag else "sol")
        if bant == "omuz":
            yuk, yon = DOWN, "ters (ust kapak tablada)"
        else:
            yuk, yon = UP, "dik (alt kenari tablada)"
        k = GOVDE_BANT.index(bant)
        pat = ((130 if sag else -130), 60 * k + 40, 0)
    PARCA[ad] = dict(shape=sh, yukari=yuk, yon=yon, patlat=pat, grup="Govde kabugu")
for (bant, sag), sh in ETEK.items():
    ad = "%s %s" % (ETEK_AD[bant], "sag" if sag else "sol")
    zp = {"arka": -150, "orta": 0, "on": 150}[bant]
    PARCA[ad] = dict(shape=sh, yukari=DOWN, yon="ters (ust plakasi tablada)", patlat=((150 if sag else -150), -60, zp),
                     grup="Taban etegi")


def sahip(pt, haric=()):
    """Noktayi iceren baski parcasi (yoksa None)."""
    pt = V(*pt)
    for ad, d in PARCA.items():
        if ad in haric:
            continue
        sh = d["shape"]
        bb = sh.BoundBox
        if bb.isInside(pt) and sh.isInside(pt, 1e-6, True):
            return ad
    return None


EKLE = {ad: [] for ad in PARCA}     # parcaya eklenecek boss'lar
CIKAR = {ad: [] for ad in PARCA}    # parcadan cikarilacak delikler

# ====================================================================== bindirme civatalari (M3 ISO 7380 + isil gomme somun)
dk3, k3, _ = A.ISO7380[3]
OD_I3, L_I3 = A.INSERT[3]
BOSS_L = L_I3 + 0.5 + 1.0          # orta yuzeyden iceri: delik 6,2 + 1 mm taban
VIDA_L = 6.0                        # M3x6 ISO 7380
ADAY = []      # (etiket, kesit tablosu, yer, y, u)
for y_d, xs in ((A.GOVDE_DIKIS[0], None), (A.GOVDE_DIKIS[1], None)):
    ym = y_d + W / 2
    (a, bf, bb, r), _ = kesit_param(GK, ym)
    f = 0.55 * (a - r)
    ADAY += [("govde y%.0f on" % y_d, GK, "on", ym, sx * f) for sx in (1, -1)]
    if y_d == A.GOVDE_DIKIS[0]:
        ADAY += [("govde y%.0f arka" % y_d, GK, "arka", ym, sx * f) for sx in (1, -1)]
    else:
        ADAY += [("govde y%.0f arka" % y_d, GK, "arka", ym, sx * (AK["x"] + W + 6.0)) for sx in (1, -1)]
    zc = 0.5 * ((bf - r) - (bb - r))
    ADAY += [("govde y%.0f yan" % y_d, GK, yer, ym, zc) for yer in ("sag", "sol")]
ym = A.GOVDE_DIKIS[2] + W / 2
ADAY += [("govde y%.0f arka" % A.GOVDE_DIKIS[2], GK, "arka", ym, sx * xx) for sx in (1, -1) for xx in (70.0, 120.0)]
for yer, ys in (("on", (330.0, 420.0, 550.0, 640.0, 741.0, 940.0)), ("arka", (330.0, 420.0, 745.0, 830.0, 940.0))):
    ADAY += [("govde x0 %s" % yer, GK, yer, y, -W / 2) for y in ys]
for x, y in ((-45.0, AK["y0"] + W / 2), (0.0, AK["y0"] + W / 2), (45.0, AK["y0"] + W / 2)) + \
            tuple((sx * (AK["x"] - W / 2), y) for sx in (1, -1) for y in (570.0, 650.0)):
    ADAY.append(("arka kapak", GK, "arka", y, x))
for yer, ys in (("on", (60.0, 200.0)), ("arka", (60.0, 115.0, 200.0))):
    ADAY += [("etek x0 %s" % yer, EK, yer, y, -W / 2) for y in ys]
for yer in ("sag", "sol"):
    for zz in (ZD + W / 2, -ZD - W / 2):
        ADAY += [("etek z%+.0f %s" % (math.copysign(ZD, zz), yer), EK, yer, y, zz) for y in (60.0, 85.0, 200.0)]

atla = []
BAS_BOSLUK = 0.05       # civata basi dis yuzeyden 0,05 mm: B-spline yuzeye tam temasta boolean (common) guvenilmez
for (etiket, secs, yer, y, u) in ADAY:
    kayan = "u" if (etiket.startswith("govde y") or (etiket == "arka kapak" and abs(y - (AK["y0"] + W / 2)) < 1e-6)) else "y"
    for kay in (0.0, 1.0, -1.0, 2.0, -2.0, 3.0):
        yy, uu = (y, u + kay) if kayan == "u" else (y + kay, u)
        p, n, hn = yuzey(secs, yer, yy, uu)
        ic = sahip(p - n * (hn * 0.5))
        dis = sahip(p + n * (hn * 0.5))
        if ic is None or dis is None or ic == dis:
            continue
        p_dis = p + n * hn
        t_del = cyl(CLEAR[3] / 2, p - n * 1.0, p_dis + n * 1.0)
        t_ins = insert_hole(3, p, n * -1, extra=0.5)
        # boolean saglamligi: delik araclari gercekten dudagi ve dili kesiyor mu (B-spline duzlemde nadiren 0 donuyor)
        if PARCA[dis]["shape"].common(t_del).Volume < 0.6 * math.pi * (CLEAR[3] / 2) ** 2 * hn or            PARCA[ic]["shape"].common(t_ins).Volume < 0.6 * math.pi * (OD_I3 / 2) ** 2 * hn:
            continue
        break
    else:
        atla.append((etiket, y, u))
        continue
    asagi = PARCA[ic]["yukari"] * -1
    EKLE[ic].append(damla(p, n * -1, 4.0, BOSS_L, asagi))
    CIKAR[ic].append(t_ins)
    CIKAR[dis].append(t_del)
    VIDA.append(dict(etiket=etiket, p=p, n=n, hn=hn, ic=ic, dis=dis, tip="bindirme", kaydirma=kay))
log("bindirme civatasi: %d yer, %d atlandi" % (len(VIDA), len(atla)), atla)

# ====================================================================== Nextion yuvasi: 4x boss + M3 isil gomme somun
N = A.NEXTION
KAL = N["kalinlik"]
PCB_T = N["pcb"][2]
w_pcb_on = -(KAL - PCB_T)          # PCB on yuzu (cam onunden geride)
for (s, v) in EO["delikler"]:
    p_boss = EKM.multVec(V(s, v, w_pcb_on))
    ax_in = EKM.multVec(V(s, v, w_pcb_on + 1.0)) - p_boss          # +w (one, duvara)
    p_duvar = EKM.multVec(V(s, v, 1.0))                              # duvarin ic yarisinda bir nokta
    ic = sahip(p_duvar)
    L = 1.5 - w_pcb_on
    EKLE[ic].append(damla(p_boss, ax_in, 4.0, L, PARCA[ic]["yukari"] * -1))
    CIKAR[ic].append(insert_hole(3, p_boss, ax_in, extra=0.5))
    VIDA.append(dict(etiket="Nextion %+.1f %+.1f" % (s, v), p=p_boss, n=ax_in * -1, hn=0.0, ic=ic, dis="Nextion", tip="ekran"))

# ====================================================================== iskelete baglanti boss'lari
GB = A.KABUK_GOVDE_BRAKET
GB_YER = []
for yb in GB["y"]:
    yc = yb + GB["m5_y"]
    (a, bf, bb, r), _ = kesit_param(GK, yc)
    xw = a - GB["insert_bosluk"]
    for sx in (1, -1):
        p0 = V(sx * xw, yc, 0.0)
        ic = sahip(V(sx * (a - T + 0.5), yc, 0.0))
        od5, l5 = A.INSERT[5]
        EKLE[ic].append(damla(p0, V(sx, 0, 0), 7.0, (a - H) - xw, PARCA[ic]["yukari"] * -1))
        CIKAR[ic].append(insert_hole(5, p0, V(sx, 0, 0), extra=0.5))
        GB_YER.append(dict(yb=yb, yc=yc, sx=sx, xw=xw, a=a, parca=ic))
EB = A.KABUK_ETEK_BRAKET
EB_YER = []
for zb in EB["z"]:
    for sx in (1, -1):
        (a, bf, bb, r), _ = kesit_param(EK, EB["m3_y"])
        p0 = V(sx * EB["x_ic"], EB["m3_y"], zb)
        ic = sahip(V(sx * (a - T + 0.5), EB["m3_y"], zb))
        EKLE[ic].append(damla(p0, V(sx, 0, 0), 4.5, (a - H) - EB["x_ic"], PARCA[ic]["yukari"] * -1))
        CIKAR[ic].append(insert_hole(3, p0, V(sx, 0, 0), extra=0.5))
        EB_YER.append(dict(zb=zb, sx=sx, a=a, parca=ic))

TEMIZLIK = []
for ad, d in PARCA.items():
    sh = d["shape"]
    if EKLE[ad]:
        sh = sh.fuse(EKLE[ad])
    for tl in CIKAR[ad]:
        # delikler tek tek: boolean nadiren delik tapasini ayri kati birakiyor; o zaman arac 0,01 mm kaydirilip tekrarlanir
        n0, v0 = len(sh.Solids), sh.Volume
        for dv in ((0, 0, 0), (0.01, 0, 0), (0, 0.01, 0), (0, 0, 0.01), (0.013, 0.007, -0.011)):
            t_ = tl.copy()
            t_.translate(V(*dv))
            r_ = sh.cut(t_)
            if len(r_.Solids) == n0 and r_.Volume < v0 - 1e-6:
                if dv != (0, 0, 0):
                    TEMIZLIK.append((ad, "delik %.2f mm kaydirildi" % V(*dv).Length, [round(c, 1) for c in tl.BoundBox.Center]))
                sh = r_
                break
        else:
            TEMIZLIK.append((ad, "DELIK ACILAMADI", [round(c, 1) for c in tl.BoundBox.Center]))
    sh = sh.removeSplitter()
    if len(sh.Solids) > 1:
        # boolean bazen delik tapasini ayri kati birakiyor: delik araci icinde kalan kucuk katilar atilir (kayit tutulur)
        ana = max(sh.Solids, key=lambda s_: s_.Volume)
        kalan = [ana]
        for s_ in sh.Solids:
            if s_ is ana:
                continue
            tapa = s_.Volume < 50.0 and any(t_.BoundBox.isInside(s_.BoundBox.Center) and t_.isInside(s_.CenterOfMass, 1e-6, True)
                                            for t_ in CIKAR[ad])
            if tapa:
                TEMIZLIK.append((ad, round(s_.Volume, 2)))
            else:
                kalan.append(s_)
        sh = ana if len(kalan) == 1 else Part.Compound(kalan)
    d["shape"] = sh
log("boss ve delikler islendi; ayri kalan delik tapasi:", TEMIZLIK)

# ====================================================================== parcalari ekle: baski parcalari
RENK_BASKI = ["k01", "k02", "k03", "k04", "k05", "k06", "k07", "k08", "k09", "k10", "k11", "k12", "k13", "k14", "k15", "k16"]
for i, (ad, d) in enumerate(PARCA.items()):
    d["indeks"] = add(ad, d["grup"], d["shape"], "Baski", "PETG", kod="PETG baski, %s mm duvar" % ("%.1f" % T).replace(".", ","),
                      renk="kabuk", patlat=d["patlat"], not_="baski: %s" % d["yon"])
    d["renk_baski"] = RENK_BASKI[i % len(RENK_BASKI)]
    BASKI[ad] = dict(yukari=d["yukari"], yon=d["yon"], renk=d["renk_baski"])

# ====================================================================== Nextion (satin alinan)
L_, Wd_, _ = N["pcb"]
pcb = box(-L_ / 2, L_ / 2, -Wd_ / 2, Wd_ / 2, -KAL, w_pcb_on)
for (s, v) in EO["delikler"]:
    pcb = pcb.cut(Part.makeCylinder(N["delik_d"] / 2, 4, V(s, v, -KAL - 1), V(0, 0, 1)))
c = EO["cam"]
ekran = pcb.fuse(box(c[0], c[1], c[2], c[3], w_pcb_on, 0.0))
k0, kw, kk = N["konnektor"]
ekran = ekran.fuse(box(-L_ / 2 + 0.5, -L_ / 2 + kk, -Wd_ / 2 + k0, -Wd_ / 2 + k0 + kw, -KAL - N["bilesen_h"], -KAL))
ekran = ekran.removeSplitter()
I_EKRAN = add("Nextion NX1060P101_011 (10,1 in)", "Gogus ekrani", yerlestir(ekran, EKM), "Satin", "-",
              kod="Nextion NX1060P101_011 10,1\" 1024x600", renk="siyah", patlat=(0, 60, 260), kutle=N["kutle_g"],
              not_="olculer datasheet cizimi; konnektor yeri cizimden yorum (tahmini)")
pat_ek = V(0, 60, 260)
for (s, v) in EO["delikler"]:
    p_boss = EKM.multVec(V(s, v, w_pcb_on))
    p_pcb_arka = EKM.multVec(V(s, v, -KAL))
    ax = EKM.multVec(V(s, v, w_pcb_on + 1.0)) - p_boss
    add("Isil gomme somun M3 (ekran)", "Gogus ekrani", insert(3, p_boss, ax), "Baglanti", "Pirinc", kod="M3 isil gomme somun",
        renk="pirinc", patlat=tuple(pat_ek * 0.5))
    add("Ekran civatasi M3x6", "Gogus ekrani", screw912(3, 6, p_pcb_arka, ax), "Baglanti", "Celik 8.8", kod="M3x6 DIN 912",
        renk="celik", patlat=tuple(pat_ek * 1.3))

# ====================================================================== bindirme civatalari ve isil gomme somunlar
for v in VIDA:
    if v["tip"] != "bindirme":
        continue
    pi, pd = V(*PARCA[v["ic"]]["patlat"]), V(*PARCA[v["dis"]]["patlat"])
    v["i_insert"] = add("Isil gomme somun M3 (%s)" % v["etiket"], PARCA[v["ic"]]["grup"], insert(3, v["p"], v["n"] * -1),
                        "Baglanti", "Pirinc", kod="M3 isil gomme somun", renk="pirinc", patlat=tuple(pi))
    v["i_vida"] = add("Bindirme civatasi M3x6 (%s)" % v["etiket"], PARCA[v["dis"]]["grup"],
                      screw7380(3, VIDA_L, v["p"] + v["n"] * (v["hn"] + BAS_BOSLUK), v["n"] * -1), "Baglanti", "Celik 10.9",
                      kod="M3x6 ISO 7380", renk="celik", patlat=tuple(pd + v["n"] * 25))

# ====================================================================== govde braketleri (3 mm Al U) + M6 + M5
ALU = "Aluminyum 5754"
d6, L6 = GB["civata_m6"]
d5, L5 = GB["civata_m5"]
t6 = WASH125[6][2]
t5 = WASH125[5][2]
for g in GB_YER:
    sx, yb, yc, xw = g["sx"], g["yb"], g["yc"], g["xw"]
    tb, en = GB["t"], GB["en"] / 2
    xa0, xa1 = sorted((sx * A.SG / 2, sx * (A.SG / 2 + tb)))
    xc0, xc1 = sorted((sx * (xw - tb), sx * xw))
    xb0, xb1 = sorted((sx * A.SG / 2, sx * xw))
    br = box(xa0, xa1, yb, yb + GB["a_boy"], -en, en).fuse(box(xb0, xb1, yb, yb + tb, -en, en))
    br = br.fuse(box(xc0, xc1, yb, yb + GB["c_boy"], -en, en))
    for dy in GB["m6_y"]:
        br = br.cut(cyl(CLEAR[6] / 2, (xa0 - 1, yb + dy, 0), (xa1 + 1, yb + dy, 0)))
    br = br.cut(cyl(CLEAR[5] / 2, (xc0 - 1, yc, 0), (xc1 + 1, yc, 0)))
    ad_b = "Govde braketi %s y%.0f" % ("sag" if sx > 0 else "sol", yb)
    pat = V(sx * 70, 0, 0)
    ib = add(ad_b, "Govde braketleri", br.removeSplitter(), "Satin", ALU, kod="Govde braketi 3 mm Al U (bukum)", renk="alu2",
             patlat=tuple(pat))
    el = []
    for dy in GB["m6_y"]:
        yy = yb + dy
        p_yuz = V(sx * (A.SG / 2 + tb), yy, 0)            # braket ic yuzu (pul buraya)
        nv = V(sx, 0, 0)                                  # direk yuzunden disari
        el.append(add("Pul M6 (%s)" % ad_b, "Govde braketleri", washer(6, p_yuz, nv), "Baglanti", "Celik", kod="M6 DIN 125 pul",
                      renk="celik", patlat=tuple(pat + nv * 20)))
        el.append(add("Civata M6x%d (%s)" % (L6, ad_b), "Govde braketleri", screw912(6, L6, p_yuz + nv * t6, nv * -1), "Baglanti",
                      "Celik 8.8", kod="M6x%d DIN 912" % L6, renk="celik", patlat=tuple(pat + nv * 40)))
        el.append(add("Cekic somun M6 (%s)" % ad_b, "Govde braketleri",
                      hammer_nut(V(sx * (A.SG / 2 - A.LIP), yy, 0), nv, (0, 0, 1)), "Baglanti", "Celik",
                      kod="M6 cekic somun, kanal 10", renk="celik", patlat=tuple(pat - nv * 15)))
    p_c = V(sx * (xw - tb), yc, 0)                        # C ayaginin ic yuzu
    el.append(add("Pul M5 (%s)" % ad_b, "Govde braketleri", washer(5, p_c, V(-sx, 0, 0)), "Baglanti", "Celik", kod="M5 DIN 125 pul",
                  renk="celik", patlat=tuple(pat - V(sx * 20, 0, 0))))
    el.append(add("Civata M5x%d (%s)" % (L5, ad_b), "Govde braketleri", screw912(5, L5, p_c - V(sx * t5, 0, 0), V(sx, 0, 0)),
                  "Baglanti", "Celik 8.8", kod="M5x%d DIN 912" % L5, renk="celik", patlat=tuple(pat - V(sx * 40, 0, 0))))
    el.append(add("Isil gomme somun M5 (%s)" % ad_b, "Govde kabugu", insert(5, V(sx * xw, yc, 0), V(sx, 0, 0)), "Baglanti",
                  "Pirinc", kod="M5 isil gomme somun", renk="pirinc", patlat=tuple(V(*PARCA[g["parca"]]["patlat"]))))
    BAG.append(dict(ad=ad_b, tip="govde", govde=ib, eleman=el, sx=sx, yb=yb, yc=yc, xw=xw, parca=g["parca"]))

# ====================================================================== etek braketleri (2 mm Al L) + M6 + M3
d6e, L6e = EB["civata_m6"]
d3e, L3e = EB["civata_m3"]
for g in EB_YER:
    sx, zb = g["sx"], g["zb"]
    tb, en = EB["t"], EB["en"] / 2
    yr = A.Y_RAIL1
    xh0, xh1 = sorted((sx * EB["x0"], sx * EB["x_ic"]))
    xd0, xd1 = sorted((sx * (EB["x_ic"] - tb), sx * EB["x_ic"]))
    br = box(xh0, xh1, yr, yr + tb, zb - en, zb + en).fuse(box(xd0, xd1, EB["y_alt"], yr + tb, zb - en, zb + en))
    xr = sx * A.UZUN_RAY_X
    br = br.cut(cyl(CLEAR[6] / 2, (xr, yr - 1, zb), (xr, yr + tb + 1, zb)))
    br = br.cut(cyl(CLEAR[3] / 2, (xd0 - 1, EB["m3_y"], zb), (xd1 + 1, EB["m3_y"], zb)))
    ad_b = "Etek braketi %s z%+.0f" % ("sag" if sx > 0 else "sol", zb)
    pat = V(sx * 60, 40, 0)
    ib = add(ad_b, "Etek braketleri", br.removeSplitter(), "Satin", ALU, kod="Etek tasiyici L braket 2 mm Al (bukum)", renk="alu2",
             patlat=tuple(pat))
    el = []
    nv = V(0, 1, 0)
    p_yuz = V(xr, yr + tb, zb)
    el.append(add("Pul M6 (%s)" % ad_b, "Etek braketleri", washer(6, p_yuz, nv), "Baglanti", "Celik", kod="M6 DIN 125 pul",
                  renk="celik", patlat=tuple(pat + nv * 20)))
    el.append(add("Civata M6x%d (%s)" % (L6e, ad_b), "Etek braketleri", screw912(6, L6e, p_yuz + nv * t6, nv * -1), "Baglanti",
                  "Celik 8.8", kod="M6x%d DIN 912" % L6e, renk="celik", patlat=tuple(pat + nv * 40)))
    el.append(add("Cekic somun M6 (%s)" % ad_b, "Etek braketleri", hammer_nut(V(xr, yr - A.LIP, zb), nv, (1, 0, 0)), "Baglanti",
                  "Celik", kod="M6 cekic somun, kanal 10", renk="celik", patlat=tuple(pat - nv * 15)))
    p_d = V(sx * (EB["x_ic"] - tb), EB["m3_y"], zb)
    el.append(add("Civata M3x%d (%s)" % (L3e, ad_b), "Etek braketleri", screw912(3, L3e, p_d, V(sx, 0, 0)), "Baglanti", "Celik 8.8",
                  kod="M3x%d DIN 912" % L3e, renk="celik", patlat=tuple(pat - V(sx * 30, 0, 0))))
    el.append(add("Isil gomme somun M3 (%s)" % ad_b, "Taban etegi", insert(3, V(sx * EB["x_ic"], EB["m3_y"], zb), V(sx, 0, 0)),
                  "Baglanti", "Pirinc", kod="M3 isil gomme somun", renk="pirinc", patlat=tuple(V(*PARCA[g["parca"]]["patlat"]))))
    BAG.append(dict(ad=ad_b, tip="etek", govde=ib, eleman=el, sx=sx, zb=zb, xr=xr, parca=g["parca"]))

# ====================================================================== kutle ve merkez
RHO = {"PETG": A.PETG_RHO * A.KABUK_DOLULUK, ALU: 2.68, "Celik": 7.85, "Celik 8.8": 7.85, "Celik 10.9": 7.85, "Pirinc": 8.50}
for p in P:
    sh = p["shape"]
    p["hacim"] = sh.Volume
    p["kati"] = len(sh.Solids)
    if p["kati"] >= 1:
        vt = sum(s_.Volume for s_ in sh.Solids)
        cc = V(0, 0, 0)
        for s_ in sh.Solids:
            cc = cc + s_.CenterOfMass * (s_.Volume / vt)
        p["merkez"] = cc
    else:
        p["merkez"] = sh.BoundBox.Center
    p["kutle"] = p["kutle_sabit"] if p["kutle_sabit"] is not None else p["hacim"] / 1000.0 * RHO.get(p["malzeme"], 1.0)
    p["bb"] = sh.BoundBox
log("kabuk parca sayisi %d (baski %d), kutle %.0f g" % (len(P), sum(1 for p in P if p["tur"] == "Baski"), sum(p["kutle"] for p in P)))
