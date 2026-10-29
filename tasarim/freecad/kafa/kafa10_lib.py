# Lale 1,65 m - YENI KAFA: 10,1" HDMI yuz ekrani, tilt ekseni kafa AM'sinden (FreeCAD 1.1, Part)
# Y2a (26 Ekim 2026): taslak-170/kafa10.py'den kafa modulune tasindi (olculer arayuz.KAFA: ekran, govde_y, kafa_alt_y, denge, tilt).
# kafa_parcalar.py bunu kullanir (kur(dy, zb) + adaptor(h)); dengele() yalniz denge parametresini yeniden bulmak icindir.
#
# Eski kafanin (kafa7_parcalar.py; 125 cm kafa_parcalar) Govde (boyun plakasi, servo yuvasi, 6808 cifti, pan MG996R) ve Pan (pan horn, boyun mili,
# egme catali, tilt MG996R, 625ZZ pimi) gruplari AYNEN kullanilir. Degisen:
#   - Boyun yukseltme adaptoru (yeni, PETG): boyun mili flansi (y 96) ile egme catali arasina girer; catal + tilt servosu + pim H kadar
#     yukari kalkar. Catalin 4x M3x8 civatasi yerine 4x M3 saplama (DIN 976) + pul + M3 DIN 985: saplama mil flansindaki mevcut
#     isil gomme somunlara vidalanir, catal tabanini ve adaptoru birlikte sikar.
#   - Kafa (Bas) grubu yeniden: kafa iskeleti (tabla + yanaklar), on (yuz) ve arka kabuk (her biri sag/sol iki baski parcasi, x = 0
#     dikisinde bindirme dili), 10,1" ekran + 4 tutucu tirnak, Camera Module 3, Pi 5 + 5 V cevirici + amfi (tablada, ekranin arkasi).
#     Eski tilt horn'u, horn vidasi, 625ZZ dis bilezigi ve 4 yanak-horn civatasi aynen (eksene gore ayni yerde).
# Denge: tilt ekseni kafa (Bas) grubunun AM'sinden gecsin diye ekranin eksene gore yuksekligi (dy) ve arka kabugun derinligi (zb)
#   dengele() ile cozulur (sekant). Ekran onde (catal on agi tilt suprulmesinde ekran arkasina degmesin diye cam onu eksenin 44 mm
#   onunde); Pi 5, cevirici, tabla ve derin arka kabuk karsi agirlik.
# Cerceve: "eksen cercevesi" = tilt ekseni orijinde (x ekseni boyunca), Y yukari, Z ileri. Kafa yereline: + (0, yT, KAFA_TILT_Z).
import os, sys, math, time

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "kabuk"), os.path.join(UST, "dirsek")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from kafa_lib import *   # noqa  (ortak_lib + MG, HORN_MG, kafa_kutu, yuv_dikdortgen_*, pi5_kafa, CAM, CEV, AMP, screw7380 ...)
import arayuz as A
from kabuk_lib import damla

E10 = A.KAFA["ekran"]
KAFA_GOVDE_Y = A.KAFA["govde_y"]          # kafa kabugu alt / ust dis yuzu, ekran merkezine gore (-100, 115)
KX = 135.0                  # kafa yari genisligi (cam 253,96 + 2 x (0,5 bosluk + 2 cerceve) + duvar; eski 105)
KT = 2.5                    # kabuk duvari (eski kafa ile ayni)
R_ON, R_K = 20.0, 5.0       # Z'ye paralel kenar yaricapi, on/arka yuz kenar yaricapi (5: alt cerceve dikis boss'u duz yuzde kalsin)
ZF = 47.0                   # on dis yuz (eksenden); cam onu ZF - KT - 0,5 = 44
Z_CAM_ON = ZF - KT - 0.5    # 44 cam on yuzu
Z_DIKIS = 10.0              # on / arka kabuk ayrimi; arka kabugun dili on kabuga 6 mm girer
DIL_W = 16.0                # sag/sol bindirme dili (kabukta 12; kafada kamera boss'lari x -13...-8 dilin icinde kalsin diye 16)
GB_BOS = A.KABUK_BINDIRME_BOSLUK
Y_TABLA = (27.0, 32.0)      # kafa tablasi (eksenden): catal kulak plakasi ust kosesi tilt +-15'te y 23,7'ye cikar -> 3,3 mm pay
TABLA_X = 112.0             # tabla yari genisligi (224 <= 230 baski hedefi)
LEDGE = dict(x0=100.0, y=(19.0, Y_TABLA[0]), w=8.0, civata_x=106.0)   # arka kabuk yan duvarinda tabla rafi (2 / taraf)
YARIK = dict(x=38.0, z_on=41.0, h=12.0, r=12.0)  # kafa alt duvarinda boyun acikligi: R30 boyun x tilt +-15 suprulmesi + 3 mm; arka duvarin
                                                # altinda 12 mm centik (tilt -15'te arka-alt kose rulman yuvasina iner)
CAM_Y = 101.0               # kamera lens ekseni (ekran merkezine gore), ekranin ustunde
Z_CAM = ZF - KT - 6.5       # kamera PCB on yuzu (eski kafada on duvar icinden 6,5 geride)
TIRNAK_X = (-80.0, 80.0)    # ekran tutucu tirnaklari (ust ve alt kenar)
DOLULUK = 0.80              # kucuk PETG parcalar (eski kafa ile ayni, tahmini)
HAVSA = 1.7                 # tepe dikis civatalari: ISO 7380 basi (k 1,65) yuzeyin altinda
RHO = {"PETG": A.PETG_RHO, "Aluminyum": 2.70, "Celik": 7.85, "Celik 8.8": 7.85, "Celik 10.9": 7.85, "Pirinc": 8.50, "Kopuk": 0.10}
BIG = 1000.0

# eski kafa sabitleri (eski kafa yerelinde): tilt ekseni (130, 25), yanak x araliklari, horn delikleri
import kafa7_parcalar as KP  # noqa  125 cm kafasi (gruplar Govde / Pan / Kafa); yeniden kullanilan parcalar buradan
YT0, ZT0 = KP.YT, KP.ZT
OFS0 = V(0, -YT0, -ZT0)      # eski kafa yereli -> eksen cercevesi


def _ax(p):
    return V(p.x, p.y - YT0, p.z - ZT0)


HORN_T = [_ax(h) for h in KP.HORN_T]
X_SAG, X_SOL, X_RUL = KP.X_SAG, KP.X_SOL, KP.X_RUL
TEKRAR = ("Tilt horn 25T aluminyum disk", "Tilt horn merkez vidasi M3", "625ZZ rulman (dis bilezik)", "Yanak-horn civatasi M3x8")


def _kutu(e, yb, yu, zb):
    return kafa_kutu(-KX + e, KX - e, yb + e, yu - e, zb + e, ZF - e, R_ON - e, R_K - e)


def lcd10_local():
    """Waveshare 10.1" (B) govdesi (robot_cad lcd10() ile ayni hacim): cam onu z = 0, merkez orijinde, -Z arkaya."""
    l, h = E10["cam"]
    pt, ki, kt = E10["panel_t"], E10["kart_ic"], E10["kart_t"]
    s = box(-l / 2, l / 2, -h / 2, h / 2, -pt, 0)
    s = s.fuse(box(-l / 2 + ki, l / 2 - ki, -h / 2 + ki, h / 2 - ki, -pt - kt, -pt))
    k0, k1, ky = E10["konnektor"]
    s = s.fuse(box(l / 2 - k0, l / 2 - k1, -ky, ky, -E10["kalinlik"], -pt - kt))
    return s.removeSplitter()


def kur(dy, zb, log=print):
    """Kafa (Bas) parcalari eksen cercevesinde. dy: ekran merkezinin eksene gore yuksekligi; zb: arka dis yuz z'si."""
    yb, yu = dy + KAFA_GOVDE_Y[0], dy + KAFA_GOVDE_Y[1]
    P, BAG = [], []

    def add(ad, shape, tur, malzeme, kod=None, renk="gri", not_="", kutle=None, doluluk=None, baski=None):
        P.append(dict(ad=ad, grup="Kafa", shape=shape, tur=tur, malzeme=malzeme, kod=kod or ad, renk=renk, not_=not_,
                      kutle_sabit=kutle, doluluk=doluluk, baski=baski, patlat=[0, 0, 0]))
        return len(P) - 1

    # ------------------------------------------------------------------ kabuk zarfi ve acikliklar
    O = _kutu(0.0, yb, yu, zb)
    I = _kutu(KT, yb, yu, zb)
    M = _kutu(KT / 2, yb, yu, zb)
    S = O.cut(I)
    yar = yuv_dikdortgen_y(-YARIK["x"], YARIK["x"], zb - 20.0, YARIK["z_on"], YARIK["r"], yb - 5, yb + KT + 4)
    yar = yar.fuse(yuv_dikdortgen_z(-YARIK["x"], YARIK["x"], yb - 5, yb + YARIK["h"], 6.0, zb - 5, zb + KT + 2))
    S = S.cut(yar)
    cw, ch = E10["cam_pencere"]
    S = S.cut(box(-cw / 2, cw / 2, dy - ch / 2, dy + ch / 2, ZF - KT - 1, ZF + 1))           # ekran penceresi
    S = S.cut(cyl(4.5, (0, dy + CAM_Y, Z_CAM), (0, dy + CAM_Y, ZF + 1)))                       # kamera deligi O9
    # havalandirma (arka duvar): giris tabla ustunde Pi seviyesinde, cikis ustte (eski kafadaki baca mantigi)
    for (y0, n) in ((36.0, 3), (72.0, 4)):
        for (x0, x1) in ((-45.0, -10.0), (10.0, 45.0)):
            for k in range(n):
                S = S.cut(box(x0, x1, y0 + 7.0 * k, y0 + 7.0 * k + 3.0, zb - 1, zb + KT + 1))
    S = S.removeSplitter()
    S_dis, S_ic = S.cut(M), S.common(M)
    S_bos = S_ic.cut(_kutu(KT / 2 + GB_BOS, yb, yu, zb))
    # arka kabugun on kabuga giren dili (ic yuzeye bitisik 1,5 mm halka, z dikis ... dikis + 6)
    dil = I.cut(_kutu(KT + 1.5, yb, yu, zb)).common(box(-BIG, BIG, -BIG, BIG, Z_DIKIS - 0.01, Z_DIKIS + 6.0)).cut(yar)
    # ekran yuvasi kenari (cam + 0,5 bosluk + 2 cerceve), on kabugun ic yuzunden cam arkasina
    gl, gh = E10["cam"]
    kenar = box(-gl / 2 - 2.5, gl / 2 + 2.5, dy - gh / 2 - 2.5, dy + gh / 2 + 2.5, Z_CAM_ON - E10["panel_t"], ZF - KT + 0.05)
    kenar = kenar.cut(box(-gl / 2 - 0.5, gl / 2 + 0.5, dy - gh / 2 - 0.5, dy + gh / 2 + 0.5, Z_CAM_ON - 10, ZF))
    ic_ozellik = {"on": [kenar], "arka": [dil]}

    # ------------------------------------------------------------------ 4 kabuk parcasi: (on/arka) x (sag/sol), bindirme dili sagda
    def hucre(sag, on, ic):
        z0, z1 = (Z_DIKIS, BIG) if on else (-BIG, Z_DIKIS)
        if ic:
            x0, x1 = (-DIL_W, BIG) if sag else (-BIG, -DIL_W)
        else:
            x0, x1 = (0.0, BIG) if sag else (-BIG, 0.0)
        return box(x0, x1, -BIG, BIG, z0, z1)

    PARCA = {}
    for on in (True, False):
        for sag in (True, False):
            ad = "%s %s" % ("Yuz kabugu (on)" if on else "Arka kafa kabugu", "sag" if sag else "sol")
            r_dis, r_ic = hucre(sag, on, False), hucre(sag, on, True)
            d_ = S_ic.common(r_ic).cut(S_bos.common(r_ic.cut(r_dis)))
            sh = S_dis.common(r_dis).fuse(d_)
            for f in ic_ozellik["on" if on else "arka"]:
                xb = box(-DIL_W, BIG, -BIG, BIG, -BIG, BIG) if sag else box(-BIG, -DIL_W, -BIG, BIG, -BIG, BIG)
                sh = sh.fuse(f.common(xb))
            PARCA[ad] = dict(shape=sh.removeSplitter(), yukari=V(0, 0, -1) if on else V(0, 0, 1),
                             yon="on yuzu tablada" if on else "arka yuzu tablada")
    EKLE = {k: [] for k in PARCA}
    CIKAR = {k: [] for k in PARCA}

    def sahip(pt):
        pt = V(*pt)
        for ad_, d_ in PARCA.items():
            if d_["shape"].BoundBox.isInside(pt) and d_["shape"].isInside(pt, 1e-6, True):
                return ad_
        return None

    VIDA = []
    BOSS_L = A.INSERT[3][1] + 0.5 + 1.0
    # --- sag/sol dikis civatalari: dis yari (sol parca) dudagindan, dil (sag parca) uzerindeki boss'a M3x6 ISO 7380 + isil gomme
    zm_on, zm_ar = 0.5 * (Z_DIKIS + 6.0 + ZF), 0.5 * (zb + Z_DIKIS)
    for etk, p, n in (("on ust", V(-DIL_W / 2, yu - KT / 2, zm_on), V(0, 1, 0)),
                      ("on alt (cerceve)", V(-DIL_W / 2, dy - 90.0, ZF - KT / 2), V(0, 0, 1)),
                      ("arka ust", V(-DIL_W / 2, yu - KT / 2, zm_ar), V(0, 1, 0)),
                      ("arka duvar ust", V(-DIL_W / 2, 60.0, zb + KT / 2), V(0, 0, -1)),
                      ("arka duvar alt", V(-DIL_W / 2, -50.0, zb + KT / 2), V(0, 0, -1))):
        hn = KT / 2
        ic, dis = sahip(p - n * (hn * 0.5)), sahip(p + n * (hn * 0.5))
        if ic is None or dis is None or ic == dis:
            log("UYARI dikis civatasi yerlesmedi:", etk, ic, dis)
            continue
        havsa_ = etk in ("on ust", "arka ust")
        p_ins = p - n * (HAVSA - hn + 0.05) if havsa_ else p          # havsali civatada somun basin altindan baslar
        EKLE[ic].append(damla(p, n * -1, 4.0, BOSS_L, PARCA[ic]["yukari"] * -1))
        CIKAR[ic].append(insert_hole(3, p_ins, n * -1, extra=0.5))
        CIKAR[dis].append(cyl(CLEAR[3] / 2, p - n * 1.0, p + n * (hn + 1.0)))
        havsa = etk in ("on ust", "arka ust")    # kafa tepesi: civata basi gomulu (boy BOY'u gecmesin), O6,2 x 1,7 havsa + M3x5
        if havsa:
            hv = cyl(3.1, p + n * (hn - HAVSA), p + n * (hn + 1.0))
            CIKAR[dis].append(hv)
            CIKAR[ic].append(hv)
        VIDA.append(dict(etiket="kafa sag/sol " + etk, p=p, n=n, hn=hn, ic=ic, dis=dis, havsa=havsa, p_ins=p_ins))
    # --- on/arka dikis: on kabuk yan duvarindan arka kabugun diline (dilde boss), 4x M3x6 ISO 7380 + isil gomme
    for sx in (1, -1):
        for yy in (-60.0, 70.0):
            pw = V(sx * (KX - KT), yy, Z_DIKIS + 3.0)                  # on kabuk ic yuzu = dil dis yuzu
            ic = "Arka kafa kabugu %s" % ("sag" if sx > 0 else "sol")
            dis = "Yuz kabugu (on) %s" % ("sag" if sx > 0 else "sol")
            EKLE[ic].append(damla(pw - V(sx * 1.5, 0, 0), V(-sx, 0, 0), 4.0, 5.0, V(0, 0, -1)))
            CIKAR[ic].append(insert_hole(3, pw, V(-sx, 0, 0), extra=0.5))
            CIKAR[dis].append(cyl(CLEAR[3] / 2, pw - V(sx * 1.0, 0, 0), pw + V(sx * (KT + 1.0), 0, 0)))
            VIDA.append(dict(etiket="kafa on/arka %s y%+.0f" % ("sag" if sx > 0 else "sol", yy), p=pw, n=V(sx, 0, 0), hn=KT,
                             ic=ic, dis=dis))
    # --- arka kabuk tabla raflari (2 / taraf), ustten isil gomme somun
    RAF_Z = (-15.0, zb + 15.0)
    for sx in (1, -1):
        ad = "Arka kafa kabugu %s" % ("sag" if sx > 0 else "sol")
        for zc in RAF_Z:
            x0, x1 = sorted((sx * LEDGE["x0"], sx * (KX - KT + 0.5)))
            EKLE[ad].append(box(x0, x1, LEDGE["y"][0], LEDGE["y"][1], zc - LEDGE["w"] / 2, zc + LEDGE["w"] / 2))
            # 45 derece alt destek (arka yuz tablada basilir: rafin alt yuzu havada kalmasin), arka duvarda kesilir
            xw_, xr_ = sx * (KX - KT + 0.5), sx * LEDGE["x0"]
            za = zc - LEDGE["w"] / 2
            kama = Part.Face(Part.makePolygon([V(xr_, LEDGE["y"][0], za), V(xw_, LEDGE["y"][0], za),
                                               V(xw_, LEDGE["y"][0], za - abs(xw_ - xr_)), V(xr_, LEDGE["y"][0], za)]))
            kama = kama.extrude(V(0, LEDGE["y"][1] - LEDGE["y"][0], 0)).common(box(-BIG, BIG, -BIG, BIG, zb + KT - 0.5, BIG))
            EKLE[ad].append(kama)
            CIKAR[ad].append(insert_hole(3, (sx * LEDGE["civata_x"], LEDGE["y"][1], zc), (0, -1, 0), extra=0.5))
    # --- ekran tutucu boss'lari (on kabuk ic yuzunden z 34'e, arkadan isil gomme) ve kamera boss'lari
    TIRNAK = []
    for xs in TIRNAK_X:
        for sy in (1, -1):
            yb_ = dy + sy * (gh / 2 + 7.5)
            ad = sahip(V(xs, yb_, ZF - KT * 0.75))              # ic yari: boss ic yuze (dil kuralina gore) baglanir
            EKLE[ad].append(cyl(4.5, (xs, yb_, 34.0), (xs, yb_, ZF - KT + 0.05)))
            CIKAR[ad].append(insert_hole(3, (xs, yb_, 34.0), (0, 0, 1), extra=0.5))
            TIRNAK.append((xs, yb_, sy, ad))
    CAM_DEL = [(x, dy + CAM_Y + y) for (x, y) in kamera_delikler()]
    for (x, y) in CAM_DEL:
        ad = sahip(V(x, y, ZF - KT * 0.75))
        EKLE[ad].append(cyl(2.5, (x, y, Z_CAM), (x, y, ZF - KT + 0.05)))
        CIKAR[ad].append(cyl(1.0, (x, y, Z_CAM - 0.1), (x, y, Z_CAM + 7.5)))

    for ad, d_ in PARCA.items():
        sh = d_["shape"]
        if EKLE[ad]:
            sh = sh.fuse(EKLE[ad])
        for t_ in CIKAR[ad]:
            sh = sh.cut(t_)
        sh = sh.removeSplitter()
        if len(sh.Solids) > 1:
            ana = max(sh.Solids, key=lambda s_: s_.Volume)
            log("  %s: %d kati, kucukler atildi %s" % (ad, len(sh.Solids), [round(s_.Volume, 1) for s_ in sh.Solids if s_ is not ana]))
            sh = ana
        d_["shape"] = sh
        d_["i"] = add(ad, sh, "Baski", "PETG", kod="PETG baski, 2,5 mm duvar", renk="kabuk", doluluk=A.KABUK_DOLULUK,
                      baski=dict(yukari=tuple(d_["yukari"]), yon=d_["yon"]),
                      not_="10,1 in kafa; x = 0 dikisinde bindirme dili (sag parcada), dikis civatalari M3x6 ISO 7380")

    # ------------------------------------------------------------------ kafa iskeleti: tabla + yanaklar (eski kafanin yanak olculeri)
    zt0 = zb + KT + 0.5
    ki = yuv_dikdortgen_y(-TABLA_X, TABLA_X, zt0, 28.0, 8.0, Y_TABLA[0], Y_TABLA[1])
    for (x0, x1) in (X_SAG, X_SOL):
        ki = ki.fuse(box(x0, x1, 0.0, Y_TABLA[0] + 0.01, -16.0, 16.0)).fuse(cyl(16.0, (x0, 0, 0), (x1, 0, 0)))
    ki = ki.cut(cyl(4.5, (X_SAG[0] - 0.1, 0, 0), (X_SAG[1] + 0.1, 0, 0)))                 # horn merkez vidasi erisimi
    for h in HORN_T:
        ki = ki.cut(cyl(CLEAR[3] / 2, (X_SAG[0] - 0.1, h.y, h.z), (X_SAG[1] + 0.1, h.y, h.z)))
    ki = ki.cut(cyl(8.0, (X_RUL[0], 0, 0), (X_SOL[1] + 0.01, 0, 0)))                     # 625ZZ yuvasi O16
    ki = ki.cut(cyl(6.5, (X_SOL[0] - 0.01, 0, 0), (X_RUL[0], 0, 0)))                     # civata basi cebi
    ki = ki.cut(yuv_dikdortgen_y(-50.0, -37.0, -25.0, -1.0, 4.0, Y_TABLA[0] - 1, Y_TABLA[1] + 1))   # kablo gecisi (catal -> tabla)
    for sx in (1, -1):                                                                     # hafifletme (arka yarida, Pi'nin yanlari)
        x0, x1 = sorted((sx * 50.0, sx * 98.0))
        ki = ki.cut(yuv_dikdortgen_y(x0, x1, zt0 + 12.0, -22.0, 6.0, Y_TABLA[0] - 1, Y_TABLA[1] + 1))
    for sx in (1, -1):
        for zc in RAF_Z:
            ki = ki.cut(cyl(CLEAR[3] / 2, (sx * LEDGE["civata_x"], Y_TABLA[0] - 1, zc), (sx * LEDGE["civata_x"], Y_TABLA[1] + 1, zc)))
    PI_T = (-42.5, Y_TABLA[1] + KP.PI_BURC, zt0 + 3.0 + PI5["w"])          # Pi kablo kenari one, kart arka kabuga 3 mm
    PI_DEL = pi5_delikler_kafa(PI_T)
    for (x, z) in PI_DEL:
        ki = ki.cut(cyl(1.45, (x, Y_TABLA[0] - 1, z), (x, Y_TABLA[1] + 1, z)))
    ki = ki.removeSplitter()
    I_ISK = add("Kafa iskeleti (10 in)", ki, "Baski", "PETG", renk="petg2", doluluk=DOLULUK,
                baski=dict(yukari=(0, -1, 0), yon="ters: tabla tablada, yanaklar yukari"),
                not_="tabla 224 genis + iki yanak (eski kafa yanak olculeri): sag yanak tilt horn'una 4x M3, sol yanakta 625ZZ; "
                     "arka kabuk raflarina 4x M3x10; Pi 5 icin 4x O2,9")
    for sx in (1, -1):
        ad = "Arka kafa kabugu %s" % ("sag" if sx > 0 else "sol")
        for zc in RAF_Z:
            i_c = add("Tabla civatasi M3x10 (%s z%+.0f)" % ("sag" if sx > 0 else "sol", zc),
                      screw912(3, 10, (sx * LEDGE["civata_x"], Y_TABLA[1], zc), (0, -1, 0)), "Baglanti", "Celik 8.8", kod="M3x10 DIN 912",
                      renk="celik")
            i_i = add("Isil gomme somun M3 (tabla rafi %s z%+.0f)" % ("sag" if sx > 0 else "sol", zc),
                      insert(3, (sx * LEDGE["civata_x"], LEDGE["y"][1], zc), (0, -1, 0)), "Baglanti", "Pirinc",
                      kod="M3 isil gomme somun", renk="pirinc")
            BAG.append(dict(ad="Kafa tablasi -> arka kabuk rafi", tip="M3x10 DIN 912 + M3 isil gomme somun (rafta)", adet=1,
                            nokta=(sx * LEDGE["civata_x"], Y_TABLA[1], zc), parcalar=("Kafa iskeleti (10 in)", ad)))
    for v in VIDA:
        on_ = v["etiket"].startswith("kafa on/arka")
        i_i = add("Isil gomme somun M3 (%s)" % v["etiket"], insert(3, v.get("p_ins", v["p"]), v["n"] * -1), "Baglanti", "Pirinc",
                  kod="M3 isil gomme somun", renk="pirinc")
        if v.get("havsa"):
            i_c = add("Kabuk civatasi M3x5 ISO 7380 havsada (%s)" % v["etiket"],
                      screw7380(3, 5.0, v["p"] + v["n"] * (v["hn"] - HAVSA + 0.02), v["n"] * -1), "Baglanti", "Celik 10.9",
                      kod="M3x5 ISO 7380", renk="celik")
        else:
            i_c = add("Kabuk civatasi M3x6 ISO 7380 (%s)" % v["etiket"],
                      screw7380(3, 6.0, v["p"] + v["n"] * (v["hn"] + 0.05), v["n"] * -1), "Baglanti", "Celik 10.9", kod="M3x6 ISO 7380",
                      renk="celik")
        BAG.append(dict(ad=("Yuz kabugu -> arka kabuk dili" if on_ else "Kafa kabugu sag/sol dikisi"), tip="M3x6 ISO 7380 + M3 isil gomme somun (dil boss'unda)",
                        adet=1, nokta=tuple(v["p"]), parcalar=(v["dis"], v["ic"])))

    # ------------------------------------------------------------------ ekran + tutucu tirnaklar
    lcd = lcd10_local()
    lcd.translate(V(0, dy, Z_CAM_ON))
    I_LCD = add("Yuz ekrani 10,1 in HDMI 1280x800 (tahmini model)", lcd, "Satin", "-", kod=E10["model"], renk="siyah",
                kutle=E10["kutle_g"], not_="cam on yuzu kenar cercevesine dayali, 4 tirnakla arkadan bastirilir; " + E10["kaynak"])
    for (xs, yb_, sy, ad) in TIRNAK:
        ycam = dy + sy * gh / 2
        y0, y1 = sorted((ycam - sy * 5.0, yb_ + sy * 5.0))
        t_ = box(xs - 8.0, xs + 8.0, y0, y1, 31.0, 34.0)
        ty0, ty1 = sorted((ycam - sy * 5.0, ycam))
        t_ = t_.fuse(box(xs - 8.0, xs + 8.0, ty0, ty1, 34.0 - 0.01, Z_CAM_ON - E10["panel_t"]))
        t_ = t_.cut(cyl(CLEAR[3] / 2, (xs, yb_, 30.0), (xs, yb_, 35.0)))
        etk = "%s %s" % ("ust" if sy > 0 else "alt", "sag" if xs > 0 else "sol")
        i_t = add("Ekran tutucu tirnak (%s)" % etk, t_.removeSplitter(), "Baski", "PETG", renk="petg", doluluk=DOLULUK,
                  baski=dict(yukari=(0, 0, 1), yon="plaka tablada, dil yukari"),
                  not_="cam/panel kenarina arkadan basar (kenar bandi 5 mm; arka kart 6 mm iceride)")
        add("Tirnak civatasi M3x8 ISO 7380 (%s)" % etk, screw7380(3, 8.0, (xs, yb_, 31.0), (0, 0, 1)), "Baglanti", "Celik 10.9",
            kod="M3x8 ISO 7380", renk="celik")
        add("Isil gomme somun M3 (tirnak boss %s)" % etk, insert(3, (xs, yb_, 34.0), (0, 0, 1)), "Baglanti", "Pirinc",
            kod="M3 isil gomme somun", renk="pirinc")
        BAG.append(dict(ad="Ekran tutucu tirnak -> yuz kabugu boss'u", tip="M3x8 ISO 7380 + M3 isil gomme somun", adet=1,
                        nokta=(xs, yb_, 31.0), parcalar=("Ekran tutucu tirnak (%s)" % etk, ad)))

    # ------------------------------------------------------------------ kamera
    cam = kamera_local()
    cam.translate(V(0, dy + CAM_Y, Z_CAM))
    add("Kamera Raspberry Pi Camera Module 3", cam, "Satin", "-", kod="Raspberry Pi Camera Module 3", renk="pcb", kutle=CAM["kutle_g"])
    for k, (x, y) in enumerate(CAM_DEL):
        add("Kamera vidasi M2x8 PT (%d)" % k, screw_m2(8.0, (x, y, Z_CAM - CAM["t"]), (0, 0, 1)), "Baglanti", "Celik",
            kod="M2x8 PT vida (plastik icin)", renk="celik")
    BAG.append(dict(ad="Kamera -> yuz kabugu boss'lari", tip="4x M2x8 PT vida", adet=4, nokta=(0, dy + CAM_Y, Z_CAM),
                    parcalar=("Kamera Raspberry Pi Camera Module 3", "Yuz kabugu (on)")))

    # ------------------------------------------------------------------ Pi 5 + cevirici + amfi (tablada; karsi agirlik)
    add("Raspberry Pi 5 4GB + Active Cooler", pi5_kafa(PI_T), "Satin", "-", kod="Raspberry Pi 5 4GB + resmi Active Cooler", renk="pcb",
        kutle=PI5["kutle_g"], not_="tabla ustunde, arka kabuga 3 mm; kablo kenari one (micro HDMI -> ekran, CSI -> kamera)")
    for j, (x, z) in enumerate(PI_DEL):
        add("Burc M2,5x8 (Pi %d)" % j, burc25(KP.PI_BURC, (x, Y_TABLA[1], z), (0, 1, 0)), "Satin", "Pirinc", kod="M2,5 x 8 burc, disi-disi",
            renk="pirinc")
        add("Vida M2,5x5 (Pi %d ust)" % j, screw912_25(5.0, (x, PI_T[1] + PI5["t"], z), (0, -1, 0)), "Baglanti", "Celik 8.8",
            kod="M2,5x5 DIN 912", renk="celik")
        add("Vida M2,5x8 (Pi %d alt)" % j, screw912_25(8.0, (x, Y_TABLA[0], z), (0, 1, 0)), "Baglanti", "Celik 8.8",
            kod="M2,5x8 DIN 912", renk="celik")
    BAG.append(dict(ad="Pi 5 -> burc -> kafa tablasi", tip="4x M2,5x8 pirinc burc + M2,5x5 (ust) + M2,5x8 (alt)", adet=4,
                    nokta=PI_T, parcalar=("Raspberry Pi 5 4GB + Active Cooler", "Kafa iskeleti (10 in)")))
    for ad_, (cx_, cz_), sh_, kod_, l_, w_, m_ in (
            ("5 V cevirici Pololu D36V50F5", (-80.0, 6.0), cevirici_local(), "Pololu D36V50F5 5 V 5,5 A", CEV["l"], CEV["w"], CEV["kutle_g"]),
            ("MAX98357A I2S amfi", (80.0, 6.0), amp_local(), "Adafruit MAX98357A", AMP["l"], AMP["w"], AMP["kutle_g"])):
        add("Kopuk bant (%s)" % ad_.split()[0], box(cx_ - l_ / 2, cx_ + l_ / 2, Y_TABLA[1], Y_TABLA[1] + 1.0, cz_ - w_ / 2, cz_ + w_ / 2),
            "Satin", "Kopuk", kod="Cift tarafli kopuk bant 1 mm (VHB)", renk="siyah")
        sh_ = sh_.copy()
        sh_.translate(V(cx_, Y_TABLA[1] + 1.0, cz_))
        add(ad_, sh_, "Satin", "-", kod=kod_, renk="pcb", kutle=m_, not_="tablada kopuk bant + kablo bagi")
        BAG.append(dict(ad=ad_ + " -> kafa tablasi", tip="cift tarafli kopuk bant 1 mm + kablo bagi", adet=1, nokta=(cx_, Y_TABLA[1], cz_),
                        parcalar=(ad_, "Kafa iskeleti (10 in)")))

    # ------------------------------------------------------------------ eski kafadan aynen: tilt horn, horn vidasi, 625ZZ dis bilezigi, yanak civatalari
    for p in KP.P:
        if p["grup"] == "Kafa" and p["ad"] in TEKRAR:
            sh = p["shape"].copy()
            sh.translate(OFS0)
            i_ = add(p["ad"], sh, p["tur"], p["malzeme"], kod=p["kod"], renk=p["renk"], kutle=p["kutle"], not_="eski kafadan aynen")
    BAG.append(dict(ad="Kafa iskeleti sag yanak -> tilt horn", tip="4x M3x8 DIN 912 (eski kafadaki gibi)", adet=4, nokta=(X_SAG[1], 0, 0),
                    parcalar=("Kafa iskeleti (10 in)", "Tilt horn 25T aluminyum disk")))
    BAG.append(dict(ad="Tilt pimi: 625ZZ dis bilezigi sol yanakta", tip="625ZZ (eski kafadaki gibi; M5x12 pim catalda)", adet=1,
                    nokta=(X_RUL[0], 0, 0), parcalar=("Kafa iskeleti (10 in)", "Egme catali")))

    # ------------------------------------------------------------------ kutle ve merkez
    for p in P:
        sh = p["shape"]
        sol = sh.Solids
        vt = sum(s_.Volume for s_ in sol)
        cc = V(0, 0, 0)
        for s_ in sol:
            cc = cc + s_.CenterOfMass * (s_.Volume / vt)
        p["merkez"] = cc
        p["hacim"] = vt
        if p["kutle_sabit"] is not None:
            p["kutle"] = p["kutle_sabit"]
        else:
            d_ = p["doluluk"] if p["doluluk"] else (DOLULUK if p["malzeme"] == "PETG" else 1.0)
            p["kutle"] = vt / 1000.0 * RHO.get(p["malzeme"], 1.0) * d_
    return P, BAG, dict(dy=dy, zb=zb, yb=yb, yu=yu, raf_z=RAF_Z, pi_t=PI_T, vida=len(VIDA))


def am(P):
    m = sum(p["kutle"] for p in P)
    c = V(0, 0, 0)
    for p in P:
        c = c + p["merkez"] * (p["kutle"] / m)
    return m, c


def dengele(log=print, dy0=-10.0, zb0=-82.0, tol=0.3):
    """Sekant: cy(dy) = 0 ve cz(zb) = 0 (eksenler zayif bagli; her biri kendi degiskeniyle)."""
    gecmis = []
    dy, zb = dy0, zb0
    for it in range(7):
        P, BAG, info = kur(dy, zb, log=lambda *a: None)
        m, c = am(P)
        gecmis.append(dict(dy=round(dy, 3), zb=round(zb, 3), m=round(m, 1), am=[round(c.x, 3), round(c.y, 3), round(c.z, 3)]))
        log("  denge %d: dy %.2f zb %.2f -> m %.1f g, AM (%.2f, %.2f, %.2f)" % (it, dy, zb, m, c.x, c.y, c.z))
        if abs(c.y) < tol and abs(c.z) < tol:
            break
        if len(gecmis) == 1:
            ndy, nzb = dy - c.y / 0.85, zb - c.z / 0.30
        else:
            g0, g1 = gecmis[-2], gecmis[-1]
            sy = (g1["am"][1] - g0["am"][1]) / (g1["dy"] - g0["dy"]) if abs(g1["dy"] - g0["dy"]) > 1e-6 else 0.85
            sz = (g1["am"][2] - g0["am"][2]) / (g1["zb"] - g0["zb"]) if abs(g1["zb"] - g0["zb"]) > 1e-6 else 0.30
            ndy = dy - c.y / (sy if abs(sy) > 0.1 else 0.85)
            nzb = zb - c.z / (sz if abs(sz) > 0.05 else 0.30)
        dy, zb = max(-30.0, min(10.0, ndy)), max(-150.0, min(-60.0, nzb))
    return P, BAG, info, gecmis


# ====================================================================== boyun yukseltme adaptoru (Pan grubu, kafa yerelinde)
def adaptor(h, log=print):
    """Boyun mili flansi (y Y_FL[1] = 96) ile egme catali tabani arasinda h yuksekliginde. Doner: parca listesi (kafa yereli)."""
    y0, y1 = KP.Y_FL[1], KP.Y_FL[1] + h
    P = []

    def add(ad, shape, tur, malzeme, kod, renk, kutle=None, doluluk=None, baski=None, not_=""):
        P.append(dict(ad=ad, grup="Pan", shape=shape, tur=tur, malzeme=malzeme, kod=kod, renk=renk, kutle_sabit=kutle, doluluk=doluluk,
                      baski=baski, not_=not_, patlat=[0, 0, 0]))

    t_fl = 5.0
    # Y2a (29 Ekim 2026): govde tek donel profil; ust flansin alti 45 derece koni (r 21 -> R_CAP): dik baskida (alt flans tablada) ust
    # flans 9 mm yatay cikintiydi (kafa_montaj baski: z 53,5'te destek sorunu 4). Koni flans altindan R_CAP - 21 asagi iner.
    _hk = KP.R_CAP - 21.0
    _pr = [V(0, y0, 0), V(KP.R_CAP, y0, 0), V(KP.R_CAP, y0 + t_fl, 0), V(21.0, y0 + t_fl, 0), V(21.0, y1 - t_fl - _hk, 0),
           V(KP.R_CAP, y1 - t_fl, 0), V(KP.R_CAP, y1, 0), V(0, y1, 0)]
    a = Part.Face(Part.makePolygon(_pr + [_pr[0]])).revolve(V(0, 0, 0), V(0, 1, 0), 360)
    a = Part.Solid(Part.Shell(a.Faces)) if a.ShapeType != "Solid" else a
    for (x, z) in KP.FL_DEL:
        a = a.fuse(cyl(5.0, (x, y0, z), (x, y1, z)))
    a = a.cut(cyl(16.0, (0, y0 - 1, 0), (0, y1 + 1, 0)))                         # O32 kablo deligi (mil ve catal ile ayni hat)
    for (x, z) in KP.FL_DEL:
        a = a.cut(cyl(CLEAR[3] / 2, (x, y0 - 1, z), (x, y1 + 1, z)))
    a = a.removeSplitter()
    add("Boyun yukseltme adaptoru", a, "Baski", "PETG", "Boyun yukseltme adaptoru (PETG baski)", "petg2", doluluk=DOLULUK,
        baski=dict(yukari=(0, 1, 0), yon="dik: alt flans tablada"),
        not_="boyun mili flansi ile egme catali arasinda %.1f mm; 4 saplama ile birlikte sikilir; ici O32 kablo yolu" % h)
    # mil flansi isil gomme somununa 5,5; ustte catal tabani (3) + pul + DIN 985 somun (4) + 1 mm tasma (Y2a: taslakta somuna yalniz
    # 3 mm giriyordu, naylon halka gecilmiyordu -> kilitlemez)
    ya, yu_ = y0 - 5.5, y1 + 3.0 + A.WASH125[3][2] + A.NUT985[3][1] + 1.0
    L = yu_ - ya
    for k, (x, z) in enumerate(KP.FL_DEL):
        add("Saplama M3x%.0f DIN 976 (%d)" % (math.ceil(L), k), cyl(1.5, (x, ya, z), (x, yu_, z)), "Baglanti", "Celik 8.8",
            "M3 saplama DIN 976, %.0f mm (kesilir)" % math.ceil(L), "celik",
            not_="alt ucu mil flansindaki mevcut M3 isil gomme somuna 5,5 mm, ust ucu catal tabani ustunde pul + somun")
        add("Pul M3 (saplama %d)" % k, washer(3, (x, y1 + 3.0, z), (0, 1, 0)), "Baglanti", "Celik", "M3 DIN 125 pul", "celik")
        add("Somun M3 DIN 985 (saplama %d)" % k, nut(3, (x, y1 + 3.0 + A.WASH125[3][2], z), (0, 1, 0), "985"), "Baglanti", "Celik",
            "M3 DIN 985 kontra somun", "celik")
    for p in P:
        sh = p["shape"]
        p["merkez"] = sh.Solids[0].CenterOfMass if len(sh.Solids) == 1 else sh.BoundBox.Center
        p["hacim"] = sh.Volume
        d_ = p["doluluk"] if p["doluluk"] else 1.0
        p["kutle"] = p["kutle_sabit"] if p["kutle_sabit"] is not None else sh.Volume / 1000.0 * RHO.get(p["malzeme"], 1.0) * d_
    return P
