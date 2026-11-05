# -*- coding: utf-8 -*-
# Lale 1,58 m - kafa yerlesim secenekleri OLCUM (freecadcmd). Mevcut hicbir dosyaya yazmaz; yalniz sonuc.json (bu klasor).
# FC_SCRIPT=<bu dosya> FC_MONTAJ=<robot-montaj.FCStd KOPYASI> freecadcmd run_fc.py
import os, sys, json, math, time, traceback
sys.dont_write_bytecode = True
import FreeCAD as App
import Part
t0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import yerlesim_lib as Y
from yerlesim_lib import V, box, cyl, bas2g, tasi, YT, ZT, Y0, DY, ZB, YU, X_IC, Y_IC_UST, Z_ARKA_IC, URUN
import arayuz as A
import kablo_yolu_ekran as KY


def log(*a):
    print(" ".join(str(x) for x in a), "[%.0fs]" % (time.time() - t0), flush=True)


import kafa_parcalar as KP
import kafa_lib as KL
P = KP.P
log("kafa_parcalar", len(P))
Ptilt, grup_yer = KP.Ptilt, KP.grup_yer
TAR = A.KAFA["tilt_aralik"]


def tasi_pl(sh, pl):
    s = sh.copy()
    s.transformShape(pl.toMatrix(), True)
    return s


def hedef(ad, sh):
    return dict(ad=ad, sh=sh, bb=sh.BoundBox)


KAFA_P = [p for p in P if p["grup"] == "Kafa"]
PAN_P = [p for p in P if p["grup"] == "Pan"]
GOV_P = [p for p in P if p["grup"] == "Govde"]
ZARF = [hedef(z["ad"], z["shape"]) for z in KP.ZARF]


def bbgap(a, b):
    dx = max(a.XMin - b.XMax, b.XMin - a.XMax, 0.0)
    dy = max(a.YMin - b.YMax, b.YMin - a.YMax, 0.0)
    dz = max(a.ZMin - b.ZMax, b.ZMin - a.ZMax, 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def en_yakin(sh, hedefler, k=4, atla=()):
    """Gercek geometri. BoundBox alt siniriyla erken cikis; distToShape."""
    bb = sh.BoundBox
    aday = sorted(((bbgap(bb, h["bb"]), i) for i, h in enumerate(hedefler) if h["ad"] not in atla))
    r = []
    for g, i in aday:
        if len(r) >= k and g > r[k - 1][1]:
            break
        h = hedefler[i]
        d = sh.distToShape(h["sh"])[0]
        r.append((h["ad"], round(d, 3)))
        r.sort(key=lambda q: q[1])
    return r[:k]


def cakisma(sh, hedefler, atla=(), esik=0.5):
    bb = sh.BoundBox
    out = []
    for h in hedefler:
        if h["ad"] in atla or not bb.intersect(h["bb"]):
            continue
        try:
            v = sh.common(h["sh"]).Volume
        except Exception:
            v = -1.0
        if v > esik or v < 0:
            out.append((h["ad"], round(v, 2)))
    return sorted(out, key=lambda q: -q[1])


def kabuk_mu(ad):
    return ad.startswith(("Yuz kabugu", "Arka kafa kabugu"))


# --------------------------------------------------------------------------------- 1) tork: kafa_montaj bolum 6 ile ayni formul; taban degerleri dogrulama
G = 9.81
ALFA = 4 * math.radians(60) / 0.4 ** 2
STALL = 9.4
THS = [TAR[0] + 5 * k for k in range(int((TAR[1] - TAR[0]) // 5) + 1)]


def _I(sh, kutle, pl, n, u):
    sh2 = tasi_pl(sh, pl)
    sols = sh2.Solids
    if not sols or kutle <= 0:
        return 0.0
    vt = sum(s.Volume for s in sols)
    rho = kutle / max(vt, 1e-9)
    I_ = 0.0
    for s in sols:
        Mi = s.MatrixOfInertia
        Iuu = (Mi.A11 * u.x * u.x + Mi.A22 * u.y * u.y + Mi.A33 * u.z * u.z + 2 * Mi.A12 * u.x * u.y + 2 * Mi.A13 * u.x * u.z + 2 * Mi.A23 * u.y * u.z)
        c = s.CenterOfMass - n
        I_ += rho * (Iuu + s.Volume * (c - u * c.dot(u)).Length ** 2)
    return I_


def tork(ek=(), kaldir=(), kablo_ek=()):
    """ek: [(shape_ky, kutle_g)] Kafa grubuna; kaldir: parca adlari; kablo_ek: [(nokta_ky, kutle)]."""
    K = A.KAFA
    kafa = [(p["shape"], p["kutle"], p["merkez"]) for p in KAFA_P if p["ad"] not in kaldir]
    for sh, m in ek:
        if m > 0:
            sols = sh.Solids
            vt = sum(s.Volume for s in sols)
            c = V(0, 0, 0)
            for s in sols:
                c = c + s.CenterOfMass * (s.Volume / vt)
            kafa.append((sh, m, c))
    mk0 = sum(q[1] for q in kafa)
    ck0 = V(0, 0, 0)
    for q in kafa:
        ck0 = ck0 + q[2] * (q[1] / mk0)
    _mke = K["kablo_payi"]["merkez_eksen"]
    pay = (V(_mke[0], YT + _mke[1], ZT + _mke[2]), K["kablo_payi"]["kutle_g"])
    nokta = [pay] + [(V(*q[0]), q[1]) for q in kablo_ek]
    mK, cK = mk0, ck0 * mk0
    for c_, m_ in nokta:
        cK = cK + c_ * m_
        mK += m_
    cK = cK * (1.0 / mK)
    n_t, u_t = V(0, YT, ZT), V(*K["tilt_yon"])
    I_t = 0.0
    for sh, m, c in kafa:
        I_t += _I(sh, m, App.Placement(), n_t, u_t)
    for c_, m_ in nokta:
        r = c_ - n_t
        I_t += m_ * (r - u_t * r.dot(u_t)).Length ** 2
    I_t *= 1e-9
    egri = {}
    for th in THS:
        c = Ptilt(th).multVec(cK)
        egri[th] = mK * (c.z - ZT) / 1e4
    tg = max(abs(v) for v in egri.values())
    eg15 = {th: round(mK * (Ptilt(th).multVec(cK).z - ZT) / 1e4, 3) for th in (-15, 15)}
    ti = I_t * ALFA / 9.81 * 100
    tilt_t = tg + ti
    # tilt +-15 icin ayni formul
    tilt_t15 = max(abs(v) for v in eg15.values()) + ti
    # pan (kafa_montaj: kablo payi atalete girmez; yeni kablolar girer)
    u_p, n_p = V(*K["pan_yon"]), V(0, 0, 0)
    I_pan = {}
    pan_parca = [(p["shape"], p["kutle"]) for p in PAN_P]
    I_pan0 = sum(_I(s, m, App.Placement(), n_p, u_p) for s, m in pan_parca)
    for th in (TAR[0], 0, TAR[1]):
        pl = Ptilt(th)
        I_ = I_pan0
        for sh, m, c in kafa:
            I_ += _I(sh, m, pl, n_p, u_p)
        for c_, m_ in kablo_ek:
            q = pl.multVec(V(*c_))
            I_ += m_ * (q - u_p * q.dot(u_p)).Length ** 2
        I_pan[th] = I_ * 1e-9
    Ipm = max(I_pan.values())
    mPan = sum(m for _, m in pan_parca)
    cPan = V(0, 0, 0)
    for p in PAN_P:
        cPan = cPan + p["merkez"] * (p["kutle"] / mPan)
    mPK = mPan + mK
    cPK = (cPan * mPan + cK * mK) * (1.0 / mPK)
    F_ax = mPK / 1000 * G
    M_dev = mPK / 1000 * G * math.hypot(cPK.x, cPK.z) / 1000
    ARA = (KP.Y_R2[0] + KP.Y_R2[1]) / 2 - (KP.Y_R1[0] + KP.Y_R1[1]) / 2
    F_rad = M_dev / (ARA / 1000)
    T_rul = 0.0015 * (F_ax + 2 * F_rad) * 0.023
    T_kablo = 0.03
    pan_t = (Ipm * ALFA + T_rul + T_kablo) / 9.81 * 100
    return dict(kutle_g=round(mK, 1), am_eksen=[round(cK.x, 2), round(cK.y - YT, 2), round(cK.z - ZT, 2)], statik_kgcm=round(tg, 3), statik_kgcm_tilt15=eg15,
                I_tilt=round(I_t, 6), tilt_toplam_kgcm=round(tilt_t, 3), tilt_pay=round(STALL / tilt_t, 2), tilt15_toplam_kgcm=round(tilt_t15, 3), tilt15_pay=round(STALL / tilt_t15, 2),
                I_pan=round(Ipm, 6), pan_kgcm=round(pan_t, 3), pan_pay=round(STALL / pan_t, 2))


# --------------------------------------------------------------------------------- govde: montaj kopyasindan (salt okunur kopya)
doc = App.openDocument(os.environ["FC_MONTAJ"])
GOVDE_G = []
for o in doc.Objects:
    if o.TypeId == "Part::Feature" and hasattr(o, "Tur") and getattr(o, "Tur", "") != "Referans":
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        s = s.copy()
        GOVDE_G.append(dict(ad=o.Label, sh=s, bb=s.BoundBox))
App.closeDocument(doc.Name)
log("montaj parca", len(GOVDE_G))
KAFA_ADLARI = {p["ad"] for p in KAFA_P}
PAN_ADLARI = {p["ad"] for p in PAN_P}
HER_G = GOVDE_G


def kok(ad):
    return ad.rstrip("0123456789").strip()


GOVDE_SABIT = [h for h in GOVDE_G if h["bb"].YMax < 1560 and kok(h["ad"]) not in KAFA_ADLARI]
_l = [h for h in GOVDE_G if h["ad"] == "Ust arka servis kapagi"][0]
_c = _l["sh"].common(Part.makeLine(V(47.5, 1125, -120), V(47.5, 1125, 0)))
LID_Z = max(v.Z for v in _c.Vertexes)
log("kapak ic z", LID_Z, [round(v.Z, 2) for v in _c.Vertexes])
_kp = [h for h in GOVDE_G if h["ad"] == "Arka servis kapagi"]
ARKA_KAPAK_BB = _kp[0]["bb"] if _kp else None

H_KAFA = [hedef(p["ad"], p["shape"]) for p in KAFA_P]
H_PAN = [hedef(p["ad"], p["shape"]) for p in PAN_P]
H_GOV = [hedef(p["ad"], p["shape"]) for p in GOV_P]
_H_UST = [h for h in GOVDE_G if 1200 < h["bb"].YMax < 1420 and kok(h["ad"]) not in KAFA_ADLARI and kok(h["ad"]) not in PAN_ADLARI and abs(h["bb"].Center.x) < 260 and not h["ad"].startswith(("Kol", "Ust kol", "On kol", "El "))]
H_UST = [hedef(h["ad"], tasi(h["sh"], (0, -Y0, 0))) for h in _H_UST]
log("ust govde hedef", len(H_UST))
AIHAT = hedef("AI HAT+ zarfi (VARSAYIM, modelde yok)", tasi(Y.ai_hat_zarf(), (0, YT, ZT)))
SONUC = dict(tarih="2026-11-04", cerceve="bas = tilt ekseni orijin; ky = bas + (0, %.3f, %.1f); g = ky + (0, %.0f, 0)" % (YT, ZT, Y0), urun=URUN)
if ARKA_KAPAK_BB is not None:
    SONUC["arka_kapak_bb_g"] = [round(x, 1) for x in (ARKA_KAPAK_BB.XMin, ARKA_KAPAK_BB.XMax, ARKA_KAPAK_BB.YMin, ARKA_KAPAK_BB.YMax, ARKA_KAPAK_BB.ZMin, ARKA_KAPAK_BB.ZMax)]
SONUC["ust_kapak_ic_z"] = round(LID_Z, 2)


def yaz():
    json.dump(SONUC, open(os.path.join(HERE, "sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


# --------------------------------------------------------------------------------- dogrulama
tb = tork()
SONUC["taban_tork"] = tb
log("TABAN tork", tb)
yol0 = KY.yollar()
tb_c = {}
for ad, yol in yol0.items():
    t = Y.tup(yol, KY.KABLO[ad][0] / 2)
    tb_c[ad] = cakisma(t, HER_G)
SONUC["taban_kablo_tup"] = tb_c
log("TABAN kablo", tb_c)
yaz()


def kafa_shell(ad):
    return [p for p in KAFA_P if p["ad"] == ad][0]["shape"]


# --------------------------------------------------------------------------------- parca olcumu
def parca_olc(ad, sh_ky, atla_ek=(), poz_tam=True):
    """Tek parca: kafa ici, kabuk, zarflar, AI HAT, Pan (tilt), Govde + ust govde (pan x tilt)."""
    atla = set(atla_ek) | {ad}
    r = dict()
    icler = [h for h in H_KAFA if not kabuk_mu(h["ad"]) and h["ad"] not in atla]
    kb = [h for h in H_KAFA if kabuk_mu(h["ad"]) and h["ad"] not in atla]
    r["kafa_ici_en_yakin"] = en_yakin(sh_ky, icler, k=4)
    r["kabuk_en_yakin"] = en_yakin(sh_ky, kb, k=2)
    r["cakisma"] = cakisma(sh_ky, icler + kb)
    r["zarf_en_yakin"] = en_yakin(sh_ky, ZARF, k=3, atla=atla)
    r["zarf_cakisma"] = cakisma(sh_ky, [z for z in ZARF if z["ad"] not in atla])
    r["ai_hat_mm"] = round(sh_ky.distToShape(AIHAT["sh"])[0], 3)
    pan_min = (1e9, None, None)
    for th in (-15, -10, -5, 0, 5, 10, 15):
        s2 = tasi_pl(sh_ky, Ptilt(th))
        q = en_yakin(s2, H_PAN, k=1)[0]
        if q[1] < pan_min[0]:
            pan_min = (q[1], q[0], th)
    r["boyun_pan_min"] = dict(mm=pan_min[0], parca=pan_min[1], tilt=pan_min[2])
    gov_min = (1e9, None, None, None)
    if poz_tam:
        for psi in range(-90, 91, 30):
            for th in (-15, 0, 15):
                s2 = tasi_pl(sh_ky, grup_yer("Kafa", psi, th))
                q = en_yakin(s2, H_GOV + H_UST, k=1)[0]
                if q[1] < gov_min[0]:
                    gov_min = (q[1], q[0], psi, th)
        r["govde_min"] = dict(mm=gov_min[0], parca=gov_min[1], pan=gov_min[2], tilt=gov_min[3])
    return r


def isi_olc(sh_ky):
    """Yarik kutularina mesafe, yarik arkasi 20 mm prizma ile kesisim, fan yeri."""
    yb = [tasi(b, (0, YT, ZT)) for b in Y.yarik_kutulari()]
    d = min(sh_ky.distToShape(b)[0] for b in yb)
    pr = []
    for b in Y.yarik_kutulari():
        bb = b.BoundBox
        pr.append(box(bb.XMin, bb.XMax, bb.YMin + YT, bb.YMax + YT, Z_ARKA_IC + ZT, Z_ARKA_IC + 20.0 + ZT))
    v = sum(sh_ky.common(q).Volume for q in pr if sh_ky.BoundBox.intersect(q.BoundBox))
    fan = [z for z in ZARF if z["ad"].startswith("Fan yeri")][0]
    return dict(yarik_mm=round(d, 2), yarik_prizma_kesisim_mm3=round(v, 1), fan_yeri_mm=round(sh_ky.distToShape(fan["sh"])[0], 2), fan_yeri_kesisim_mm3=round(sh_ky.common(fan["sh"]).Volume, 2))


# mevcut model parcalari (bugunku yer)
A0 = {}
for ad in ("USB Hub 4 lu", "USB ses karti", "PAM8403 amfi"):
    sh = [p for p in KAFA_P if p["ad"] == ad][0]["shape"]
    A0[ad] = parca_olc(ad, sh, atla_ek=("Kopuk bant (%s)" % ad,), poz_tam=False)
    A0[ad]["isi"] = isi_olc(sh)
    bb = sh.BoundBox
    A0[ad]["bb_bas"] = [round(x, 2) for x in (bb.XMin, bb.XMax, bb.YMin - YT, bb.YMax - YT, bb.ZMin - ZT, bb.ZMax - ZT)]
    log("mevcut", ad, A0[ad]["kafa_ici_en_yakin"][:1], A0[ad]["kabuk_en_yakin"][:1], A0[ad]["cakisma"], A0[ad]["boyun_pan_min"])
_s0 = Y.ses_karti(-1, 44.0, -19.5)
_pam0 = [p for p in KAFA_P if p["ad"] == "PAM8403 amfi"][0]["shape"]
A0["mevcut_ses_fis_x_PAM"] = dict(
    usb_fis_pam_mm3=round(tasi(_s0["usb"], (0, YT, ZT)).common(_pam0).Volume, 1), uzatma_pam_mm3=round(tasi(_s0["uzatma"], (0, YT, ZT)).common(_pam0).Volume, 1),
    gercek_govde_pam_mm3=round(tasi(_s0["govde"], (0, YT, ZT)).common(_pam0).Volume, 1),
    not_="Modeldeki PAM yeri (y 44, z -56) ses kartinin USB fis ekseninde. Gercek boy govde z -43,5...+4,5; fis -55,5; PAM z -68...-44.")
SONUC["mevcut_yer"] = A0
yaz()
log("mevcut yer tamam")


def ky(sh):
    return tasi(sh, (0, YT, ZT))


# --------------------------------------------------------------------------------- secenekler
def secenek_olc(harf):
    S = Y.secenek(harf, lid_z=LID_Z)
    R = S["R"]
    out = dict(R=dict(ad=R["ad"], merkez_bas=[R["cx"], round(Y.Y_PCB_UST, 3), R["cz"]], not_=R["not_"]))
    kaldir = set(S["kaldir"])
    kendi_ky = [dict(ad=q["ad"], sh=ky(q["sh"]), renk=q["renk"], kutle=q["kutle"], zarf=q["zarf"]) for q in S["kafa"]]
    pr = {}
    for q in kendi_ky:
        if q["ad"].startswith("Dizi vidasi"):
            continue
        r = parca_olc(q["ad"], q["sh"], atla_ek=kaldir, poz_tam=(q["ad"] in ("ReSpeaker Mic Array v2.0", "Hoparlor 40 x 20")))

        def grup(a):
            if a.startswith(("Dizi", "ReSpeaker")):
                return "dizi"
            if a.startswith("Hoparlor"):
                return "hop"
            if a in Y.SES_ADLAR:
                return "ses"
            return a
        diger = [hedef(x["ad"], x["sh"]) for x in kendi_ky if grup(x["ad"]) != grup(q["ad"])]
        r["kendi_en_yakin"] = en_yakin(q["sh"], diger, k=2) if diger else []
        r["isi"] = isi_olc(q["sh"])
        bb = q["sh"].BoundBox
        r["bb_bas"] = [round(x, 2) for x in (bb.XMin, bb.XMax, bb.YMin - YT, bb.YMax - YT, bb.ZMin - ZT, bb.ZMax - ZT)]
        pr[q["ad"]] = r
        log(harf, q["ad"], r["kafa_ici_en_yakin"][:1], r["kabuk_en_yakin"][:1], r["cakisma"][:3], r["boyun_pan_min"], r["zarf_cakisma"][:3])
    out["kafa_parca"] = pr
    grp = {}
    for q in S["govde"]:
        sh = q["sh"]
        bb = sh.BoundBox
        b2 = App.BoundBox(bb)
        b2.enlarge(80)
        H = [h for h in GOVDE_SABIT if h["bb"].intersect(b2)]
        grp[q["ad"]] = dict(en_yakin=en_yakin(sh, H, k=5), cakisma=cakisma(sh, H), bb_g=[round(x, 2) for x in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)])
        log(harf, q["ad"], grp[q["ad"]]["en_yakin"][:2], grp[q["ad"]]["cakisma"][:4])
    out["govde_parca"] = grp
    # kablolar
    kab = {}
    sy = [h for h in HER_G if h["ad"].startswith("SY8205")][0]
    for ad, (yol, r, liste, not_) in S["kablo"].items():
        t = Y.tup(yol, r)
        H = [h for h in HER_G if h["ad"] not in kaldir]
        # gogus ekrani ucu taban yolunda da ekrana girer (167,6 mm3, lale158-kontrol.json); common burada dakikalar suruyor, dokunmatik icin atlanir
        c_hep = cakisma(t, H, atla=(("Gogus ekrani 11,6 in HDMI 1920x1080 kasali",) if ad.startswith("Gogus dokunmatik") else ()))
        c = [q for q in c_hep if not q[0].startswith("Gogus ekrani 11")]
        c_gok = [q for q in c_hep if q[0].startswith("Gogus ekrani 11")]
        L = Y.uzun(yol)
        kab[ad] = dict(yol_mm=round(L, 0), oneri_mm=round(L * 1.25, -1), liste_mm=liste, kalan_mm=(round(liste - L * 1.25, 0) if liste else None), cap=2 * r, cakisma=c,
                       gogus_ekrani_ucu_mm3=c_gok, sy8205_mm=round(t.distToShape(sy["sh"])[0], 2), not_=not_)
        log(harf, ad, kab[ad]["yol_mm"], c[:5], "SY", kab[ad]["sy8205_mm"])
    dz = S["kablo"]["Dizi USB (Pi -> micro B)"][0]
    tdz = Y.tup(dz, 2.0)
    gc = {}
    for adg in ("SY8205 kafa ekrani 5 V", "5 V cevirici Pololu D24V50F5", "TVS P6KE6V8A kafa ekrani"):
        gc[adg] = round(tdz.distToShape([h for h in HER_G if h["ad"].startswith(adg)][0]["sh"])[0], 2)
    for ad_, (yol_, r_, _l, _n) in S["kablo"].items():
        if ad_.startswith(("PAM 5 V", "Hoparlor")):
            gc[ad_] = round(tdz.distToShape(Y.tup(yol_, r_))[0], 2)
    out["dizi_usb_guc_mesafe_mm"] = gc
    out["kablo"] = kab
    # tork
    ek = [(q["sh"], q["kutle"]) for q in kendi_ky if q["kutle"] > 0 and not q["zarf"]]
    kablo_ek = []
    for q in kendi_ky:
        if q["zarf"] and q["kutle"] > 0:
            bc = q["sh"].BoundBox.Center
            kablo_ek.append(((bc.x, bc.y, bc.z), q["kutle"]))
    Y_KAFA_ALT = Y0 + YT + Y.YB
    km = []
    for ad, (yol, r, liste, not_) in S["kablo"].items():
        gm = 30.0 if ("USB" in ad or "Hub" in ad or "uzatma" in ad) else 15.0
        Lk, cc = 0.0, V(0, 0, 0)
        for a_, b_ in zip(yol[:-1], yol[1:]):
            a2, b2_ = V(*a_), V(*b_)
            if a2.y > Y_KAFA_ALT and b2_.y > Y_KAFA_ALT:
                l_ = (b2_ - a2).Length
                Lk += l_
                cc = cc + (a2 + b2_) * (0.5 * l_)
        if ad == "Hub kablosu":
            Lk = 0.0                                 # hub kutlesinin icinde
        if Lk > 0:
            c3 = cc * (1.0 / Lk)
            kablo_ek.append(((c3.x, c3.y - Y0, c3.z), Lk / 1000.0 * gm))
            km.append((ad, round(Lk, 0), round(Lk / 1000.0 * gm, 1)))
    out["kafa_ici_kablo_kutle"] = km
    tk = tork(ek=ek, kaldir=kaldir, kablo_ek=kablo_ek)
    out["tork"] = tk
    d_idx = [i for i, e_ in enumerate(ek) if abs(e_[1] - URUN["respeaker"]["kutle_g"]) < 1e-9][0]
    for m_ in (18.0, 70.0):
        ek2 = list(ek)
        ek2[d_idx] = (ek[d_idx][0], m_)
        t2 = tork(ek=ek2, kaldir=kaldir, kablo_ek=kablo_ek)
        out["tork_dizi_%dg" % int(m_)] = dict(statik=t2["statik_kgcm"], tilt=t2["tilt_toplam_kgcm"], tilt_pay=t2["tilt_pay"], pan=t2["pan_kgcm"], pan_pay=t2["pan_pay"])
    t3 = tork(ek=ek + [(AIHAT["sh"], URUN["ai_hat"]["kutle_g"])], kaldir=kaldir, kablo_ek=kablo_ek)
    out["tork_ai_hat_ekli"] = dict(statik=t3["statik_kgcm"], tilt=t3["tilt_toplam_kgcm"], tilt_pay=t3["tilt_pay"], pan=t3["pan_kgcm"], pan_pay=t3["pan_pay"], am=t3["am_eksen"])
    log(harf, "tork", tk)
    # akustik geometri
    mics = [V(m[0], m[1] + YT, m[2] + ZT) for m in S["dizi"]["mic"]]
    h = S["hop"]
    if S["hop_cerceve"] == "g":
        c_h = h["merkez_diyafram"] - V(0, Y0, 0)
        en, ev, enb = 1e9, None, -1
        for psi in range(-90, 91, 15):
            for th in (-15, -10, -5, 0, 5, 10, 15):
                pl = grup_yer("Kafa", psi, th)
                for m in mics:
                    d = (pl.multVec(m) - c_h).Length
                    if d < en:
                        en, ev = d, (psi, th)
                    enb = max(enb, d)
        ev0 = min((m - c_h).Length for m in mics)
        ak = dict(mic_hoparlor_ev_min_mm=round(ev0, 1), mic_hoparlor_poz_min_mm=round(en, 1), poz=ev, mic_hoparlor_poz_max_mm=round(enb, 1))
    else:
        c_h = h["merkez_diyafram"] + V(0, YT, ZT)
        ds = [(m - c_h).Length for m in mics]
        ak = dict(mic_hoparlor_ev_min_mm=round(min(ds), 1), mic_hoparlor_poz_min_mm=round(min(ds), 1), poz="kafa ile birlikte doner, sabit", mic_hoparlor_poz_max_mm=round(max(ds), 1))
    ak["h1_40cm"] = bool(ak["mic_hoparlor_poz_min_mm"] >= 400.0)

    def en_ad(bas):
        return [p for p in KAFA_P if p["ad"].startswith(bas)][0]["shape"]
    kay = dict()
    pts = [Part.Vertex(m) for m in mics]
    for adk, sh in (("QLED ekran", en_ad("Yuz ekrani")), ("Pi + Active Cooler", en_ad("Raspberry Pi 5")), ("SY8205", en_ad("SY8205")), ("D24V50F5", en_ad("5 V cevirici")), ("Kamera", en_ad("Kamera Raspberry"))):
        kay[adk] = round(min(v.distToShape(sh)[0] for v in pts), 1)
    fan = [z for z in ZARF if z["ad"].startswith("Fan yeri")][0]["sh"]
    kay["Fan yeri (ayrilmis)"] = round(min(v.distToShape(fan)[0] for v in pts), 1)
    _cf = V(37.75 - 42.5, 40.0 + 15.0, -27.893 - 27.75) + V(0, YT, ZT)
    kay["Active Cooler ust yuzu merkezi"] = round(min((m - _cf).Length for m in mics), 1)
    kay["Arka yarik (en yakin)"] = round(min(v.distToShape(ky(b))[0] for v in pts for b in Y.yarik_kutulari()), 1)
    srv = [p for p in PAN_P if p["ad"].startswith("Tilt servosu MG996R")][0]["shape"]
    kay["Tilt servosu (ev pozu)"] = round(min(v.distToShape(srv)[0] for v in pts), 1)
    ps = [p for p in GOV_P if "MG996R" in p["ad"]]
    kay["Pan servosu (ev pozu)"] = round(min(v.distToShape(ps[0]["shape"])[0] for v in pts), 1) if ps else None
    ak["mikrofon_yakinlik_mm"] = kay
    ak["mikrofon_bas"] = [[round(c, 2) for c in m] for m in S["dizi"]["mic"]]
    ak["dizi_merkez_pan_ekseni_mm"] = round(math.hypot(R["cx"], R["cz"] + ZT), 1)
    ak["dizi_merkez_tilt_ekseni_mm"] = round(math.hypot(Y.Y_PCB_UST, R["cz"]), 1)
    jm = S["dizi"]["mic"][0]
    ak["port_kabuk"] = dict(port_ust_duvar_ic_mm=round(Y_IC_UST - jm[1], 2), duvar_mm=Y.KT, delik_cap_mm=3.0, toplam_yol_mm=round(YU - jm[1], 2), port_cap_mm=0.7, not_="O3 delik VARSAYIM")
    ak["tepe_duz_bolge"] = dict(arka_fillet_z=round(ZB + 5.0, 2), on_fillet_z=42.0, dikis_x=0.0, dikis_z=10.0, delik_dikis_x_min=round(min(abs(m[0]) for m in S["dizi"]["mic"]) - 1.5, 2))
    out["akustik"] = ak
    log(harf, "akustik", ak["mic_hoparlor_poz_min_mm"], kay)
    # servis: on kabuk + ekran sokuldu. Ufuk z = +10 (bas)
    H_KAL = [h for h in H_KAFA if h["ad"] not in kaldir and not h["ad"].startswith(("Yuz kabugu", "Yuz ekrani", "Ekran tirnagi", "Kopuk bant (tirnak", "Tirnak civatasi", "Isil gomme somun M3 (tirnak", "Kamera", "Arka kafa kabugu"))]
    sv = {}
    for q in kendi_ky:
        if q["zarf"] or q["ad"].startswith(("Dizi boss", "Dizi vidasi", "Hoparlor boss")):
            continue
        bb = q["sh"].BoundBox
        z_on = 10.0 + ZT
        if bb.ZMax < z_on:
            pr_ = box(bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMax + 0.05, z_on)
            eng = [c_ for c_ in cakisma(pr_, H_KAL) if not c_[0].startswith(q["ad"])]
            dd = z_on - bb.ZMin
        else:
            eng, dd = [], 0.0
        sv[q["ad"]] = dict(on_ufuktan_derinlik_mm=round(dd, 1), prizma_engel=eng[:6])
    tak = []
    for (xs, ys) in Y.STP_DELIK:
        x, y, z = Y.stp_map(R["cx"], R["cz"], xs, ys, 0.0)
        y_bas = y - 1.2 - 1.6 + YT
        ax = Part.makeCylinder(4.0, 75.0, V(x, y_bas - 75.0, z + ZT), V(0, 1, 0))
        en_ = 75.0
        ad_ = None
        for h2 in H_KAL + [AIHAT]:
            if ax.BoundBox.intersect(h2["bb"]):
                cm = ax.common(h2["sh"])
                if cm.Volume > 0.5:
                    bos = y_bas - cm.BoundBox.YMax
                    if bos < en_:
                        en_, ad_ = bos, h2["ad"]
        tak.append(dict(xz=[round(x, 1), round(z, 1)], serbest_mm=round(en_, 1), engel=ad_, z_on_mm=round(10.0 - z, 1)))
    sv["dizi_vida_takim"] = tak
    out["servis"] = sv
    log(harf, "servis", sv)
    return out


SEC = {}
SONUC["secenek"] = SEC
# FC_ONCEKI + FC_HARF: yalniz degisen secenekler yeniden olculur, digerleri ayni betigin onceki kosusundan alinir
_onc = json.load(open(os.environ["FC_ONCEKI"], encoding="utf-8"))["secenek"] if os.environ.get("FC_ONCEKI") else {}
_yeni = os.environ.get("FC_HARF", "A,B,C,R2").split(",")
for harf in ("A", "B", "C", "R2"):
    if harf in _yeni:
        SEC[harf] = secenek_olc(harf)
    else:
        SEC[harf] = _onc[harf]
    yaz()
    log("tamam", harf)

# --------------------------------------------------------------------------------- hoparlor alternatif: gogus alti, yatay eksen; yalniz yer kontrolu
_yat = cyl(20.0, (Y.SP_X, 982.0, 66.0), (Y.SP_X, 982.0, 85.9))
H = [h for h in GOVDE_SABIT if bbgap(_yat.BoundBox, h["bb"]) < 60]
SONUC["hoparlor_yatay_eksen"] = dict(en_yakin=en_yakin(_yat, H, k=4), cakisma=cakisma(_yat, H), not_="eksen yatay (+Z), on duzlem z 85,9; duvar ici y 962 z 86,4 / y 1002 z 114,4; kama bosluk 0,5...28 mm")
n = V(*Y.SP_N)
c = Y.hoparlor_gogus()["merkez_diyafram"]
aci = {}
for adn, kulak in (("kulak 1,6 m, 0,5 m onde", V(0, 1600, 500 + 47)), ("kulak 1,6 m, 1,0 m onde", V(0, 1600, 1000 + 47)), ("kulak 1,6 m, 1,5 m onde", V(0, 1600, 1500 + 47))):
    u = kulak - c
    L = u.Length
    u.normalize()
    aci[adn] = dict(duvara_paralel_eksen_derece=round(math.degrees(math.acos(max(-1, min(1, u.dot(n))))), 1), yatay_eksen_derece=round(math.degrees(math.acos(u.z)), 1), mesafe_mm=round(L, 0))
SONUC["hoparlor_gogus_eksen"] = dict(duvar_normali=[round(x, 3) for x in Y.SP_N], yatayin_altinda_derece=round(math.degrees(Y.SP_ALFA), 1), dinleyici=aci)
# kafa ici kosegen: kabuk ici en uzak iki nokta alt siniri (kose yuvarlaklari sayilmadan, ust sinir)
SONUC["kafa_ic_kosegen_mm"] = round(math.sqrt(sum((x - 5.0) ** 2 for x in A.KAFA["kafa_kutu"])), 1)

# --------------------------------------------------------------------------------- boyun demeti
top0 = sum(a for _, a in KY.MEVCUT)
U = math.pi / 4 * 4.0 ** 2
Hdmi = math.pi / 4 * 6.0 ** 2
HOPK = math.pi / 4 * 4.0 ** 2
dem = {}
for ad, tp, not_ in (("C ve mevcut", top0 + Hdmi + U, "12 V, ESP32 USB, tilt, HDMI, gogus dokunmatik"), ("A", top0 + Hdmi + U + HOPK, "+ hoparlor"), ("B", top0 + Hdmi + HOPK, "- gogus dokunmatik - ESP32 USB + hub uzatmasi + hoparlor")):
    dem[ad] = dict(alan_mm2=round(tp, 1), not_=not_, gecis=[dict(ad=g["ad"], doluluk=round(tp / g["alan"], 3)) for g in KY.GECIS])
SONUC["boyun_demet"] = dem
yaz()


# --------------------------------------------------------------------------------- baski: secenek kabuk parcalari
def baski_mod(ad, sh, yukari, dol=A.KABUK_DOLULUK):
    t1 = time.time()
    r = KL.baski_analiz(ad, sh, yukari, dol)
    log("baski", ad, r["olcu"], r["destek_sorun_sayi"], r["desteksiz"], "%.0fs" % (time.time() - t1))
    return {k: r[k] for k in ("ad", "olcu", "sigar", "destek_sorun_sayi", "desteksiz", "destek_sorun", "cikinti_orani", "kutle_g", "sure_saat", "ofset_uyari")}


def baski_hepsi():
    B = dict()
    SONUC["baski"] = B
    _as = kafa_shell("Arka kafa kabugu sag")
    _ol = kafa_shell("Arka kafa kabugu sol")
    _on = [h for h in GOVDE_G if h["ad"] == "Govde orta bandi sag"][0]["sh"]
    B["taban Arka sag"] = baski_mod("Arka kafa kabugu sag", _as, (0, 0, 1))
    B["taban Arka sol"] = baski_mod("Arka kafa kabugu sol", _ol, (0, 0, 1))
    B["taban Orta bant sag"] = baski_mod("Govde orta bandi sag", _on, (0, 1, 0))
    yaz()
    d1 = Y.dizi_parcalari(Y.R1["cx"], Y.R1["cz"])
    s = _as
    for f in d1["boss"]:
        s = s.fuse(ky(f))
    for f in d1["delik"] + d1["pilot"]:
        s = s.cut(ky(f))
    s = s.removeSplitter()
    B["R1 Arka sag"] = baski_mod("Arka sag + R1", s, (0, 0, 1))
    B["R1 Arka sag"]["gecerli"] = s.isValid()
    B["R1 Arka sag"]["kati"] = len(s.Solids)
    d2 = Y.dizi_parcalari(Y.R2["cx"], Y.R2["cz"])
    sg, sl = _as, _ol
    yer = []
    for f, pf in zip(d2["boss"], d2["pilot"]):
        c_ = f.BoundBox.Center
        yer.append("sag" if c_.x > -16.0 else "sol")
        if c_.x > -16.0:
            sg = sg.fuse(ky(f)).cut(ky(pf))
        else:
            sl = sl.fuse(ky(f)).cut(ky(pf))
    for f in d2["delik"]:
        bb = f.BoundBox
        if bb.Center.x > 0:
            sg = sg.cut(ky(f))
        else:
            sl = sl.cut(ky(f))
    B["R2 Arka sag"] = baski_mod("Arka sag + R2", sg.removeSplitter(), (0, 0, 1))
    B["R2 Arka sol"] = baski_mod("Arka sol + R2", sl.removeSplitter(), (0, 0, 1))
    B["R2 boss yeri"] = yer
    yaz()
    h = Y.hoparlor_gogus()
    s = _on
    for f in h["boss"]:
        s = s.fuse(f)
    for f in h["pilot"] + h["izgara"]:
        s = s.cut(f)
    s = s.removeSplitter()
    B["Gogus alti izgara + boss, Orta bant sag"] = baski_mod("Orta bant sag + hoparlor", s, (0, 1, 0))
    B["Gogus alti izgara + boss, Orta bant sag"]["gecerli"] = s.isValid()
    B["Gogus alti izgara + boss, Orta bant sag"]["delik_sayi"] = len(h["izgara"])
    h = Y.hoparlor_kafa()
    s = _ol
    for f in h["boss"]:
        s = s.fuse(ky(f))
    for f in h["pilot"] + h["izgara"]:
        s = s.cut(ky(f))
    s = s.removeSplitter()
    B["Kafa yan izgara + boss, Arka sol"] = baski_mod("Arka sol + hoparlor", s, (0, 0, 1))
    B["Kafa yan izgara + boss, Arka sol"]["gecerli"] = s.isValid()
    _kp2 = KL.baski_analiz("Hoparlor kabi", Y.hoparlor_gogus()["kap"], Y.SP_N, 0.8)
    B["Hoparlor kabi (ayri baski)"] = {k: _kp2[k] for k in ("ad", "olcu", "sigar", "destek_sorun_sayi", "desteksiz", "kutle_g", "sure_saat")}
    # R2: tasinacak tepe civatasi yeni yeri
    _b2 = Y.damla(V(-8.0, Y_IC_UST + 0.05, -72.0), V(0, -1, 0), 4.0, 7.2, V(0, 0, -1))
    rb = Y.respeaker(Y.R2["cx"], Y.R2["cz"])
    fan_b = [z for z in KP.ZARF if z["ad"].startswith("Fan yeri")][0]["shape"]
    SONUC["R2_tasinan_civata"] = dict(yeni_boss_bas=[-8.0, round(Y_IC_UST, 3), -72.0], dizi_mm=round(_b2.distToShape(rb)[0], 2), fan_yeri_mm=round(ky(_b2).distToShape(fan_b)[0], 2),
                                       arka_duvar_ic_mm=round(-72.0 - 4.0 - Z_ARKA_IC, 2), fillet_payi_mm=round(-72.0 - (ZB + 5.0) - 4.0, 2))
    yaz()


if os.environ.get("FC_BASKI"):
    # baski sonuclari yalniz dizi ve hoparlor kabuk degisikliklerine bagli; ses karti konumundan etkilenmez. Govde bandi analizi parca basina 7,5 dk.
    _on = json.load(open(os.environ["FC_BASKI"], encoding="utf-8"))
    SONUC["baski"] = _on["baski"]
    SONUC["R2_tasinan_civata"] = _on["R2_tasinan_civata"]
    SONUC["baski_not"] = "baski bolumu ayni betigin ilk tam kosusundan alindi (dizi/hoparlor kabuk geometrisi degismedi)"
else:
    baski_hepsi()
_kk = Y.hoparlor_gogus()["kap"]
_k2 = KL.baski_analiz("Hoparlor kabi ters", _kk, tuple(V(*Y.SP_N) * -1), 0.8)
SONUC["baski"]["Hoparlor kabi (flans tablada)"] = {k: _k2[k] for k in ("ad", "olcu", "sigar", "destek_sorun_sayi", "desteksiz", "kutle_g", "sure_saat")}
yaz()
log("BITTI")
