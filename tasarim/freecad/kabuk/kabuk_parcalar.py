# Kabuk modulu (V3, 1,65 m) - PARCALAR: govde kabugu (6 bant x sag/sol + arka kapak; 2 bant 1,65 m uzatmasi), taban etegi (520:
# 3 z bandi x sag/sol + 2 orta dolgu seridi), S1 kablo kasetleri, iskelete baglanti braketleri ve tum baglanti elemanlari.
# Nextion gogus ekrani KALDIRILDI (Duffy, 25 Ekim 2026): gogus bandi kapali kabuk. Import edilebilir: kabuk_montaj.py (kontroller
# + kayit), ../carpisma.py ve ../montaj/moduller.py kullanir. Koordinat = global (arayuz.py), mm.
#
# Yapi
# - Kabuk = dis zarf - ic zarf (cizgisel loft, arayuz.GOVDE_KESIT / ETEK_KESIT). Orta zarf (T/2) duvari dis ve ic
#   yariya ayirir. Parca = (dis yari  kesisim  dis hucre) + (ic yari  kesisim  ic hucre). Ic hucrenin siniri dikisten
#   KABUK_BINDIRME kadar kaydirilinca bir parcanin ic yarisi komsusunun dis yarisinin arkasina "dil" olarak uzanir
#   (bindirme). Dilde isil gomme somunlu boss, komsunun dudagindan M3 ISO 7380 civata. Dil, komsunun dis yarisina
#   degmesin diye orta yuzeyden KABUK_BINDIRME_BOSLUK (0,25 mm; 14 Ekim 2026'ya dek 0,2) iceri cekilir (baski toleransi).
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
GB_BOS = A.KABUK_BINDIRME_BOSLUK      # dil ile komsunun dis yarisi arasi bosluk: dil orta yuzeyden bu kadar iceri cekilir
BIG = 3000.0
P = []          # parcalar
BAG = []        # iskelete baglantilar (kontroller icin)
VIDA = []       # bindirme ve ekran civatalari (kontroller icin)
BASKI = {}      # baski parcasi adi -> dict(yukari=V (robot koordinatinda baski yukari yonu), yon=aciklama)
DIS_HUCRE = {}  # baski parcasi adi -> dis hucre (r_dis, hacim bolgesi): komsunun dili bu bolgeye girer (bindirme boslugu kontrolu, kabuk_montaj)


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
# (125 cm: gogus bandinda Nextion penceresi vardi; 1,65 m'de ekran yok, gogus kapali)
S = S.removeSplitter()
S_dis = S.cut(M)
S_ic = S.common(M)
S_bos = S_ic.cut(zarf(GK, H + GB_BOS))     # ic yarinin orta yuzeye bitisik GB_BOS katmani (yalniz dilden cikarilir)
log("govde zarf: kabuk hacmi %.0f cm3" % (S.Volume / 1000))

AK = A.ARKA_KAPAK
KAPAK = rrect_prizma_z(-AK["x"], AK["x"], AK["y0"], AK["y1"], AK["r"], AK["z0"], AK["z1"])
KAPAK_IC = rrect_prizma_z(-AK["x"] + W, AK["x"] - W, AK["y0"] + W, AK["y1"], AK["r"] - W + 0.0 if AK["r"] > W else 1.0,
                          AK["z0"], AK["z1"])
I_KAPAK_DIKIS = A.GOVDE_DIKIS.index(AK["y1"])                              # arka kapagin ust kenari bu dikiste (1075)
KAPAK_DIKIS = kutu(-AK["x"], AK["x"], AK["y1"], AK["y1"] + W, -BIG, AK["z1"])   # kapak ust kenari: alin
# K4 (M6, Y3): ust arka servis kapagi, gogus bandi arka duvari; ARKA_KAPAK ile ayni yapi (ust kenari 1268 dikisinde alin)
AK2 = A.M6["arka_kapak_ust"]
KAPAK2 = rrect_prizma_z(-AK2["x"], AK2["x"], AK2["y0"], AK2["y1"], AK2["r"], AK2["z0"], AK2["z1"])
KAPAK2_IC = rrect_prizma_z(-AK2["x"] + W, AK2["x"] - W, AK2["y0"] + W, AK2["y1"], AK2["r"] - W + 0.0 if AK2["r"] > W else 1.0,
                           AK2["z0"], AK2["z1"])
I_KAPAK2_DIKIS = A.GOVDE_DIKIS.index(AK2["y1"])                            # 1268 (gogus | omuz)
KAPAK2_DIKIS = kutu(-AK2["x"], AK2["x"], AK2["y1"], AK2["y1"] + W, -BIG, AK2["z1"])
KAPAKLAR = KAPAK.fuse(KAPAK2)
KAPAKLAR_IC = KAPAK_IC.fuse(KAPAK2_IC)


def x_ic(sag, y_plaka):
    if sag:
        return kutu(-W, BIG, -BIG, y_plaka).fuse(kutu(0, BIG, y_plaka, BIG))
    return kutu(-BIG, -W, -BIG, y_plaka).fuse(kutu(-BIG, 0, y_plaka, BIG))


# 1,65 m (Y2a): 476,5 dikisinin ustune iki sabit kesitli uzatma bandi (arayuz UZATMA_DIKIS); dikis sirasiyla bantlar
GOVDE_BANT = ["alt"] + ["uzatma%d" % (k + 1) for k in range(A.UZATMA_BANT)] + ["orta", "gogus", "omuz"]
GOVDE_AD = dict({"alt": "Govde alt bandi", "orta": "Govde orta bandi", "gogus": "Gogus bandi", "omuz": "Omuz bandi"},
                **{"uzatma%d" % (k + 1): "Govde uzatma bandi %d" % (k + 1) for k in range(A.UZATMA_BANT)})
assert len(GOVDE_BANT) == len(A.GOVDE_DIKIS) + 1
y_ic = []
for k in range(len(GOVDE_BANT)):
    c_ = kutu(y0=YKI[k], y1=YKI[k + 1])
    if k == I_KAPAK_DIKIS:              # kapagin altindaki bant (orta): kapak ust kenarinda dil yok
        c_ = c_.cut(KAPAK_DIKIS)
    elif k == I_KAPAK_DIKIS + 1:        # kapagin ustundeki bant (gogus)
        c_ = c_.fuse(KAPAK_DIKIS)
    if k == I_KAPAK2_DIKIS:             # K4: ust kapagin altindaki bant (gogus)
        c_ = c_.cut(KAPAK2_DIKIS)
    elif k == I_KAPAK2_DIKIS + 1:       # K4: ust kapagin ustundeki bant (omuz)
        c_ = c_.fuse(KAPAK2_DIKIS)
    y_ic.append(c_)
GOVDE = {}
for k, bant in enumerate(GOVDE_BANT):
    for sag in (True, False):
        r_dis = kutu(*((0, BIG) if sag else (-BIG, 0))).common(kutu(y0=YK[k], y1=YK[k + 1])).cut(KAPAKLAR)
        r_ic = x_ic(sag, Y_KAPAK_PLAKA).common(y_ic[k]).cut(KAPAKLAR_IC)
        dil = S_ic.common(r_ic).cut(S_bos.common(r_ic.cut(r_dis)))      # dil bolgesi (ic hucre - dis hucre) GB_BOS incelir
        sh = S_dis.common(r_dis).fuse(dil).removeSplitter()
        GOVDE[(bant, sag)] = sh
        DIS_HUCRE['%s %s' % (GOVDE_AD[bant], 'sag' if sag else 'sol')] = r_dis
_kdil = KAPAK_IC.cut(KAPAK)
_kic = S_ic.common(KAPAK_IC)
if _kdil.Volume > 1e-6:
    _kic = _kic.cut(S_bos.common(_kdil))
GOVDE[("kapak", None)] = S_dis.common(KAPAK).fuse(_kic).removeSplitter()
DIS_HUCRE['Arka servis kapagi'] = KAPAK
_kdil2 = KAPAK2_IC.cut(KAPAK2)
_kic2 = S_ic.common(KAPAK2_IC)
if _kdil2.Volume > 1e-6:
    _kic2 = _kic2.cut(S_bos.common(_kdil2))
GOVDE[("kapak2", None)] = S_dis.common(KAPAK2).fuse(_kic2).removeSplitter()
DIS_HUCRE['Ust arka servis kapagi'] = KAPAK2
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
# K7 (M6, Y3): ana anahtar dugmesi deligi; K5 / K6: etek servis kapaklari H1 (sigorta kutusu) / H2 (ana sigorta) delikleri
_AAM = A.TABAN["ana_anahtar"]["merkez"]
Se = Se.cut(Part.makeCylinder(A.M6["ana_anahtar_delik_d"] / 2, 30.0, V(_AAM[0], A.Y_COV1 - 15, _AAM[1]), V(0, 1, 0)))


def rrect_y(x, z, r, y0, y1):
    """XZ'de kose yaricapi r dikdortgen, y0 -> y1 boyunca (etek ust plakasi delikleri / kapaklari)."""
    b_ = Part.makeBox(x[1] - x[0], y1 - y0, z[1] - z[0], V(x[0], y0, z[0]))
    return b_.makeFillet(r, [e for e in b_.Edges if abs(e.Vertexes[0].Point.y - e.Vertexes[-1].Point.y) > 1e-6])


ETEK_KAPAK = {"Etek servis kapagi H1 (sigorta kutusu)": A.M6["etek_kapak_h1"], "Etek servis kapagi H2 (ana sigorta)": A.M6["etek_kapak_h2"]}
for _h in ETEK_KAPAK.values():
    Se = Se.cut(rrect_y(_h["x"], _h["z"], _h["r"], A.Y_COV1 - 15, A.Y_COV1 + 15))
SN = A.SONAR
for x in SN["x"]:
    for dx in (-SN["dx"], SN["dx"]):
        Se = Se.cut(Part.makeCylinder(SN["delik_r"], 30.0, V(x + dx, SN["y"], A.ETEK_B - 15), V(0, 0, 1)))
Se = Se.removeSplitter()
Se_dis = Se.cut(Me)
Se_ic = Se.common(Me)
Se_bos = Se_ic.cut(zarf(EK, H + GB_BOS))
log("etek zarf: kabuk hacmi %.0f cm3" % (Se.Volume / 1000))
ZD = A.ETEK_DIKIS_Z
ETEK_BANT = ["arka", "orta", "on"]
ETEK_AD = {"arka": "Etek arka", "orta": "Etek orta", "on": "Etek on"}
z_dis = {"arka": kutu(z1=-ZD), "orta": kutu(z0=-ZD, z1=ZD), "on": kutu(z0=ZD)}
z_ic = {"arka": kutu(z1=-ZD - W, y1=Y_ETEK_PLAKA).fuse(kutu(z1=-ZD, y0=Y_ETEK_PLAKA)),
        "orta": kutu(z0=-ZD - W, z1=ZD + W, y1=Y_ETEK_PLAKA).fuse(kutu(z0=-ZD, z1=ZD, y0=Y_ETEK_PLAKA)),
        "on": kutu(z0=ZD + W, y1=Y_ETEK_PLAKA).fuse(kutu(z0=ZD, y0=Y_ETEK_PLAKA))}
# 520 taban (arayuz ETEK_DIKIS_X, Duffy 25 Ekim 2026): etek x'te uc hucre: sol yari | dolgu seridi | sag yari. Ic hucre siniri dikisten
# KABUK_BINDIRME kadar -x'e kayik (dil soldaki komsunun dis yarisinin arkasina uzanir; 125 cm x = 0 dikisindeki kuralla ayni). Ust plakada
# dil yok (alin). Yarilar 3 z bandina (arka / orta / on), dolgu seridi aciklikta z = 0'da ikiye (arka / on) bolunur.
XD0, XD1 = A.ETEK_DIKIS_X
ETEK_X = {"sol": (-BIG, XD0), "dolgu": (XD0, XD1), "sag": (XD1, BIG)}


def etek_x(hucre, ic):
    x0, x1 = ETEK_X[hucre]
    if not ic:
        return kutu(x0, x1)
    xi0 = x0 - W if x0 > -BIG else x0
    xi1 = x1 - W if x1 < BIG else x1
    return kutu(xi0, xi1, -BIG, Y_ETEK_PLAKA).fuse(kutu(x0, x1, Y_ETEK_PLAKA, BIG))


ETEK = {}
for bant in ETEK_BANT:
    for sag in (True, False):
        h = "sag" if sag else "sol"
        r_dis = etek_x(h, False).common(z_dis[bant])
        r_ic = etek_x(h, True).common(z_ic[bant])
        dil = Se_ic.common(r_ic).cut(Se_bos.common(r_ic.cut(r_dis)))
        ETEK[(bant, sag)] = Se_dis.common(r_dis).fuse(dil).removeSplitter()
        DIS_HUCRE['%s %s' % (ETEK_AD[bant], h)] = r_dis
ETEK_DOLGU = {}
if XD1 - XD0 > 1e-6:
    for yer, zk in (("arka", kutu(z1=0.0)), ("on", kutu(z0=0.0))):
        r_dis = etek_x("dolgu", False).common(zk)
        r_ic = etek_x("dolgu", True).common(zk)
        dil = Se_ic.common(r_ic).cut(Se_bos.common(r_ic.cut(r_dis)))
        ETEK_DOLGU[yer] = Se_dis.common(r_dis).fuse(dil).removeSplitter()
        DIS_HUCRE["Etek dolgu seridi %s" % yer] = r_dis
log("etek parcalari:", {("%s %s" % (b, "sag" if s else "sol")): len(v.Solids) for (b, s), v in ETEK.items()},
    {"dolgu " + k: len(v.Solids) for k, v in ETEK_DOLGU.items()})

# ====================================================================== baski yonleri
_n_arka = yuzey(GK, "arka", 0.5 * (AK["y0"] + AK["y1"]), 0.0)[1]
PARCA = {}      # ad -> dict(shape, yukari, yon, renk, patlat)
for (bant, sag), sh in GOVDE.items():
    if bant == "kapak":
        ad, yuk, yon = "Arka servis kapagi", _n_arka * -1, "dis yuzu tablada"
        pat = (0, -40, -170)
    elif bant == "kapak2":
        ad, yuk, yon = "Ust arka servis kapagi", yuzey(GK, "arka", 0.5 * (AK2["y0"] + AK2["y1"]), 0.0)[1] * -1, "dis yuzu tablada"
        pat = (0, 40, -170)
    else:
        ad = "%s %s" % (GOVDE_AD[bant], "sag" if sag else "sol")
        if bant == "omuz":
            yuk, yon = DOWN, "ters (ust kapak tablada)"
        else:
            yuk, yon = UP, "dik (alt kenari tablada)"
        k = GOVDE_BANT.index(bant)
        pat = ((130 if sag else -130), 60 * k + 40, 0)      # (patlatma: bant sirasi)
    PARCA[ad] = dict(shape=sh, yukari=yuk, yon=yon, patlat=pat, grup="Govde kabugu")
for (bant, sag), sh in ETEK.items():
    ad = "%s %s" % (ETEK_AD[bant], "sag" if sag else "sol")
    zp = {"arka": -150, "orta": 0, "on": 150}[bant]
    PARCA[ad] = dict(shape=sh, yukari=DOWN, yon="ters (ust plakasi tablada)", patlat=((150 if sag else -150), -60, zp),
                     grup="Taban etegi")
for yer, sh in ETEK_DOLGU.items():
    PARCA["Etek dolgu seridi %s" % yer] = dict(shape=sh, yukari=DOWN, yon="ters (ust plakasi tablada)",
                                               patlat=(0, -60, -150 if yer == "arka" else 150), grup="Taban etegi")


# K5 / K6 (M6, Y3): etek servis kapaklari (3 mm PETG, etek ust plakasinin ustunde; duz basilir)
for _ad, _h in ETEK_KAPAK.items():
    _kp = rrect_y((_h["x"][0] - _h["pay_x"], _h["x"][1] + _h["pay_x"]), (_h["z"][0] - _h["pay_z"], _h["z"][1] + _h["pay_z"]),
                  _h["r"] + min(_h["pay_x"], _h["pay_z"]), A.Y_COV1, A.Y_COV1 + _h["t"])
    for _x in _h["vida_x"]:
        for _z in _h["vida_z"]:
            _kp = _kp.cut(Part.makeCylinder(CLEAR[3] / 2, _h["t"] + 2, V(_x, A.Y_COV1 - 1, _z), V(0, 1, 0)))
    PARCA[_ad] = dict(shape=_kp.removeSplitter(), yukari=UP, yon="duz (alt yuzu tablada)", grup="Taban etegi",
                      patlat=(0.5 * (_h["x"][0] + _h["x"][1]), 90, 0.5 * (_h["z"][0] + _h["z"][1]) - 60))


# ====================================================================== S1 kablo kaseti (duzeltme plani M1 / S1, 15 Ekim 2026)
# Doner U-lop kasetinin sabit yarisi (arayuz.KOL_KABLO["s1"]; tambur omuz modulunde). Iki baski parcasi (taraf basina):
#   govde = arka plaka (x 152-153, kabugun duz omuz yuzune oturur) + dis duvar (r 75,2-77,2) + 2 dikme + ust uc pim yuvasi;
#           baski: arka yuz tablada (desteksiz).
#   kapak = flans (x 158,3-159,5) + dikme basliklari (havsali M3 basi) + ust uc pimi; baski: flans dis yuzu tablada (desteksiz).
# Taban cizgisi (yz duzleminde) = S1 ekseni etrafinda halka dilimi (psi0 ... phi 135'teki U'nun dis temasi) + phi 135'teki U'nun
# (temasli elastika, dirsek/kablo_yolu.py) ic bolgesi u_pay kadar buyutulmus + ust uc pimi. Duvar = taban cizgisinin 2 mm ic seridi
# (tambura bakan ic kenar haric). Kabuga: 2 dikme icin omuz pedine isil gomme + boss, kablo cikisi icin ped yarigi. Sol = X aynasi.
# Y1b (25 Ekim 2026): flans ic kenari pahi (K3), U cebi payi 6,5 (K4), duvar bagi baglama ipi delikleri (K4), duvar disi ikinci pim
# kulagi (B9). Montaj: govde ve kapak ONDEN RADYAL takilir (K5; planlama/adim2/S1-kaset.md).
for _p in (os.path.join(UST, "dirsek"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import kablo_yolu as KY
S1K = A.KOL_KABLO["s1"]
S1D = S1K["duvar"]
S1O = KY.s1_olcu(A.KOL_KABLO)
S1U = KY.s1_poz(A.KOL_KABLO, A.OMUZ["one_arka_aralik"][1], S1O)         # U'nun en ileri konumu (S1 ust siniri)
KAS_X0, KAS_XA = S1D["x0"], S1D["x0"] + S1D["arka_t"]                    # arka plaka
KAS_XF0, KAS_XF1 = S1D["flans_x"]
KAS_RI, KAS_RO = S1D["flans_r_ic"], S1D["r"][1]


def _yz(psi, r, x=0.0):
    y, z = KY.psi_yz(psi, r)
    return V(x, y, z)


def _yay_poligon(r0, r1, psi0, psi1, adim=1.0):
    n = max(2, int(abs(psi1 - psi0) / adim) + 1)
    dis = [_yz(psi0 + (psi1 - psi0) * i / n, r1) for i in range(n + 1)]
    ic = [_yz(psi1 - (psi1 - psi0) * i / n, r0) for i in range(n + 1)]
    return Part.Face(Part.makePolygon(dis + ic + [dis[0]]))


def _daire(r, merkez=V(0, 0, 0)):
    return Part.Face(Part.Wire(Part.makeCircle(r, merkez, V(1, 0, 0))))


_psi_a = S1U["psi_U"] + S1O["U"]["delta"]                                # phi 135'te dis temas (duvarin bittigi yer, + U payi)
_dilim = _yay_poligon(KAS_RI, KAS_RO, S1D["psi0"], _psi_a)
_u = [V(0, q.y, q.z) for q in S1U["u_nokta"]]
_u_yuz = Part.Face(Part.Wire(Part.makePolygon(_u + [_u[0]]))).makeOffset2D(S1D["u_pay"], 0)
# ust uc pimi: U'nun (phi 135) en yakin noktasina >= demet yari kalinligi + bosluk + dikme yaricapi
_pm = S1D["pim"]
_u2 = [(q.y, q.z) for q in S1U["u_nokta"]]
_pim_psi = S1U["u_uc_psi"]
while True:
    _c = KY.psi_yz(_pim_psi, _pm["r"])
    if min(math.hypot(_c[0] - a_, _c[1] - b_) for a_, b_ in _u2) >= S1O["kalinlik"] / 2 + _pm["bosluk"] + _pm["post_r"] + 0.5:
        break
    _pim_psi += 0.5
_taban = _dilim.fuse([_u_yuz, _daire(_pm["post_r"] + 2.0, _yz(_pim_psi, _pm["r"]))])
_taban = _taban.common(_daire(KAS_RO).cut(_daire(KAS_RI))).removeSplitter()
assert len(_taban.Faces) == 1, "S1 kaseti taban cizgisi tek yuz degil: %d" % len(_taban.Faces)
_taban = _taban.Faces[0]
_ic = _taban.makeOffset2D(-2.0, 0)
_serit = _taban.cut(_ic).cut(_daire(S1D["ic_kes_r"]))


def _uz(face, x0, x1):
    f = face.copy()
    f.translate(V(x0, 0, 0))
    return f.extrude(V(x1 - x0, 0, 0))


S1_DIKME = []                       # (psi, r, havsa oturma noktasi, kabuk yuzu noktasi) yerel
_bx, _hx = S1D["bolum_x"], S1D["havsa_x"]
k_govde = _uz(_taban, KAS_X0, KAS_XA).fuse(_uz(_serit, KAS_XA, KAS_XF0))
k_kapak = _uz(_taban, KAS_XF0, KAS_XF1)
for (ps, r) in S1K["dikme"]:
    c = _yz(ps, r)
    k_govde = k_govde.fuse(Part.makeCylinder(S1K["dikme_r"], _bx - KAS_XA + 0.01, V(KAS_XA - 0.01, c.y, c.z), V(1, 0, 0)))
    k_kapak = k_kapak.fuse(Part.makeCylinder(S1K["dikme_r"], KAS_XF0 - _bx + 0.01, V(_bx, c.y, c.z), V(1, 0, 0)))
    k_govde = k_govde.cut(Part.makeCylinder(CLEAR[3] / 2, _bx - KAS_X0 + 2, V(KAS_X0 - 1, c.y, c.z), V(1, 0, 0)))
    k_kapak = k_kapak.cut(Part.makeCylinder(CLEAR[3] / 2, KAS_XF1 - _bx + 2, V(_bx - 1, c.y, c.z), V(1, 0, 0)))
    k_kapak = k_kapak.cut(Part.makeCylinder(3.0, KAS_XF1 - _hx + 1, V(_hx, c.y, c.z), V(1, 0, 0)))      # O6 havsa (DIN 912 basi O5,5)
    S1_DIKME.append((ps, r, V(_hx, c.y, c.z), V(KAS_X0, c.y, c.z)))
_pc = _yz(_pim_psi, _pm["r"])
k_govde = k_govde.fuse(Part.makeCylinder(_pm["post_r"], KAS_XF0 - KAS_XA + 0.01, V(KAS_XA - 0.01, _pc.y, _pc.z), V(1, 0, 0)))
k_govde = k_govde.cut(Part.makeCylinder(_pm["d"] / 2 + 0.1, 3.2, V(KAS_XF0 - 3.1, _pc.y, _pc.z), V(1, 0, 0)))
k_kapak = k_kapak.fuse(Part.makeCylinder(_pm["d"] / 2, 3.0, V(KAS_XF0 - 3.0, _pc.y, _pc.z), V(1, 0, 0)))
# --- Y1b duzeltmeleri (25 Ekim 2026; planlama/adim2/K2-s1-kontrol.md K3, K4, B9; gunluk S1-duzeltme-gunluk.md)
# ikinci pim (B9): duvarin disinda kulak (govde: dikme + kopru; kapak: flans uzantisi + O3 pim). Pim U'nun suprudugu halkaya giremez.
_p2 = S1D["pim2"]
_pc2 = _yz(_p2["psi"], _p2["r"])
_e2r, _e2t = _yz(_p2["psi"], 1.0), _yz(_p2["psi"] + 90.0, 1.0)


def _kulak(x0, x1):
    a_, b_ = _e2r * _p2["kopru_r"], _e2r * _p2["r"]
    w_ = _e2t * _p2["post_r"]
    kopru = Part.Face(Part.makePolygon([a_ + w_, b_ + w_, b_ - w_, a_ - w_, a_ + w_]))
    kopru.translate(V(x0, 0, 0))
    return kopru.extrude(V(x1 - x0, 0, 0)).fuse(Part.makeCylinder(_p2["post_r"], x1 - x0, V(x0, _pc2.y, _pc2.z), V(1, 0, 0)))


k_govde = k_govde.fuse(_kulak(KAS_X0, KAS_XF0 + 0.01))
k_govde = k_govde.cut(Part.makeCylinder(_p2["d"] / 2 + 0.1, 3.2, V(KAS_XF0 - 3.1, _pc2.y, _pc2.z), V(1, 0, 0)))
k_kapak = k_kapak.fuse(_kulak(KAS_XF0, KAS_XF1))
k_kapak = k_kapak.fuse(Part.makeCylinder(_p2["d"] / 2, 3.0, V(KAS_XF0 - 3.0, _pc2.y, _pc2.z), V(1, 0, 0)))
assert _p2["r"] - _p2["d"] / 2 - 0.1 > KAS_RO, "ikinci pim deligi duvara giriyor"
# flans pahi (K3): flans ic kenarinin dis (x 159,5) kosesi, tam kalinlik 45 derece (ic yuz x 158,3'te r 44,2 korunur)
_ph = S1D["pah"]
k_kapak = k_kapak.cut(Part.makeCone(KAS_RI - 0.01, KAS_RI + _ph * (KAS_XF1 - KAS_XF0 + 0.02) / (KAS_XF1 - KAS_XF0) - 0.01,
                                    KAS_XF1 - KAS_XF0 + 0.02, V(KAS_XF0 - 0.01, 0, 0), V(1, 0, 0)))
# duvar bagi baglama ipi delikleri (K4): her ip_psi'de arka plaka dibinde radyal yarik + duvar ust kenarinda centik (O0,4 ip)
_DI = S1D["ip"]
for _ps in S1D["ip_psi"]:
    for (xa_, xb_) in (_DI["arka_x"], (_DI["ust_x"][0], _DI["ust_x"][1] + 0.01)):
        _b = Part.makeBox(xb_ - xa_, S1D["r"][1] - S1D["r"][0] + 1.0, _DI["gen"], V(xa_, S1D["r"][0] - 0.5, -_DI["gen"] / 2))
        _b.rotate(V(0, 0, 0), V(-1, 0, 0), _ps)
        k_govde = k_govde.cut(_b)
# kablo cikisi: duvar bagi -> psi_c'de radyal ice -> r_don'da arka plaka + ped yarigi (radyal x teget = yarik olcusu)
_C = S1K["cikis"]
_yr, _yt = _C["yarik"]
_e_r = _yz(_C["psi"], 1.0)
_e_t = _yz(_C["psi"] + 90.0, 1.0)
_m = _yz(_C["psi"], _C["r_don"])


def _yarik(x0, x1):
    a_ = _m - _e_r * ((_yr - _yt) / 2)
    b_ = _m + _e_r * ((_yr - _yt) / 2)
    s_ = Part.makeCylinder(_yt / 2, x1 - x0, V(x0, a_.y, a_.z), V(1, 0, 0)).fuse(
        Part.makeCylinder(_yt / 2, x1 - x0, V(x0, b_.y, b_.z), V(1, 0, 0)))
    kut = Part.Face(Part.makePolygon([a_ + _e_t * (_yt / 2), b_ + _e_t * (_yt / 2), b_ - _e_t * (_yt / 2), a_ - _e_t * (_yt / 2),
                                      a_ + _e_t * (_yt / 2)]))
    kut.translate(V(x0, 0, 0))
    return s_.fuse(kut.extrude(V(x1 - x0, 0, 0))).removeSplitter()


k_govde = k_govde.cut(_yarik(KAS_X0 - 1, KAS_XA + 1)).removeSplitter()
k_kapak = k_kapak.removeSplitter()
S1_YARIK_KABUK = _yarik(A.OMUZ_DUVAR["x0"] - 3.0, KAS_X0 + 0.01)         # kabuk ped yarigi (yerel)


def _yarik_ic(x0, x1, r_ic):
    """K3 (M6, Y3): ped yarigindan O84'e radyal kanal (genislik yarik tegeti), psi_c'de r_ic ... r_don."""
    a_ = _yz(_C["psi"], r_ic)
    kut = Part.Face(Part.makePolygon([a_ + _e_t * (_yt / 2), _m + _e_t * (_yt / 2), _m - _e_t * (_yt / 2), a_ - _e_t * (_yt / 2),
                                      a_ + _e_t * (_yt / 2)]))
    kut.translate(V(x0, 0, 0))
    return kut.extrude(V(x1 - x0, 0, 0))


S1_YARIK_KABUK = S1_YARIK_KABUK.fuse(_yarik_ic(A.OMUZ_DUVAR["x0"] - 3.0, KAS_X0 + 0.01, A.M6["s1_ped_yarik_r_ic"])).removeSplitter()
S1_KASET = dict(pim_psi=_pim_psi, psi_a=_psi_a, psi_uc=S1U["u_uc_psi"], dikme=S1_DIKME, pim2_psi=_p2["psi"], pah=_ph,
                ip_psi=list(S1D["ip_psi"]))
_OMUZ_Y = A.MODULLER["omuz_sag"]["konum"][1]


def _glob(sh, sag):
    s_ = sh.copy()
    s_.translate(V(0, _OMUZ_Y, 0))
    if not sag:
        s_ = s_.mirror(V(0, 0, 0), V(1, 0, 0))
    return s_


def _gnok(p, sag):
    return V(p.x if sag else -p.x, p.y + _OMUZ_Y, p.z)


for sag in (True, False):
    sx = 1 if sag else -1
    t_ = "sag" if sag else "sol"
    PARCA["S1 kaset govdesi %s" % t_] = dict(shape=_glob(k_govde, sag), yukari=V(sx, 0, 0), yon="arka yuzu (x 152) tablada",
                                             patlat=(sx * 60, 0, 40), grup="S1 kablo kaseti")
    PARCA["S1 kaset kapagi %s" % t_] = dict(shape=_glob(k_kapak, sag), yukari=V(-sx, 0, 0), yon="flans dis yuzu tablada",
                                            patlat=(sx * 90, 0, 40), grup="S1 kablo kaseti")
log("S1 kaseti: psi %.1f...%.1f (U ucu %.1f, u_pay %.1f, pim %.1f, pim2 %.1f), govde %.1f cm3, kapak %.1f cm3, kati %d/%d" % (
    S1D["psi0"], _psi_a, S1U["u_uc_psi"], S1D["u_pay"], _pim_psi, _p2["psi"], k_govde.Volume / 1000, k_kapak.Volume / 1000,
    len(k_govde.Solids), len(k_kapak.Solids)))


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

# --- S1 kaseti: omuz pedinde dikme isil gomme somunlari (boss icerde) + kablo cikis yarigi
KASET_PARCA = [ad for ad in PARCA if ad.startswith("S1 kaset")]
S1_VIDA = []
for sag in (True, False):
    sx = 1 if sag else -1
    for (ps, r, p_has, p_yuz) in S1_DIKME:
        pg = _gnok(p_yuz, sag)
        ic = sahip(pg - V(sx * 2.5, 0, 0), haric=KASET_PARCA)
        EKLE[ic].append(damla(pg, V(-sx, 0, 0), 4.0, BOSS_L, PARCA[ic]["yukari"] * -1))
        CIKAR[ic].append(insert_hole(3, pg, V(-sx, 0, 0), extra=0.5))
        S1_VIDA.append(dict(sag=sag, psi=ps, r=r, p_yuz=pg, p_has=_gnok(p_has, sag), ic=ic,
                            kapak="S1 kaset kapagi %s" % ("sag" if sag else "sol"), govde="S1 kaset govdesi %s" % ("sag" if sag else "sol")))
    yk = _glob(S1_YARIK_KABUK, sag)
    for ad_ in [a_ for a_ in PARCA if a_ not in KASET_PARCA and PARCA[a_]["shape"].BoundBox.intersect(yk.BoundBox)]:
        if PARCA[ad_]["shape"].common(yk).Volume > 1.0:
            CIKAR[ad_].append(yk)
log("S1 kaseti: dikme somunlari", [(v["ic"], v["psi"]) for v in S1_VIDA])
VIDA_L = 6.0                        # M3x6 ISO 7380
ADAY = []      # (etiket, kesit tablosu, yer, y, u)
# Yatay dikisler (1,65 m): 476,5 / 669 / 861,5 (uzatma) 125 cm'deki 476,5 kurali (on +-f, arka +-f, yanlar); 1075 (arka kapak ust kenari)
# arka +-(kapak + dil + 6); 1268 (gogus | omuz) arka +-70 / +-120 ve ON +-f (125 cm'de Nextion penceresinin ust kenariydi, on civata yoktu).
for k, y_d in enumerate(A.GOVDE_DIKIS):
    ym = y_d + W / 2
    (a, bf, bb, r), _ = kesit_param(GK, ym)
    f = 0.55 * (a - r)
    ADAY += [("govde y%.0f on" % y_d, GK, "on", ym, sx * f) for sx in (1, -1)]
    if k == I_KAPAK_DIKIS:
        ADAY += [("govde y%.0f arka" % y_d, GK, "arka", ym, sx * (AK["x"] + W + 6.0)) for sx in (1, -1)]
    elif k == I_KAPAK2_DIKIS:           # K4: 1268 dikisi ust kapagin ust kenari (alin) -> kapak disinda
        ADAY += [("govde y%.0f arka" % y_d, GK, "arka", ym, sx * xx) for sx in (1, -1) for xx in (AK2["x"] + W + 6.0, 120.0)]
    elif k > I_KAPAK_DIKIS:
        ADAY += [("govde y%.0f arka" % y_d, GK, "arka", ym, sx * xx) for sx in (1, -1) for xx in (70.0, 120.0)]
    else:
        ADAY += [("govde y%.0f arka" % y_d, GK, "arka", ym, sx * f) for sx in (1, -1)]
    if k <= I_KAPAK_DIKIS:
        zc = 0.5 * ((bf - r) - (bb - r))
        ADAY += [("govde y%.0f yan" % y_d, GK, yer, ym, zc) for yer in ("sag", "sol")]
# x = 0 dikisi (on ve arka): 125 cm'deki yerler (476,5 ustu UZAMA yukari) + her uzatma bandinda bant ortasi +-55 (taslak-170 ile ayni) +
# gogus onunde 835 + UZAMA (125 cm'de Nextion penceresi vardi). Arka: orta bantta (861,5 ... 1075) arka kapak var -> yok.
_UZ = A.UZAMA
_UZ_X0 = [0.5 * (A.UZATMA_DIKIS[k] + A.UZATMA_DIKIS[k + 1]) + W / 2 + d_ for k in range(A.UZATMA_BANT) for d_ in (-55.0, 55.0)]
for yer, ys in (("on", (330.0, 420.0, *_UZ_X0, 550.0 + _UZ, 640.0 + _UZ, 741.0 + _UZ, 835.0 + _UZ, 940.0 + _UZ)),
                ("arka", (330.0, 420.0, *_UZ_X0, 940.0 + _UZ))):     # Y3 K4: 745 / 830 + UZAMA gogus arkasinda -> ust kapak
    ADAY += [("govde x0 %s" % yer, GK, yer, y, -W / 2) for y in ys]
for x, y in ((-45.0, AK["y0"] + W / 2), (0.0, AK["y0"] + W / 2), (45.0, AK["y0"] + W / 2)) + \
            tuple((sx * (AK["x"] - W / 2), y + _UZ) for sx in (1, -1) for y in (570.0, 650.0)):
    ADAY.append(("arka kapak", GK, "arka", y, x))
for x, y in ((-45.0, AK2["y0"] + W / 2), (0.0, AK2["y0"] + W / 2), (45.0, AK2["y0"] + W / 2)) +             tuple((sx * (AK2["x"] - W / 2), y) for sx in (1, -1) for y in (1160.0, 1225.0)):
    ADAY.append(("ust arka kapak", GK, "arka", y, x))
for yer, ys in (("on", (60.0, 200.0)), ("arka", (60.0, 115.0, 200.0))):
    for xd in A.ETEK_DIKIS_X:                 # 520: iki x dikisi (sag yari | dolgu, dolgu | sol yari); dil soldakinin dis yarisi arkasinda
        ADAY += [("etek x%+.0f %s" % (xd, yer), EK, yer, y, xd - W / 2) for y in ys]
for yer in ("sag", "sol"):
    for zz in (ZD + W / 2, -ZD - W / 2):
        ADAY += [("etek z%+.0f %s" % (math.copysign(ZD, zz), yer), EK, yer, y, zz) for y in (60.0, 85.0, 200.0)]

atla = []
BAS_BOSLUK = 0.05       # civata basi dis yuzeyden 0,05 mm: B-spline yuzeye tam temasta boolean (common) guvenilmez
for (etiket, secs, yer, y, u) in ADAY:
    kayan = "u" if (etiket.startswith("govde y") or (etiket == "arka kapak" and abs(y - (AK["y0"] + W / 2)) < 1e-6)
                    or (etiket == "ust arka kapak" and abs(y - (AK2["y0"] + W / 2)) < 1e-6)) else "y"
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
        if PARCA[dis]["shape"].common(t_del).Volume < 0.6 * math.pi * (CLEAR[3] / 2) ** 2 * hn or            PARCA[ic]["shape"].common(t_ins).Volume < 0.6 * math.pi * (A.INSERT_DELIK[3] / 2) ** 2 * (hn - GB_BOS):
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

# ====================================================================== iskelete baglanti boss'lari
GB = A.KABUK_GOVDE_BRAKET
_GM5, _EM3 = A.M6["govde_braket_m5"], A.M6["etek_braket_m3"]
_PG, _PE = _GM5["percin"], _EM3["percin"]
GB_YER = []
for yb in GB["y"]:
    yc = yb + GB["m5_y"]
    (a, bf, bb, r), _ = kesit_param(GK, yc)
    xw = a - GB["insert_bosluk"]
    for sx in (1, -1):
        p0 = V(sx * xw, yc, 0.0)
        ic = sahip(V(sx * (a - T + 0.5), yc, 0.0))
        EKLE[ic].append(damla(p0, V(sx, 0, 0), 7.0, (a - H) - xw, PARCA[ic]["yukari"] * -1))
        # K1 (M6, Y3): isil gomme yerine disaridan M5 -> boss + duvarda O5,5 gecis, boss yuzunde percin somun flansi cebi
        CIKAR[ic].append(Part.makeCylinder(CLEAR[5] / 2, a - xw + 2.0, p0 - V(sx, 0, 0), V(sx, 0, 0)))
        CIKAR[ic].append(Part.makeCylinder(A.ISO7380[5][0] / 2 + 0.5, 6.0, V(sx * (a - A.M6["oturma_derin"]), yc, 0.0), V(sx, 0, 0)))   # dis yuzde O10,5 oturma
        CIKAR[ic].append(Part.makeCylinder((_PG["flans_d"] + _GM5["cep_pay"][0]) / 2, _PG["flans_t"] + _GM5["cep_pay"][1], p0 - V(sx * 0.01, 0, 0),
                                           V(sx, 0, 0)))
        GB_YER.append(dict(yb=yb, yc=yc, sx=sx, xw=xw, a=a, parca=ic))
EB = A.KABUK_ETEK_BRAKET
EB_YER = []
for zb in EB["z"]:
    for sx in (1, -1):
        (a, bf, bb, r), _ = kesit_param(EK, EB["m3_y"])
        p0 = V(sx * EB["x_ic"], EB["m3_y"], zb)
        ic = sahip(V(sx * (a - T + 0.5), EB["m3_y"], zb))
        EKLE[ic].append(damla(p0, V(sx, 0, 0), _EM3["boss_r"], (a - H) - EB["x_ic"], PARCA[ic]["yukari"] * -1))
        # K2 (M6, Y3): disaridan M3 -> boss + duvarda O3,4 gecis, boss yuzunde percin somun flansi cebi
        CIKAR[ic].append(Part.makeCylinder(CLEAR[3] / 2, a - EB["x_ic"] + 2.0, p0 - V(sx, 0, 0), V(sx, 0, 0)))
        CIKAR[ic].append(Part.makeCylinder(A.ISO7380[3][0] / 2 + 0.5, 6.0, V(sx * (a - A.M6["oturma_derin"]), EB["m3_y"], zb), V(sx, 0, 0)))   # dis yuzde oturma
        CIKAR[ic].append(Part.makeCylinder((_PE["flans_d"] + _EM3["cep_pay"][0]) / 2, _PE["flans_t"] + _EM3["cep_pay"][1], p0 - V(sx * 0.01, 0, 0),
                                           V(sx, 0, 0)))
        EB_YER.append(dict(zb=zb, sx=sx, a=a, parca=ic))

# K5 / K6: kapak civatalari -> etek ust plakasi altinda boss + M3 isil gomme somun (kapak + plaka disaridan)
KAPAK_VIDA = []
for _ad, _h in ETEK_KAPAK.items():
    for _x in _h["vida_x"]:
        for _z in _h["vida_z"]:
            _ic = sahip(V(_x, A.Y_COV1 - T / 2, _z), haric=list(ETEK_KAPAK))
            EKLE[_ic].append(Part.makeCylinder(4.0, L_I3 + 0.5 + 1.0 - T, V(_x, A.Y_COV1 - T + 0.01, _z), DOWN))
            CIKAR[_ic].append(insert_hole(3, V(_x, A.Y_COV1, _z), DOWN, extra=0.5))
            KAPAK_VIDA.append(dict(kapak=_ad, ic=_ic, p=V(_x, A.Y_COV1, _z), t=_h["t"]))
log("etek kapak civatalari:", [(v["kapak"][-14:], v["ic"]) for v in KAPAK_VIDA])

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

# ====================================================================== etek kapak civatalari (K5 / K6, Y3)
for v in KAPAK_VIDA:
    v["i_insert"] = add("Isil gomme somun M3 (%s)" % v["kapak"], "Taban etegi", insert(3, v["p"], DOWN), "Baglanti", "Pirinc",
                        kod="M3 isil gomme somun", renk="pirinc", patlat=tuple(V(*PARCA[v["ic"]]["patlat"])))
    v["i_vida"] = add("Kapak civatasi M3x6 (%s)" % v["kapak"], "Taban etegi", screw7380(3, VIDA_L, v["p"] + UP * v["t"], DOWN), "Baglanti",
                      "Celik 10.9", kod="M3x6 ISO 7380", renk="celik", patlat=tuple(V(*PARCA[v["kapak"]]["patlat"]) + UP * 25))

# ====================================================================== S1 kaseti civatalari (M3x8 DIN 912, kapak havsasindan) + isil gomme somunlar
for v in S1_VIDA:
    sx = 1 if v["sag"] else -1
    pk = V(*PARCA[v["kapak"]]["patlat"])
    v["i_insert"] = add("Isil gomme somun M3 (S1 kaseti %s psi %.0f)" % ("sag" if v["sag"] else "sol", v["psi"]), PARCA[v["ic"]]["grup"],
                        insert(3, v["p_yuz"], V(-sx, 0, 0)), "Baglanti", "Pirinc", kod="M3 isil gomme somun", renk="pirinc",
                        patlat=tuple(V(*PARCA[v["ic"]]["patlat"])))
    v["i_vida"] = add("Kaset civatasi M3x%d (%s psi %.0f)" % (S1K["dikme_vida"][1], "sag" if v["sag"] else "sol", v["psi"]),
                      "S1 kablo kaseti", screw912(S1K["dikme_vida"][0], S1K["dikme_vida"][1], v["p_has"], V(-sx, 0, 0)), "Baglanti",
                      "Celik 8.8", kod="M3x%d DIN 912" % S1K["dikme_vida"][1], renk="celik", patlat=tuple(pk + V(sx * 25, 0, 0)))
    v["tip"] = "kaset"
    VIDA.append(v)

# ====================================================================== govde braketleri (3 mm Al U) + M6 + M5
ALU = "Aluminyum 5754"
d6, L6 = GB["civata_m6"]
d5, L5 = GB["civata_m5"]
t6 = WASH125[6][2]
# F (14 Ekim 2026): arayuz'deki M6x16 + pul vida ucunu direk yuzunden 3 + 1,6 .. 16 -> 11,4 mm'ye getiriyordu (kanal tabani 11,8: pay 0,4;
# sart: uc - somun ustu >= 0,5 ve kanal tabani - uc >= 0,5, kabuk_montaj.py). M6x14 pulsuz: uc = 14 - 3 = 11,0 mm (somun ustu 9,3 -> pay 1,7;
# kanal tabani 11,8 -> pay 0,8), taban ve omuzdaki cozumle ayni (pulsuz, bas 3 mm Al'a oturur). M6x16 + 2 pul (9,8) sinirda, M6x18 / M6x15 olmaz.
# arayuz.KABUK_GOVDE_BRAKET["civata_m6"] artik (6, 14); boy oradan okunur.
GB_PUL = False
GB_M6 = (d6, L6, GB_PUL)
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
    br = br.cut(cyl(_PG["delik"] / 2, (xc0 - 1, yc, 0), (xc1 + 1, yc, 0)))          # K1: percin somun deligi
    ad_b = "Govde braketi %s y%.0f" % ("sag" if sx > 0 else "sol", yb)
    pat = V(sx * 70, 0, 0)
    ib = add(ad_b, "Govde braketleri", br.removeSplitter(), "Satin", ALU, kod="Govde braketi 3 mm Al U (bukum)", renk="alu2",
             patlat=tuple(pat))
    el = []
    m6 = []          # her M6 deligi icin {pul (yoksa None), civata, somun} = P indeksleri
    for dy in GB["m6_y"]:
        yy = yb + dy
        p_yuz = V(sx * (A.SG / 2 + tb), yy, 0)            # braket dis yuzu (pul varsa buraya, yoksa bas buraya)
        nv = V(sx, 0, 0)                                  # direk yuzunden disari
        if GB_PUL:
            el.append(add("Pul M6 (%s)" % ad_b, "Govde braketleri", washer(6, p_yuz, nv), "Baglanti", "Celik", kod="M6 DIN 125 pul",
                          renk="celik", patlat=tuple(pat + nv * 20)))
        i_pul = el[-1] if GB_PUL else None
        el.append(add("Civata M6x%d (%s)" % (L6, ad_b), "Govde braketleri",
                      screw912(6, L6, p_yuz + nv * (t6 if GB_PUL else 0.0), nv * -1), "Baglanti",
                      "Celik 8.8", kod="M6x%d DIN 912" % L6, renk="celik", patlat=tuple(pat + nv * 40)))
        i_civ = el[-1]
        el.append(add("Cekic somun M6 (%s)" % ad_b, "Govde braketleri",
                      hammer_nut(V(sx * (A.SG / 2 - A.LIP), yy, 0), nv, (0, 0, 1)), "Baglanti", "Celik",
                      kod="M6 cekic somun, kanal 10", renk="celik", patlat=tuple(pat - nv * 15)))
        m6.append(dict(pul=i_pul, civata=i_civ, somun=el[-1]))
    # K1 (M6, Y3): M5 disaridan (kabuk dis yuzu -> boss -> C ayagindaki percin somun). Bas kabuk dis yuzunde (x = a).
    _L5 = _GM5["civata"][1]
    el.append(add("Civata M5x%d ISO 7380 (%s)" % (_L5, ad_b), "Govde kabugu", screw7380(5, _L5, V(sx * (g["a"] - A.M6["oturma_derin"]), yc, 0), V(-sx, 0, 0)),
                  "Baglanti", "Celik 10.9", kod="M5x%d ISO 7380" % _L5, renk="celik", patlat=tuple(V(*PARCA[g["parca"]]["patlat"]) + V(sx * 30, 0, 0)),
                  not_="M6 K1 (Y3): disaridan; bant sokumu disaridan"))
    el.append(add("Percin somun M5 (%s)" % ad_b, "Govde braketleri", percin_somun(_PG, V(sx * xw, yc, 0), V(-sx, 0, 0)), "Baglanti",
                  "Celik", kod="M5 percin somun, duz flansli (3 mm Al)", renk="celik", patlat=tuple(pat - V(sx * 20, 0, 0)),
                  kutle=_PG["kutle_g"], not_="M6 K1 (Y3): braket ayagina tezgahta percinlenir; flans boss tarafinda"))
    BAG.append(dict(ad=ad_b, tip="govde", govde=ib, eleman=el, m6=m6, sx=sx, yb=yb, yc=yc, xw=xw, parca=g["parca"]))

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
    br = br.cut(cyl(_PE["delik"] / 2, (xd0 - 1, EB["m3_y"], zb), (xd1 + 1, EB["m3_y"], zb)))   # K2: percin somun deligi
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
    # K2 (M6, Y3): M3 disaridan (etek dis yuzu -> boss -> L ayagindaki percin somun)
    _L3 = _EM3["civata"][1]
    el.append(add("Civata M3x%d ISO 7380 (%s)" % (_L3, ad_b), "Taban etegi", screw7380(3, _L3, V(sx * (g["a"] - A.M6["oturma_derin"]), EB["m3_y"], zb), V(-sx, 0, 0)),
                  "Baglanti", "Celik 10.9", kod="M3x%d ISO 7380" % _L3, renk="celik",
                  patlat=tuple(V(*PARCA[g["parca"]]["patlat"]) + V(sx * 30, 0, 0)), not_="M6 K2 (Y3): disaridan"))
    el.append(add("Percin somun M3 (%s)" % ad_b, "Etek braketleri", percin_somun(_PE, V(sx * EB["x_ic"], EB["m3_y"], zb), V(-sx, 0, 0)),
                  "Baglanti", "Celik", kod="M3 percin somun, duz flansli (2 mm Al)", renk="celik", patlat=tuple(pat - V(sx * 30, 0, 0)),
                  kutle=_PE["kutle_g"], not_="M6 K2 (Y3): braket ayagina tezgahta percinlenir; flans boss tarafinda"))
    BAG.append(dict(ad=ad_b, tip="etek", govde=ib, eleman=el, m6=[dict(pul=el[0], civata=el[1], somun=el[2])], sx=sx, zb=zb, xr=xr,
                    parca=g["parca"]))

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
