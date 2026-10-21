# Lale 1,70 m TASLAK - PARCALAR (FreeCAD 1.1, Part). Import edilebilir: taslak_montaj.py ve analiz ajani kullanir.
#
# Mevcut moduller ../montaj/moduller.py yukleyicileriyle (ana montajla ayni parca listesi, ayni haric listesi) yuklenir ve global
# geometriye tasinir; varyant farklari burada uygulanir. Modul betiklerinde ve arayuz.py'de HICBIR degisiklik yok.
#   iskelet : govde diregi 800,5 -> 1235,5 mm (yeni sigma kesimi); travers + ust kose baglantilari DY yukari
#   kabuk   : 476,5 dikisinin ustu DY yukari; araya iki sabit kesitli uzatma bandi x sag/sol (4 baski parcasi) + bindirme civatalari
#             + bant basina bir govde braketi cifti (3 mm Al U, direge 2x M6 + cekic somun, kabuga M5 + isil gomme somun)
#   omuz    : DY yukari; ust kol tupu 30 mm uzar (PETG, omuz Kol grubu)
#   dirsek  : DY - 30 (tupun yeni ucunda); elin yakasi 19 mm uzar (O34 / O22 bos tup), el ucu 374,5 mm (x1,15)
#   kafa    : Govde + Pan DY yukari; catal + tilt servosu + pim H yukari (boyun yukseltme adaptoru, 4 saplama); Bas grubu yeni (kafa10.py)
#   taban   : ayni (TASLAK_TABAN_W > 444 ise tahrik + plaka + etek yanlara acilir, etek dolgu seritleri; taslak_ayar.TABAN_DX)
# Her parca: ad, modul, grup (montaj grubu), shape (global), kutle (g), merkez (global), tur, malzeme, kod, renk, not_, durum
#   (ayni | tasindi | degisti | yeni), baski (yukari, yon) varsa. Gruplar ve eklemler: GRUPLAR, EKLEMLER, BAGLAR (yeni baglantilar).
import os, sys, math, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "montaj"), os.path.join(UST, "kabuk"), os.path.join(UST, "kafa"), os.path.join(UST, "dirsek")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import FreeCAD as App
import Part
import moduller as MD
from moduller import V, A
import taslak_ayar as TA
from ortak_lib import box, cyl, sigma_y, screw912, washer, hammer_nut, insert, insert_hole, nut, CLEAR, WASH125

t0 = time.time()
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a) + "  %.1fs" % (time.time() - t0)
    LOG.append(s)
    print(s)


DY = TA.DY
DYV = V(0, DY, 0)
P = []            # yeni robotun parcalari
ESKI = []         # mevcut 125 cm robotun parcalari (ayni yukleyicilerden, degisiklik yok): karsilastirma ve gorsel
BAGLAR = []       # yeni / degisen baglantilar (rapor tablosu)
DEGISEN = []      # degisiklik listesi (rapor)
RHO_PETG08 = A.PETG_RHO * 0.8


def pisir(sh, v=None):
    """Sekli kopyalar, kendi Placement'ini geometriye pisirir (transformShape(m, True)), istenirse v kadar tasir.
    Placement tasiyan sekil Part::Feature'a atanip kaydedilince konum kaybolabiliyor ve eklem cercevelerini bozuyordu."""
    s = sh.copy()
    pl = s.Placement
    if not pl.isIdentity():
        s.Placement = App.Placement()
        s.transformShape(pl.toMatrix(), True)
    if v is not None and V(v).Length > 1e-12:
        m = App.Matrix()
        m.move(V(v))
        s.transformShape(m, True)
    return s


def tasi(sh, v):
    return pisir(sh, v)


def am_sekil(sh):
    sol = sh.Solids
    if not sol:
        return sh.BoundBox.Center, 0.0
    vt = sum(s.Volume for s in sol)
    c = V(0, 0, 0)
    for s in sol:
        c = c + s.CenterOfMass * (s.Volume / vt)
    return c, vt


def ekle(ad, modul, grup, shape, kutle, tur, malzeme, kod, renk, not_="", durum="yeni", baski=None, merkez=None, kaynak=""):
    shape = pisir(shape)
    if merkez is None:
        merkez, _ = am_sekil(shape)
    P.append(dict(ad=ad, modul=modul, grup=grup, shape=shape, kutle=float(kutle), merkez=V(merkez), tur=tur, malzeme=malzeme, kod=kod,
                  renk=renk, not_=not_, durum=durum, baski=baski, kaynak=kaynak, v=None))
    return P[-1]


def bag(ad, tip, adet, parcalar, aciklama="", durum="yeni"):
    BAGLAR.append(dict(ad=ad, tip=tip, adet=adet, parcalar=list(parcalar), aciklama=aciklama, durum=durum))


# ====================================================================== 1) mevcut modulleri yukle
MOD = {}
for ad in MD.SIRA:
    d = MD.yukle(ad)
    MOD[ad] = d
    for p in d["parcalar"]:
        if p["haric"]:
            continue
        p["g"] = MD.global_sekil(p["shape"], ad)
        p["gmerkez"] = MD.global_nokta(ad, p["merkez"])
        ESKI.append(dict(ad=p["ad"], modul=ad, grup=p["grup"], shape=p["g"], kutle=p["kutle"], merkez=p["gmerkez"], renk=p["renk"],
                         tur=p["tur"]))
    log("yuklendi", ad, sum(1 for p in d["parcalar"] if not p["haric"]))
import kabuk_parcalar as KAB
import kafa_parcalar as KP
import dirsek_parcalar as DP
import omuz_parcalar as OP
import taban_parcalar as TP
from kabuk_lib import kesit_param, rrect_wire, yuzey, damla, screw7380


def _baski_bilgisi(modul, ad):
    """Mevcut modullerin baski yonu tablolari (robot yerelinde 'yukari'); bilinmiyorsa None (en iyi yon hesaplanir)."""
    for tb in ({"kabuk": KAB.BASKI, "kafa": KP.BASKI, "taban": TP.BASKI}.get(modul, {}),
               DP.BASKI if modul.startswith("dirsek") else {}):
        if ad in tb:
            y = tb[ad]["yukari"]
            y = V(*y) if not isinstance(y, App.Vector) else V(y)
            if modul.endswith("_sol"):
                y.x = -y.x
            return dict(yukari=(y.x, y.y, y.z), yon=tb[ad]["yon"])
    return None


def mevcut(modul, p, shape=None, v=None, durum=None, grup=None, kutle=None, ad=None, not_=None, kod=None):
    """Mevcut parcayi (global) ekler; v ile tasir, shape verilirse degisti sayar."""
    sh = shape if shape is not None else p["g"]
    if v is not None and v.Length > 1e-9:
        sh = tasi(sh, v)
        mer = None if shape is not None else p["gmerkez"] + v
        d_ = durum or "tasindi"
    else:
        mer = None if shape is not None else p["gmerkez"]
        d_ = durum or ("degisti" if shape is not None else "ayni")
    q = ekle(ad or p["ad"], modul, grup or p["grup"], sh, p["kutle"] if kutle is None else kutle, p["tur"], p["malzeme"],
             kod or p["kod"], p["renk"], not_=p["not_"] if not_ is None else not_, durum=d_, baski=_baski_bilgisi(modul, p["ad"]),
             merkez=mer, kaynak=modul)
    if shape is None and d_ in ("ayni", "tasindi"):
        q["v"] = V(v) if v is not None else V(0, 0, 0)       # eski robota gore rijit oteleme (yerlesim kontrolu ciftleri eler)
    return q


# ====================================================================== 2) iskelet: uzun direk, travers DY yukari
for p in MOD["iskelet"]["parcalar"]:
    if p["haric"]:
        continue
    if p["ad"] == "Govde diregi":
        sh = sigma_y(A.DIREK_Y0, TA.DIREK_Y1_YENI)
        m = sh.Volume / 1000.0 * A.SG_RHO
        mevcut("iskelet", p, shape=sh, kutle=m, kod="Sigma 40x40 agir kanal 10, %.1f mm" % TA.DIREK_L_YENI,
               not_="1 m stok yetmez: 1,5 / 2 m boy ya da ozel kesim (acik is); eski 800,5 mm")
        DEGISEN.append(("Iskelet", "Govde diregi", "800,5 -> %.1f mm (sigma 40x40 agir, %.0f -> %.0f g)" % (TA.DIREK_L_YENI, p["kutle"], m)))
    elif p.get("alt_grup") == "Travers":
        mevcut("iskelet", p, v=DYV)
    else:
        mevcut("iskelet", p)
DEGISEN.append(("Iskelet", "Omuz traversi + 2 ust kose baglantisi", "%.0f mm yukari (omuz ekseni %.0f -> %.0f)" % (DY, A.S3, TA.S3_YENI)))

# ====================================================================== 3) omuz: DY yukari, ust kol tupu +30
YC_TUP = A.DIRSEK["tup_uc_y"]
for side in ("sag", "sol"):
    ad = "omuz_" + side
    for p in MOD[ad]["parcalar"]:
        if p["haric"]:
            continue
        if p["ad"] == "Ust kol tupu":
            ek = cyl(28.0, (OP.XR, YC_TUP + 0.01, OP.ZC), (OP.XR, YC_TUP - TA.UST_KOL_UZAMA, OP.ZC))
            ek = ek.cut(cyl(OP.R_TUP_IC, (OP.XR, YC_TUP + 1, OP.ZC), (OP.XR, YC_TUP - TA.UST_KOL_UZAMA - 1, OP.ZC)))
            yerel = p["shape"].fuse(ek).removeSplitter()
            g = tasi(MD.global_sekil(yerel, ad), DYV)
            m = g.Volume / 1000.0 * (A.OMUZ["baski_rho"]["PETG"][0] * A.OMUZ["baski_rho"]["PETG"][1])
            mevcut(ad, p, shape=g, kutle=m, not_="ust kol tupu 100 -> %.0f mm (taslak); pencere ve civata delikleri ayni" % (100 + TA.UST_KOL_UZAMA))
        else:
            mevcut(ad, p, v=DYV)
DEGISEN.append(("Omuz (sag + sol)", "tum omuz", "%.0f mm yukari" % DY))
DEGISEN.append(("Omuz (sag + sol)", "Ust kol tupu", "100 -> %.0f mm (PETG); dirsek catali tupun yeni ucunda" % (100 + TA.UST_KOL_UZAMA)))

# ====================================================================== 4) dirsek: DY - 30, el yakasi +19
V_DIR = V(0, DY - TA.UST_KOL_UZAMA, 0)
Y_KES = DP.Y(DP.S_YAKA[1])                       # el yakasinin bittigi yer (koni baslangici), omuz yereli
for side in ("sag", "sol"):
    ad = "dirsek_" + side
    for p in MOD[ad]["parcalar"]:
        if p["haric"]:
            continue
        if p["ad"] == "El":
            s0 = p["shape"]
            ust = s0.common(box(-1e3, 1e3, Y_KES, 1e3, -1e3, 1e3))
            alt = tasi(s0.common(box(-1e3, 1e3, -1e3, Y_KES, -1e3, 1e3)), V(0, -TA.EL_UZAMA, 0))
            boyun = cyl(17.0, (DP.XW, Y_KES + 0.01, DP.ZE), (DP.XW, Y_KES - TA.EL_UZAMA - 0.01, DP.ZE))
            boyun = boyun.cut(cyl(11.0, (DP.XW, Y_KES - 1.5, DP.ZE), (DP.XW, Y_KES - TA.EL_UZAMA + 1.5, DP.ZE)))
            yerel = ust.fuse([boyun, alt]).removeSplitter()
            g = tasi(MD.global_sekil(yerel, ad), V_DIR)
            m = g.Volume / 1000.0 * RHO_PETG08
            mevcut(ad, p, shape=g, kutle=m, not_="el yakasi %.0f mm uzatildi (ici O22 bos, uclari 1,5 mm kapali); taslak" % TA.EL_UZAMA)
        else:
            mevcut(ad, p, v=V_DIR)
DEGISEN.append(("Dirsek + el (sag + sol)", "tum dirsek", "%.0f mm yukari (omuzla birlikte %.0f, tup uzadi -%.0f)" % (
    DY - TA.UST_KOL_UZAMA, DY, TA.UST_KOL_UZAMA)))
DEGISEN.append(("Dirsek + el (sag + sol)", "El", "yaka %.0f mm uzadi (O34 / O22 bos); el ucu omuz ekseninden %.1f -> %.1f mm (x%.3f)" % (
    TA.EL_UZAMA, TA.KOL_BOY_ESKI, TA.KOL_BOY_YENI, TA.KOL_ORAN)))
bag("Ust kol tupu -> dirsek catali", "pim + yarikli sikma bilezigi, 2x M3 (degismedi; tupun yeni ucunda)", 2,
    ("Ust kol tupu", "Dirsek catali"), durum="tasindi")

# ====================================================================== 5) kafa: Govde + Pan DY, catal H yukari, yeni Bas
import kafa10 as K10
KP_BAS, KAFA_BAG, KAFA_INFO, KAFA_DENGE = K10.dengele(log=log)
YT_YENI = TA.KAFA_ALT_YEREL - TA.KAFA_GOVDE_Y[0] - KAFA_INFO["dy"]      # tilt ekseni, kafa yereli (eski 130)
H_ADAPTOR = YT_YENI - TA.TILT_ESKI_Y
KAFA_O = V(*A.MODULLER["kafa"]["konum"]) + DYV                          # kafa yerel orijini (global)
V_PAN = V(0, H_ADAPTOR, 0)
PAN_KALKAN = ("Egme catali", "Tilt servosu MG996R", "Tilt servosu cikis mili", "Tilt servosu kulak civatasi M4x16", "Tilt servosu kontra somunu M4",
              "625ZZ rulman (ic bilezik)", "Pim pulu M5", "Pim civatasi M5x12", "Isil gomme somun M5 (catal)")
log("kafa: dy %.2f zb %.2f, tilt ekseni yerel y %.2f (eski %.0f), adaptor %.2f mm" % (KAFA_INFO["dy"], KAFA_INFO["zb"], YT_YENI, TA.TILT_ESKI_Y, H_ADAPTOR))
kald = 0
for p in MOD["kafa"]["parcalar"]:
    if p["haric"]:
        continue
    g = p.get("alt_grup", p["grup"])
    if g == "Govde":
        mevcut("kafa", p, v=DYV)
    elif g == "Pan":
        if p["ad"] == "Catal-mil civatasi M3x8":
            kald += 1
            continue
        mevcut("kafa", p, v=DYV + (V_PAN if p["ad"] in PAN_KALKAN else V(0, 0, 0)))
    else:
        continue          # eski Bas grubu: kafa10 yeni kafayi kurar (tilt horn, horn vidasi, 625ZZ dis, yanak civatalari dahil)
DEGISEN.append(("Kafa", "Govde (boyun plakasi, servo yuvasi, 6808 cifti, pan servosu) + boyun mili", "%.0f mm yukari (degismedi)" % DY))
DEGISEN.append(("Kafa", "Egme catali + tilt servosu + 625ZZ pimi", "%.1f mm daha yukari: boyun yukseltme adaptoru (yeni); tilt ekseni kafa yerelinde %.0f -> %.1f" % (
    H_ADAPTOR, TA.TILT_ESKI_Y, YT_YENI)))
DEGISEN.append(("Kafa", "Catal-mil civatasi M3x8 (4)", "kaldirildi: yerine 4x M3 saplama + pul + DIN 985 (catal + adaptor birlikte)"))
for p in K10.adaptor(H_ADAPTOR, log=log):
    ekle(p["ad"], "kafa", "Boyun", tasi(p["shape"], KAFA_O), p["kutle"], p["tur"], p["malzeme"], p["kod"], p["renk"], not_=p["not_"],
         baski=p["baski"], merkez=p["merkez"] + KAFA_O, kaynak="kafa10.adaptor")
bag("Boyun yukseltme adaptoru + egme catali -> boyun mili flansi", "4x M3 saplama DIN 976 (mevcut M3 isil gomme somunlara) + pul + M3 DIN 985",
    4, ("Egme catali", "Boyun yukseltme adaptoru", "Boyun mili"), "adaptor h = %.1f mm; catal tabani adaptor ustunde" % H_ADAPTOR)
V_BAS = KAFA_O + V(0, YT_YENI, TA.KAFA_TILT_Z)                           # eksen cercevesi -> global
TEKRAR = set(K10.TEKRAR)
for p in KP_BAS:
    ekle(p["ad"], "kafa", "Bas", tasi(p["shape"], V_BAS), p["kutle"], p["tur"], p["malzeme"], p["kod"], p["renk"], not_=p["not_"],
         durum="tasindi" if p["ad"] in TEKRAR else "yeni", baski=p["baski"], merkez=p["merkez"] + V_BAS, kaynak="kafa10")
for b in KAFA_BAG:
    bag(b["ad"], b["tip"], b["adet"], b["parcalar"])
DEGISEN.append(("Kafa", "Bas grubu (iskelet, on/arka kabuk, 7\" LCD, vizor, kamera, Pi 5)", "yeni kafa: 270 x 215 x %.0f, 10,1\" HDMI ekran (tahmini model), "
                "4 kabuk baski parcasi (sag/sol), tilt ekseni kafa AM'sinde, tilt %+.0f...%+.0f" % (
                    K10.ZF - KAFA_INFO["zb"], TA.TILT_ARALIK[0], TA.TILT_ARALIK[1])))
DEGISEN.append(("Kafa", "Vizor (siyah akrilik)", "kaldirildi: 10,1\" ekranin cami yuz; cerceveyi on kabuk yapar"))

# ====================================================================== 6) kabuk: ust kisim DY, uzatma bantlari, braketler, (taban genisse) etek
T, H, W = A.KABUK_T, A.KABUK_T / 2, A.KABUK_BINDIRME
GB_BOS = A.KABUK_BINDIRME_BOSLUK
BOSS_L = A.INSERT[3][1] + 0.5 + 1.0
GK = A.GOVDE_KESIT
DX = TA.TABAN_DX
ETEK_AD = ("Etek arka", "Etek orta", "Etek on")


def etek_tarafi(p):
    """TABAN_DX > 0 icin: etek parcasi (ya da eteke ait eleman) hangi yana kayar: +1 / -1 / 0 (kaymaz)."""
    ad = p["ad"]
    if ad.startswith(ETEK_AD):
        return 1 if ad.endswith("sag") else -1
    if "(etek x0" in ad:                         # x = 0 dikisi: somun sag dilde, civata sag dile girer -> sag ile kayar
        return 1
    if "(etek z" in ad or "Etek braketi" in ad:
        return 1 if p["gmerkez"].x > 0 else -1
    return 0


kab_ust = kab_alt = 0
VIDA_A = [v for v in KAB.VIDA if v.get("tip") == "bindirme" and v["etiket"].startswith("govde y") and abs(v["p"].y - (TA.UZATMA_Y0 + W / 2)) < 4.0]
ETEK_BRAKET_P = []
for p in MOD["kabuk"]["parcalar"]:
    if p["haric"]:
        continue
    cy = p["gmerkez"].y                          # agirlik merkezi (B-spline sinir kutusu gevsek: arka kapak 263...690 cikiyordu)
    if cy > TA.UST_ESIK_Y:
        mevcut("kabuk", p, v=DYV)
        kab_ust += 1
    elif DX > 0 and etek_tarafi(p) != 0:
        if p["ad"].startswith("Etek braketi") and p["tur"] == "Satin":
            ETEK_BRAKET_P.append(p)              # yeniden kurulur (asagida)
            continue
        if p["ad"].startswith("Civata M6x") and "(Etek braketi" in p["ad"] or p["ad"].startswith(("Pul M6 (Etek", "Cekic somun M6 (Etek")):
            mevcut("kabuk", p)                   # uzun raya giden M6 yerinde
            continue
        if p["ad"].startswith(ETEK_AD):
            continue                             # etek bantlari asagida (sonar delikleri yeniden)
        mevcut("kabuk", p, v=V(etek_tarafi(p) * DX, 0, 0), not_=p["not_"] + " (taban genisletme: yana kaydi)")
        kab_alt += 1
    elif p["ad"].startswith("Bindirme civatasi") and any(("(%s)" % v["etiket"]) in p["ad"] for v in VIDA_A):
        continue                                 # A dikisi civatasi: asagida uzatma bandinin dis yuzune gore yeniden oturtulur
    else:
        mevcut("kabuk", p)
        kab_alt += 1
log("kabuk: ust %d parca DY tasindi, alt %d" % (kab_ust, kab_alt))
DEGISEN.append(("Kabuk", "Govde orta/gogus/omuz bantlari, arka kapak, Nextion, S1 kasetleri, ust govde braketleri", "%.0f mm yukari" % DY))
DEGISEN.append(("Kabuk", "Nextion 10,1\" gogus ekrani", "yerinde birakildi (karar acik), %.0f mm yukari: merkez y %.0f -> %.0f" % (DY, A.GOGUS_Y, A.GOGUS_Y + DY)))

# --- uzatma bantlari: sabit kesit s(488,5) [ust uc dili GK egimine uyar]; sag/sol, bindirme dili kabuk modulunun kurali
YA, YB_ = TA.UZATMA_DIKIS[0], TA.UZATMA_DIKIS[-1]
(a_c, bf_c, bb_c, r_c), _ = kesit_param(GK, YA + W)
KC = [(YA - 1.0, a_c, bf_c, bb_c, r_c), (YB_ + 1.0, a_c, bf_c, bb_c, r_c)]
s_a0, _ = kesit_param(GK, YA)
s_a1, _ = kesit_param(GK, YA + W)
GK_UC = [(YB_ - 1.0,) + tuple(s_a0[k] - (s_a1[k] - s_a0[k]) / W for k in range(4)), (YB_,) + tuple(s_a0), (YB_ + W,) + tuple(s_a1),
         (YB_ + W + 1.0,) + tuple(s_a1[k] + (s_a1[k] - s_a0[k]) / W for k in range(4))]


def _prizma(e, y0, y1):
    return Part.Face(rrect_wire(y0, a_c - e, bf_c - e, bb_c - e, r_c - e)).extrude(V(0, y1 - y0, 0))


def _loft(e, secs):
    return Part.makeLoft([rrect_wire(y, a - e, bf - e, bb - e, r - e) for (y, a, bf, bb, r) in secs], True, True)


S_main = _prizma(0.0, YA, YB_).cut(_prizma(T, YA - 1, YB_ + 1))
M_main = _prizma(H, YA - 1, YB_ + 1)
S_top = _loft(0.0, GK_UC[1:3]).cut(_loft(T, GK_UC))
M_top = _loft(H, GK_UC)
S_dis = S_main.cut(M_main)
S_ic = S_main.common(M_main).fuse(S_top.common(M_top)).removeSplitter()
S_bos = S_main.common(M_main).cut(_prizma(H + GB_BOS, YA - 1, YB_ + 1)).fuse(S_top.common(M_top).cut(_loft(H + GB_BOS, GK_UC)))
BIG = 3000.0


def kutu(x0=-BIG, x1=BIG, y0=-BIG, y1=BIG, z0=-BIG, z1=BIG):
    return box(x0, x1, y0, y1, z0, z1)


UZ = {}
for k in range(TA.UZATMA_BANT):
    s0, s1 = TA.UZATMA_DIKIS[k], TA.UZATMA_DIKIS[k + 1]
    for sag in (True, False):
        r_dis = kutu(*((0, BIG) if sag else (-BIG, 0))).common(kutu(y0=s0, y1=s1))
        r_ic = kutu(*((-W, BIG) if sag else (-BIG, -W))).common(kutu(y0=s0 + W, y1=s1 + W))
        dil = S_ic.common(r_ic).cut(S_bos.common(r_ic.cut(r_dis)))
        UZ["Govde uzatma bandi %d %s" % (k + 1, "sag" if sag else "sol")] = dict(shape=S_dis.common(r_dis).fuse(dil).removeSplitter(), k=k, sag=sag)
EK_UZ = {a_: [] for a_ in UZ}
CK_UZ = {a_: [] for a_ in UZ}


def sahip_uz(pt):
    pt = V(*pt)
    for a_, d_ in UZ.items():
        if d_["shape"].BoundBox.isInside(pt) and d_["shape"].isInside(pt, 1e-6, True):
            return a_
    return None


ASAGI = V(0, -1, 0)              # bantlar dik basilir (alt kenari tablada): damla ucu asagi
YENI_VIDA = []
# A dikisi (476,5): mevcut civata + somun yerinde; bant 1'in alt dudagina delik; civata basi bandin dis yuzune oturtulur
for v in VIDA_A:
    p, n, hn = v["p"], v["n"], v["hn"]
    dis = sahip_uz(p + n * (hn * 0.5))
    if dis is None:
        log("UYARI A dikisi civatasi uzatma bandinda sahipsiz", v["etiket"])
        continue
    CK_UZ[dis].append(cyl(CLEAR[3] / 2, p - n * 1.0, p + n * (hn + 3.0)))
    # bant dis yuzu (sabit kesit) ile eski dudak yuzu farki: civata n boyunca o kadar disari
    yer = v["etiket"].split()[-1]
    fark = {"on": bf_c - kesit_param(GK, p.y)[0][1], "arka": bb_c - kesit_param(GK, p.y)[0][2]}.get(yer, a_c - kesit_param(GK, p.y)[0][0])
    YENI_VIDA.append(dict(etiket=v["etiket"] + " (A, uzatma bandi)", p=p + n * fark, n=n, hn=hn, ic=None, dis=dis, tip="A", eski=v))
# B dikisi (ara) ve bant ici x = 0 dikisleri: yeni boss + somun + civata
for k in range(1, TA.UZATMA_BANT):
    ym = TA.UZATMA_DIKIS[k] + W / 2
    f = 0.55 * (a_c - r_c)
    aday = [("on", sx * f) for sx in (1, -1)] + [("arka", sx * f) for sx in (1, -1)] + [("sag", 0.0), ("sol", 0.0)]
    for (yer, u) in aday:
        p, n, hn = yuzey(KC, yer, ym, u)
        YENI_VIDA.append(dict(etiket="uzatma y%.0f %s %+.0f" % (TA.UZATMA_DIKIS[k], yer, u), p=p, n=n, hn=hn, tip="B"))
for k in range(TA.UZATMA_BANT):
    ym = 0.5 * (TA.UZATMA_DIKIS[k] + TA.UZATMA_DIKIS[k + 1]) + W / 2
    for yer in ("on", "arka"):
        for dyy in (-55.0, 55.0):
            p, n, hn = yuzey(KC, yer, ym + dyy, -W / 2)
            YENI_VIDA.append(dict(etiket="uzatma bant %d x0 %s y%.0f" % (k + 1, yer, ym + dyy), p=p, n=n, hn=hn, tip="X"))
for v in YENI_VIDA:
    if v["tip"] == "A":
        continue
    p, n, hn = v["p"], v["n"], v["hn"]
    ic, dis = sahip_uz(p - n * (hn * 0.5)), sahip_uz(p + n * (hn * 0.5))
    if ic is None or dis is None or ic == dis:
        log("UYARI uzatma civatasi yerlesmedi", v["etiket"], ic, dis)
        v["atla"] = True
        continue
    v["ic"], v["dis"] = ic, dis
    EK_UZ[ic].append(damla(p, n * -1, 4.0, BOSS_L, ASAGI))
    CK_UZ[ic].append(insert_hole(3, p, n * -1, extra=0.5))
    CK_UZ[dis].append(cyl(CLEAR[3] / 2, p - n * 1.0, p + n * (hn + 1.0)))
# C dikisi (uzatma ustu = tasinan orta bandin alt dudagi): A dikisindeki somun + civata DY yukarida, boss bant 2'nin dilinde
for v in VIDA_A:
    p, n = v["p"] + DYV, v["n"]
    ic = sahip_uz(p - n * (v["hn"] * 0.5))
    if ic is None:
        log("UYARI C dikisi dili bulunamadi", v["etiket"])
        continue
    EK_UZ[ic].append(damla(p, n * -1, 4.0, BOSS_L, ASAGI))
    CK_UZ[ic].append(insert_hole(3, p, n * -1, extra=0.5))
    YENI_VIDA.append(dict(etiket=v["etiket"].replace("govde", "uzatma ustu") + " (C)", p=p, n=n, hn=v["hn"], ic=ic, dis="Govde orta bandi", tip="C", eski=v))

# --- uzatma bandi govde braketleri (kabuk_parcalar govde braketiyle ayni olcu ve eleman; kesit sabit)
GB = A.KABUK_GOVDE_BRAKET
d6, L6 = GB["civata_m6"]
d5, L5 = GB["civata_m5"]
t5 = WASH125[5][2]
BR_YER = []
for yb in TA.UZATMA_BRAKET_Y:
    yc = yb + GB["m5_y"]
    xw = a_c - GB["insert_bosluk"]
    for sx in (1, -1):
        ic = sahip_uz(V(sx * (a_c - T + 0.5), yc, 0.0))
        EK_UZ[ic].append(damla(V(sx * xw, yc, 0.0), V(sx, 0, 0), 7.0, (a_c - H) - xw, ASAGI))
        CK_UZ[ic].append(insert_hole(5, V(sx * xw, yc, 0.0), V(sx, 0, 0), extra=0.5))
        BR_YER.append((yb, yc, sx, xw, ic))

for a_, d_ in UZ.items():
    sh = d_["shape"]
    if EK_UZ[a_]:
        sh = sh.fuse(EK_UZ[a_])
    for tl in CK_UZ[a_]:
        sh = sh.cut(tl)
    sh = sh.removeSplitter()
    if len(sh.Solids) > 1:
        ana = max(sh.Solids, key=lambda s_: s_.Volume)
        log("  %s: %d kati (kucukler atildi %s)" % (a_, len(sh.Solids), [round(s_.Volume, 2) for s_ in sh.Solids if s_ is not ana]))
        sh = ana
    d_["shape"] = sh
    m = sh.Volume / 1000.0 * A.PETG_RHO * A.KABUK_DOLULUK
    ekle(a_, "kabuk", "Kabuk", sh, m, "Baski", "PETG", "PETG baski, 3,0 mm duvar", "kabuk",
         not_="uzatma bandi (taslak): sabit kesit %.1f x %.1f/%.1f r%.0f, yukseklik %.1f + 12 dil; bindirme kurali kabuk moduluyle ayni" % (
             2 * a_c, bf_c, bb_c, r_c, TA.DY / TA.UZATMA_BANT),
         baski=dict(yukari=(0, 1, 0), yon="dik (alt kenari tablada)"), kaynak="taslak")
DEGISEN.append(("Kabuk", "Govde uzatma bandi 1-2 x sag/sol (4 yeni baski parcasi)", "476,5 dikisine %.0f mm sabit kesit (%.0f x %.0f, r%.0f), 2 bant; "
                "kesit dikis ustunun 12 mm ustundeki kesit (alt bant diline 0,25 bosluk), bu yuzden alt ve ust dikiste 0,7 mm disa basamak" % (
                    DY, 2 * a_c, bf_c + bb_c, r_c)))
# bindirme civatalari + somunlar
for v in YENI_VIDA:
    if v.get("atla"):
        continue
    if v["tip"] in ("A", "C"):
        e = v["eski"]
        ins = min([p for p in MOD["kabuk"]["parcalar"] if p["ad"] == "Isil gomme somun M3 (%s)" % e["etiket"]],
                  key=lambda q: (q["gmerkez"] - e["p"]).Length)        # ayni adli iki eleman (sx = +-1): en yakini
        civ = min([p for p in MOD["kabuk"]["parcalar"] if p["ad"] == "Bindirme civatasi M3x6 (%s)" % e["etiket"]],
                  key=lambda q: (q["gmerkez"] - e["p"]).Length)
        if v["tip"] == "A":       # somun yerinde (mevcut parca, eklendi), civata uzatma bandinin dis yuzune
            sh = screw7380(3, 6.0, v["p"] + v["n"] * (v["hn"] + 0.05), v["n"] * -1)
            mevcut("kabuk", civ, shape=sh, durum="degisti", not_="A dikisi: dudak artik uzatma bandi (dis yuzu %.2f mm disarida)" % (v["p"] - e["p"]).Length)
        else:
            mevcut("kabuk", ins, v=DYV, ad=ins["ad"].replace("govde", "uzatma ustu"), durum="yeni")
            mevcut("kabuk", civ, v=DYV, ad=civ["ad"].replace("govde", "uzatma ustu"), durum="yeni")
        continue
    sh = insert(3, v["p"], v["n"] * -1)
    ekle("Isil gomme somun M3 (%s)" % v["etiket"], "kabuk", "Kabuk", sh, sh.Volume / 1000 * 8.5, "Baglanti", "Pirinc", "M3 isil gomme somun", "pirinc")
    sh = screw7380(3, 6.0, v["p"] + v["n"] * (v["hn"] + 0.05), v["n"] * -1)
    ekle("Bindirme civatasi M3x6 (%s)" % v["etiket"], "kabuk", "Kabuk", sh, sh.Volume / 1000 * 7.85, "Baglanti", "Celik 10.9", "M3x6 ISO 7380", "celik")
nA = sum(1 for v in YENI_VIDA if v["tip"] == "A")
nB = sum(1 for v in YENI_VIDA if v["tip"] == "B" and not v.get("atla"))
nX = sum(1 for v in YENI_VIDA if v["tip"] == "X" and not v.get("atla"))
nC = sum(1 for v in YENI_VIDA if v["tip"] == "C")
bag("Govde alt bandi dili -> uzatma bandi 1 (A dikisi, y %.1f)" % YA, "M3x6 ISO 7380 + M3 isil gomme somun (alt bant dilindeki mevcut boss)", nA,
    ("Govde alt bandi", "Govde uzatma bandi 1"), "mevcut somunlar; civata basi bandin dis yuzune oturtuldu", durum="degisti")
bag("Uzatma bandi 1 dili -> uzatma bandi 2 (B dikisi, y %.1f)" % TA.UZATMA_DIKIS[1], "M3x6 ISO 7380 + M3 isil gomme somun (dilde damla boss)", nB,
    ("Govde uzatma bandi 1", "Govde uzatma bandi 2"))
bag("Uzatma bandi 2 dili -> govde orta bandi (C dikisi, y %.1f)" % YB_, "M3x6 ISO 7380 + M3 isil gomme somun (dilde damla boss)", nC,
    ("Govde uzatma bandi 2", "Govde orta bandi"), "orta bandin mevcut delikleri; dil GK egimini izler")
bag("Uzatma bantlari sag -> sol (x = 0 dikisi, on + arka)", "M3x6 ISO 7380 + M3 isil gomme somun (sag parcanin dilinde)", nX,
    ("Govde uzatma bandi sag", "Govde uzatma bandi sol"))
# braketler
ALU = "Aluminyum 5754"
for (yb, yc, sx, xw, ic) in BR_YER:
    tb, en = GB["t"], GB["en"] / 2
    xa0, xa1 = sorted((sx * A.SG / 2, sx * (A.SG / 2 + tb)))
    xc0, xc1 = sorted((sx * (xw - tb), sx * xw))
    xb0, xb1 = sorted((sx * A.SG / 2, sx * xw))
    br = box(xa0, xa1, yb, yb + GB["a_boy"], -en, en).fuse(box(xb0, xb1, yb, yb + tb, -en, en)).fuse(box(xc0, xc1, yb, yb + GB["c_boy"], -en, en))
    for dy_ in GB["m6_y"]:
        br = br.cut(cyl(CLEAR[6] / 2, (xa0 - 1, yb + dy_, 0), (xa1 + 1, yb + dy_, 0)))
    br = br.cut(cyl(CLEAR[5] / 2, (xc0 - 1, yc, 0), (xc1 + 1, yc, 0))).removeSplitter()
    ad_b = "Govde braketi %s y%.0f (uzatma)" % ("sag" if sx > 0 else "sol", yb)
    ekle(ad_b, "kabuk", "Kabuk", br, br.Volume / 1000 * 2.68, "Satin", ALU, "Govde braketi 3 mm Al U (bukum)", "alu2")
    for dy_ in GB["m6_y"]:
        yy = yb + dy_
        p_yuz = V(sx * (A.SG / 2 + tb), yy, 0)
        nv = V(sx, 0, 0)
        sh = screw912(6, L6, p_yuz, nv * -1)
        ekle("Civata M6x%d (%s)" % (L6, ad_b), "kabuk", "Kabuk", sh, sh.Volume / 1000 * 7.85, "Baglanti", "Celik 8.8", "M6x%d DIN 912" % L6, "celik")
        sh = hammer_nut(V(sx * (A.SG / 2 - A.LIP), yy, 0), nv, (0, 0, 1))
        ekle("Cekic somun M6 (%s)" % ad_b, "kabuk", "Kabuk", sh, sh.Volume / 1000 * 7.85, "Baglanti", "Celik", "M6 cekic somun, kanal 10", "celik")
    p_c = V(sx * (xw - tb), yc, 0)
    sh = washer(5, p_c, V(-sx, 0, 0))
    ekle("Pul M5 (%s)" % ad_b, "kabuk", "Kabuk", sh, sh.Volume / 1000 * 7.85, "Baglanti", "Celik", "M5 DIN 125 pul", "celik")
    sh = screw912(5, L5, p_c - V(sx * t5, 0, 0), V(sx, 0, 0))
    ekle("Civata M5x%d (%s)" % (L5, ad_b), "kabuk", "Kabuk", sh, sh.Volume / 1000 * 7.85, "Baglanti", "Celik 8.8", "M5x%d DIN 912" % L5, "celik")
    sh = insert(5, V(sx * xw, yc, 0), V(sx, 0, 0))
    ekle("Isil gomme somun M5 (%s)" % ad_b, "kabuk", "Kabuk", sh, sh.Volume / 1000 * 8.5, "Baglanti", "Pirinc", "M5 isil gomme somun", "pirinc")
bag("Uzatma bandi -> govde diregi (bant basina 2 braket)", "3 mm Al U braket: direk +-X kanalina 2x M6x14 pulsuz + cekic somun; kabuk boss'una M5x10 + pul "
    "+ M5 isil gomme somun", len(BR_YER), ("Govde braketi (uzatma)", "Govde diregi", "Govde uzatma bandi"),
    "kabuk modulu govde braketiyle ayni olcu (arayuz.KABUK_GOVDE_BRAKET); y %s" % ", ".join("%.0f" % y for y in TA.UZATMA_BRAKET_Y))
DEGISEN.append(("Kabuk", "Govde braketi (uzatma) x 4", "yeni: bant basina bir cift, direge 2x M6 + cekic somun, kabuga M5 + isil gomme somun"))

# ====================================================================== 7) taban (+ istenirse genisletme)
TEKER_GRUP = {MD.teker_grup(k): (sx, sz) for k, sx, sz in MD.TEKER_KOSE}
for p in MOD["taban"]["parcalar"]:
    if p["haric"]:
        continue
    if DX > 0:
        if p.get("alt_grup") == "Tahrik":
            sx = 1 if p["gmerkez"].x > 0 else -1
            if p["ad"].startswith("Cekic somun M4 (braket"):
                c = p["gmerkez"] + V(sx * DX, 0, 0)
                sh = nut(4, (c.x, A.Y_RAIL0, c.z), (0, 1, 0), "985")
                ekle(p["ad"].replace("Cekic somun M4", "Somun M4 DIN 985"), "taban", p["grup"], sh, sh.Volume / 1000 * 7.85, "Baglanti", "Celik",
                     "M4 DIN 985 kontra somun", "celik", durum="degisti", not_="taban genisletme: braket civatasi raya degil plakaya")
                continue
            mevcut("taban", p, v=V(sx * DX, 0, 0), not_=p["not_"] + " (taban genisletme)")
            continue
        if p["ad"] == "Alt plaka":
            sh = p["g"]
            for sx in (1, -1):
                x0, x1 = sorted((sx * (A.V3_W / 2 - 0.5), sx * (A.V3_W / 2 + DX)))
                sh = sh.fuse(box(x0, x1, A.Y_PL, A.Y_RAIL0, -A.L0 / 2, A.L0 / 2))
            for q in MOD["taban"]["parcalar"]:
                if q["ad"].startswith("Civata M4x16 (braket"):
                    c = q["gmerkez"]
                    sx = 1 if c.x > 0 else -1
                    sh = sh.cut(cyl(CLEAR[4] / 2, (c.x + sx * DX, A.Y_PL - 1, c.z), (c.x + sx * DX, A.Y_RAIL0 + 1, c.z)))
            sh = sh.removeSplitter()
            mevcut("taban", p, shape=sh, kutle=sh.Volume / 1000 * 2.66, not_="taban genisletme: plaka her yana %.0f mm (3 mm Al; rijitlik acik)" % DX)
            continue
        if p["ad"].startswith("Acil stop") or p["ad"].startswith("Ana anahtar"):
            sx = 1 if p["gmerkez"].x > 0 else -1
            mevcut("taban", p, v=V(sx * DX, 0, 0), not_=p["not_"] + " (etekle kaydi)")
            continue
    mevcut("taban", p)

if DX > 0:
    # etek bantlari: sonar deliklerini doldur, yana kaydir, sonar deliklerini eski (sonar) yerinde yeniden ac
    SN = A.SONAR
    SON_CYL = [Part.makeCylinder(SN["delik_r"], 30.0, V(x + dx, SN["y"], A.ETEK_B - 15), V(0, 0, 1)) for x in SN["x"] for dx in (-SN["dx"], SN["dx"])]
    duvar_dis, duvar_ic = KAB.Oe.cut(KAB.Me), KAB.Me.cut(KAB.Ie)
    ETEK_YENI = {}
    for p in MOD["kabuk"]["parcalar"]:
        if not p["ad"].startswith(ETEK_AD):
            continue
        sx = 1 if p["ad"].endswith("sag") else -1
        sh = p["g"]
        if p["ad"].startswith("Etek on"):
            ic_h = box(-W, BIG, -BIG, BIG, -BIG, BIG) if sx > 0 else box(-BIG, -W, -BIG, BIG, -BIG, BIG)
            for c_ in SON_CYL:
                tapa = duvar_dis.common(c_).common(KAB.DIS_HUCRE[p["ad"]]).fuse(duvar_ic.common(c_).common(ic_h))
                if tapa.Volume > 1e-3:
                    sh = sh.fuse(tapa)
        sh = tasi(sh.removeSplitter(), V(sx * DX, 0, 0))
        ETEK_YENI[p["ad"]] = [p, sh]
    # dolgu seritleri (x = 0 kesiti uzatilir): dis + ic yari [-DX, DX], solda dil [-DX-W, -DX]; sagin kaymis dili cikarilir
    def _kesit_uzat(sh, x0, x1):
        ws = sh.slice(V(1, 0, 0), 0.0)
        fs = [Part.Face(w) for w in ws if w.isClosed()]
        out = None
        for f in fs:
            f.translate(V(x0, 0, 0))
            e_ = f.extrude(V(x1 - x0, 0, 0))
            out = e_ if out is None else out.fuse(e_)
        return out
    dolgu = _kesit_uzat(KAB.Se_dis.fuse(KAB.Se_ic), -DX, DX)
    # solda dil (yalniz duvarlarda; ust plakada kabuk modulundeki gibi alin birlesim)
    dolgu = dolgu.fuse(_kesit_uzat(KAB.Se_ic.cut(KAB.Se_bos), -DX - W, -DX).common(box(-BIG, BIG, -BIG, KAB.Y_ETEK_PLAKA, -BIG, BIG)))
    for ad_, (p, sh) in ETEK_YENI.items():
        if ad_.endswith("sag"):
            dolgu = dolgu.cut(sh)
    for c_ in SON_CYL:
        dolgu = dolgu.cut(c_)
    # x = 0 dikisi: sag dildeki mevcut somun/civata (+DX) dolgunun dis yarisindan gecer; sol dikis icin dolgu dilinde yeni boss + somun
    X0_VIDA = [v for v in KAB.VIDA if v.get("tip") == "bindirme" and v["etiket"].startswith("etek x0")]
    sol_vida = []
    for v in X0_VIDA:
        pr = v["p"] + V(DX, 0, 0)
        dolgu = dolgu.cut(cyl(CLEAR[3] / 2, pr - v["n"] * 1.0, pr + v["n"] * (v["hn"] + 1.0))).cut(insert_hole(3, pr, v["n"] * -1, extra=0.5))
        pl = v["p"] - V(DX, 0, 0)
        dolgu = dolgu.fuse(damla(pl, v["n"] * -1, 4.0, BOSS_L, V(0, 1, 0))).cut(insert_hole(3, pl, v["n"] * -1, extra=0.5))
        sol_vida.append(dict(v, p=pl))
    dolgu = dolgu.removeSplitter()
    for ad_, (p, sh) in ETEK_YENI.items():
        if ad_.startswith("Etek on"):
            for c_ in SON_CYL:
                sh = sh.cut(c_)
        sh = sh.removeSplitter()
        mevcut("kabuk", p, shape=sh, kutle=sh.Volume / 1000 * A.PETG_RHO * A.KABUK_DOLULUK, durum="degisti",
               not_="taban genisletme: %+.0f mm yana; sonar delikleri sonar yerinde yeniden" % ((1 if ad_.endswith("sag") else -1) * DX))
    for k_, so in enumerate(sorted(dolgu.Solids, key=lambda s_: s_.CenterOfMass.z)):
        ad_d = "Etek dolgu seridi %s" % ("arka" if so.CenterOfMass.z < 0 else "on")
        ekle(ad_d, "kabuk", "Kabuk", so, so.Volume / 1000 * A.PETG_RHO * A.KABUK_DOLULUK, "Baski", "PETG", "PETG baski, 3,0 mm duvar", "kabuk",
             not_="taban genisletme dolgusu (etek x = 0 kesiti, %.0f mm); sol yanda dil" % (2 * DX), baski=dict(yukari=(0, -1, 0), yon="ters (ust plaka tablada)"))
    for v in sol_vida:
        sh = insert(3, v["p"], v["n"] * -1)
        ekle("Isil gomme somun M3 (%s, dolgu sol)" % v["etiket"], "kabuk", "Kabuk", sh, sh.Volume / 1000 * 8.5, "Baglanti", "Pirinc", "M3 isil gomme somun", "pirinc")
        sh = screw7380(3, 6.0, v["p"] + v["n"] * (v["hn"] + 0.05), v["n"] * -1)
        ekle("Bindirme civatasi M3x6 (%s, dolgu sol)" % v["etiket"], "kabuk", "Kabuk", sh, sh.Volume / 1000 * 7.85, "Baglanti", "Celik 10.9", "M3x6 ISO 7380", "celik")
    bag("Etek sol yarisi -> dolgu seridi dili (taban genisletme)", "M3x6 ISO 7380 + M3 isil gomme somun (dolgu dilinde damla boss)", len(sol_vida),
        ("Etek sol", "Etek dolgu seridi"))
    bag("Etek dolgu seridi -> sag yarinin dili (taban genisletme)", "mevcut x = 0 civata + somunlari (sag yariyla kaydi)", len(X0_VIDA),
        ("Etek dolgu seridi", "Etek sag"), durum="degisti")
    EB = A.KABUK_ETEK_BRAKET
    for p in ETEK_BRAKET_P:
        sx = 1 if p["gmerkez"].x > 0 else -1
        zb = round(p["gmerkez"].z / 5.0) * 5.0
        zb = min(EB["z"], key=lambda z_: abs(z_ - p["gmerkez"].z))
        tb, en = EB["t"], EB["en"] / 2
        yr = A.Y_RAIL1
        xi = EB["x_ic"] + DX
        xh0, xh1 = sorted((sx * EB["x0"], sx * xi))
        xd0, xd1 = sorted((sx * (xi - tb), sx * xi))
        br = box(xh0, xh1, yr, yr + tb, zb - en, zb + en).fuse(box(xd0, xd1, EB["y_alt"], yr + tb, zb - en, zb + en))
        xr = sx * A.UZUN_RAY_X
        br = br.cut(cyl(CLEAR[6] / 2, (xr, yr - 1, zb), (xr, yr + tb + 1, zb))).cut(cyl(CLEAR[3] / 2, (xd0 - 1, EB["m3_y"], zb), (xd1 + 1, EB["m3_y"], zb)))
        br = br.removeSplitter()
        mevcut("kabuk", p, shape=br, kutle=br.Volume / 1000 * 2.68, durum="degisti", not_="taban genisletme: yatay kol %.0f mm uzadi" % DX)
    DEGISEN.append(("Taban (parametre)", "TABAN_W %.0f mm" % TA.TABAN_W, "tahrik (motor, braket, kaplin, teker) her yana %.0f mm; alt plaka genisledi; etek yarilari "
                    "kaydi + 2 dolgu seridi; acil stop / ana anahtar etekle; braket M4'leri plakaya DIN 985" % DX))

# ====================================================================== 8) gruplar ve eklemler (global cerceveler)
GRUP_AD = {"iskelet": {"Iskelet": "Iskelet"}, "kabuk": {"Kabuk": "Kabuk"}}
GRUPLAR = {}            # anahtar (modul, grup) -> dict(isim, etiket)
for ad in MD.SIRA:
    d = MOD[ad]
    for g, et in d["gruplar"]:
        isim = d["on_ek"] if g == d["gruplar"][0][0] and len(d["gruplar"]) == 1 else "%s_%s" % (d["on_ek"], g)
        GRUPLAR[(ad, g)] = dict(isim=isim, etiket=et, modul=ad, grup=g)


def kaydir(ad, grup):
    """Grubun ev pozundaki global oteleme (mevcut modul yerlesimine gore)."""
    if ad in ("omuz_sag", "omuz_sol"):
        return DYV
    if ad in ("dirsek_sag", "dirsek_sol"):
        return V_DIR
    if ad == "kafa":
        return DYV + (V_PAN if grup in ("Boyun", "Bas") else V(0, 0, 0))
    if ad == "iskelet":
        return V(0, 0, 0)
    if ad == "taban" and grup in TEKER_GRUP:
        return V(TEKER_GRUP[grup][0] * DX, 0, 0)
    return V(0, 0, 0)


EKLEMLER = []
for ad in MD.SIRA:
    d = MOD[ad]
    govde = d["gruplar"][0][0]
    if d["baglanti"] is None:
        EKLEMLER.append(dict(tip="Grounded", modul=ad, cocuk=GRUPLAR[(ad, govde)]["isim"]))
    else:
        b = d["baglanti"]
        nok = MD.global_nokta(ad, b["nokta"]) + kaydir(ad, govde)
        EKLEMLER.append(dict(tip="Fixed", modul=ad, ebeveyn=GRUPLAR[(b["modul"], b["grup"])]["isim"], cocuk=GRUPLAR[(ad, govde)]["isim"],
                             ref=b["ref"], nokta=nok, aciklama=b["aciklama"]))
    for e in d["eklemler"]:
        cer = MD.global_cerceve(ad, e["cerceve"])
        v = kaydir(ad, e["cocuk"])
        if ad == "kafa" and e["anahtar"] == "pan":
            v = DYV
        cer = App.Placement(cer.Base + v, cer.Rotation)
        sinir = e["sinir"]
        if ad == "kafa" and e["anahtar"] == "tilt":
            sinir = TA.TILT_ARALIK
        EKLEMLER.append(dict(tip="Revolute", modul=ad, anahtar=e["anahtar"], ad=e["ad"], ebeveyn=GRUPLAR[(ad, e["ebeveyn"])]["isim"],
                             cocuk=GRUPLAR[(ad, e["cocuk"])]["isim"], cerceve=cer, sinir=sinir, kaynak=e["kaynak"]))
for p in P:
    p["grup_isim"] = GRUPLAR[(p["modul"], p["grup"])]["isim"]
DEGISEN.append(("Kafa", "Tilt siniri", "-25...30 -> %+.0f...%+.0f derece (karar)" % TA.TILT_ARALIK))
DEGISEN.append(("Kapsam", "Lidar / lidar diregi / haritalama", "mevcut FreeCAD tasariminda yok; taslakta da yok (otonomi kapsam disi)"))
log("parca: yeni %d (eski %d), grup %d, eklem %d; kafa denge %s" % (len(P), len(ESKI), len(GRUPLAR), len(EKLEMLER), KAFA_DENGE[-1]))


def kutle_am(parcalar):
    m = sum(p["kutle"] for p in parcalar)
    c = V(0, 0, 0)
    for p in parcalar:
        c = c + p["merkez"] * (p["kutle"] / m)
    return m, c
