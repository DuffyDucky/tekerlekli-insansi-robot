# -*- coding: utf-8 -*-
# Lale 1,58 m - P1.3 / K2: AI HAT+ 26T x arka duvar ust dikis boss'u. Iki secenek + bugunku durum (freecadcmd). ANA MODELE YAZMAZ:
# kafa10_lib.SECENEK yalniz bu surecte degisir; kafa-analiz.json, FCStd, STEP dokunulmaz. Yalniz hat-secenek-<s>.json yazar
# (+ istenirse HAT_FCSTD=<yol> ile gorsel icin gecici FCStd, depo disina).
#   HAT_SECENEK=0 : bugunku model + AI HAT+ (cakisma gosterimi)
#   HAT_SECENEK=a : boss'u tasi  (arka duvar ust boss'u x -8 -> -5, y 60 -> 76; yarik bantlari arasinda, dil uzerinde)
#   HAT_SECENEK=b : yigini tasi  (Pi 5 + AI HAT+ yigini 5 mm one; boss yerinde)
# FC_SCRIPT=<bu dosya> HAT_SECENEK=a freecadcmd run_fc.py
#
# AI HAT+ olculeri: uretici urun ozeti RP-008133-DS-1 (Raspberry Pi Ltd, Ekim 2024) "Physical specification": kart 65 x 56,5, delikler
# 58 x 49 (kenardan 3,5), sag altta 10 x 16 centik, sol kenarda PCIe FPC konnektoru; "Supplied with 16mm stacking header, spacers, and
# screws ... with Raspberry Pi Active Cooler in place". Kutle uretici belgesinde YOK: 30 g VARSAYIM (brief). Bilesen yuksekligi cizimde
# yok: 3,0 mm zarf VARSAYIM (onceki yerlesim_lib.ai_hat_zarf ile ayni). GPIO yigin basligi: uretici fotografinda HAT ustunde siyah
# baslik govdesi; HAT ustunde 8,5 mm (tipik 2x20 disi baslik) VARSAYIM, Pi basliginin ustunden HAT ustune kadar tek zarf (kotumser).
import os, sys, json, math, time
sys.dont_write_bytecode = True
import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
for p_ in (os.path.join(UST, "kafa"), UST, LALE):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
t0 = time.time()
SEC = os.environ.get("HAT_SECENEK", "0")
assert SEC in ("0", "a", "b"), SEC
import kafa10_lib as K10
AYAR = {"0": dict(), "a": dict(arka_ust_boss=(-5.0, 76.0)), "b": dict(pi_dz=5.0)}[SEC]
VARS = dict(K10.SECENEK)
K10.SECENEK.update(AYAR)
import kafa_parcalar as KP
from kafa_parcalar import P, K, YT, ZT, Ptilt, Ppan
import kafa_lib as KL
import arayuz as A
sys.path.insert(0, LALE)
import kablo_yolu_ekran as KY_


def log(*a):
    print(" ".join(str(x) for x in a), "[%.0fs]" % (time.time() - t0), flush=True)


log("secenek", SEC, K10.SECENEK, "parca", len(P))
VB = V(0, YT, ZT)                                   # bas (eksen) cercevesi -> kafa yereli
PI_T = tuple(float(x) for x in KP.INFO["pi_t"])     # Pi kart alt kosesi, bas cercevesi
DZ = K10.SECENEK["pi_dz"]
ZB = KP.INFO["zb"]
KT = K10.KT


def kart(x0, x1, y0, y1, z0, z1):
    """Pi kart koordinati (x uzun kenar, y derinlik 0 = kablo kenari, z yukseklik kart altindan) -> kafa yereli kutu (pi5_kafa ile ayni donusum)."""
    b = Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))
    m = App.Matrix(1, 0, 0, PI_T[0], 0, 0, 1, PI_T[1], 0, -1, 0, PI_T[2], 0, 0, 0, 1)
    b.transformShape(m)
    b.translate(VB)
    return b


def kart_cyl(x, y, r, z0, z1):
    c = Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))
    m = App.Matrix(1, 0, 0, PI_T[0], 0, 0, 1, PI_T[1], 0, -1, 0, PI_T[2], 0, 0, 0, 1)
    c.transformShape(m)
    c.translate(VB)
    return c


# ---------------------------------------------------------------- AI HAT+ takimi (kafa yereli, Kafa grubu)
Z_PI = KL.PI5["t"]                 # Pi kart ustu (kart z)
STACK = 16.0                       # uretici: 16 mm yigin basligi / ayak
Z_H0, Z_H1 = Z_PI + STACK, Z_PI + STACK + 1.6
BILESEN = 3.0                      # VARSAYIM
BASLIK = 8.5                       # VARSAYIM
DELIK = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]       # Pi delikleri = HAT delikleri (58 x 49)
centik = kart(47.5, 57.5, -1.0, 16.0, Z_H0 - 1, Z_H1 + BILESEN + 1)
hat_pcb = kart(0.0, 65.0, 0.0, 56.5, Z_H0, Z_H1).cut(centik)
hat_bil = kart(0.0, 65.0, 0.0, 56.5, Z_H1, Z_H1 + BILESEN).cut(centik)
for (x, y) in DELIK:
    hat_pcb = hat_pcb.cut(kart_cyl(x, y, 1.35, Z_H0 - 1, Z_H1 + 1))
    hat_bil = hat_bil.cut(kart_cyl(x, y, 3.25, Z_H1 - 1, Z_H1 + BILESEN + 1))
hat_bil = hat_bil.cut(kart(7.0, 58.0, 50.0, 55.5, Z_H1 - 1, Z_H1 + BILESEN + 1))         # baslik bolgesi ayri zarf
baslik = kart(7.0, 58.0, 50.0, 55.5, 11.0, Z_H1 + BASLIK).cut(hat_pcb)                     # Pi basligi ustu (kart z 11) ... HAT ustu + 8,5
ffc = kart(-5.0, 0.0, 19.0, 37.0, Z_PI, Z_H1)                                               # PCIe FFC halkasi, Pi kisa kenari disinda (VARSAYIM)
HAT_P = [("AI HAT+ kart", hat_pcb.removeSplitter(), 22.0), ("AI HAT+ bilesen zarfi", hat_bil.removeSplitter(), 0.0),
         ("AI HAT+ GPIO yigin basligi zarfi", baslik.removeSplitter(), 4.0), ("AI HAT+ PCIe FFC zarfi", ffc, 1.0)]
for k_, (x, y) in enumerate(DELIK):
    HAT_P.append(("AI HAT+ ayak M2,5 16 mm (%d)" % k_, kart_cyl(x, y, 2.5, Z_PI, Z_H0), 0.5))
    vida = kart_cyl(x, y, 2.25, Z_H1, Z_H1 + 2.5).fuse(kart_cyl(x, y, 1.25, Z_H0 + 0.0, Z_H1))   # M2,5x5 DIN 912: bas 4,5 x 2,5
    HAT_P.append(("AI HAT+ vidasi M2,5x5 (%d)" % k_, vida.removeSplitter(), 0.25))
HAT_KUTLE = sum(m for _, _, m in HAT_P)
KALDIR = [i for i, p in enumerate(P) if p["ad"].startswith("Vida M2,5x5 (Pi")]                # HAT ayaklari Pi ust vidalarinin yerine (erkek-disi ayak burca)


def parca_listesi(hat):
    L = []
    for i, p in enumerate(P):
        if hat and i in KALDIR:
            continue
        L.append(dict(ad=p["ad"], grup=p["grup"], shape=p["shape"], tur=p["tur"], kutle=p["kutle"], merkez=p["merkez"], bb=p["shape"].BoundBox,
                      renk=p.get("renk", "gri")))
    if hat:
        for ad, sh, m in HAT_P:
            L.append(dict(ad=ad, grup="Kafa", shape=sh, tur="Satin", kutle=m, merkez=sh.BoundBox.Center if not sh.Solids else _am(sh),
                          bb=sh.BoundBox, renk="hat"))
    return L


def _am(sh):
    vt = sum(s.Volume for s in sh.Solids)
    c = V(0, 0, 0)
    for s in sh.Solids:
        c = c + s.CenterOfMass * (s.Volume / vt)
    return c


def kes(a, b):
    if not a["bb"].intersect(b["bb"]):
        return 0.0
    try:
        return a["shape"].common(b["shape"]).Volume
    except Exception:
        return -1.0


# ---------------------------------------------------------------- 1) kafa ici cakisma (kafa_montaj bolum 1 ile ayni: tum cift, 0,5 mm3)
def cakisma(L):
    out, n = [], 0
    for i in range(len(L)):
        for j in range(i + 1, len(L)):
            a, b = L[i], L[j]
            if a["tur"] == "Referans" or b["tur"] == "Referans" or not a["bb"].intersect(b["bb"]):
                continue
            n += 1
            v = kes(a, b)
            if v > 0.5 or v < 0:
                out.append((a["ad"], b["ad"], round(v, 3)))
    return out, n


# ---------------------------------------------------------------- 2) tork (kafa_montaj bolum 6 aynen)
G = 9.81
STALL = 9.4
ALFA = 4 * math.radians(60) / 0.4 ** 2
TAR = K["tilt_aralik"]


def atalet(L, gruplar, pl_map, eksen_n, eksen_u):
    u = V(*eksen_u)
    u.normalize()
    n = V(*eksen_n)
    I_ = 0.0
    for p in L:
        if p["grup"] not in gruplar or p["kutle"] <= 0:
            continue
        sh = p["shape"].copy()
        sh.transformShape(pl_map[p["grup"]].toMatrix())
        rho = p["kutle"] / max(sh.Volume, 1e-9)
        for s in sh.Solids:
            Mi = s.MatrixOfInertia
            Iuu = (Mi.A11 * u.x * u.x + Mi.A22 * u.y * u.y + Mi.A33 * u.z * u.z + 2 * Mi.A12 * u.x * u.y + 2 * Mi.A13 * u.x * u.z + 2 * Mi.A23 * u.y * u.z)
            c = s.CenterOfMass - n
            r2 = (c - u * c.dot(u)).Length ** 2
            I_ += rho * (Iuu + s.Volume * r2)
    return I_ * 1e-9


def tork(L):
    GR = {}
    for g in ("Govde", "Pan", "Kafa"):
        m = sum(p["kutle"] for p in L if p["grup"] == g)
        c = V(0, 0, 0)
        for p in L:
            if p["grup"] == g:
                c = c + p["merkez"] * (p["kutle"] / m)
        GR[g] = (m, c)
    _mke = K["kablo_payi"]["merkez_eksen"]
    KK = dict(kutle_g=K["kablo_payi"]["kutle_g"], merkez=(_mke[0], YT + _mke[1], ZT + _mke[2]))
    KE = [dict(kutle_g=q[2], nokta=q[3]) for q in KY_.kafa_ici_kablo_kutle()]
    for z_ in KP.ZARF:
        if z_.get("kutle", 0.0) > 0:
            _bc = z_["shape"].BoundBox.Center
            KE.append(dict(kutle_g=z_["kutle"], nokta=(_bc.x, _bc.y, _bc.z)))
    mK0, cK0 = GR["Kafa"]
    mK = mK0 + KK["kutle_g"] + sum(q["kutle_g"] for q in KE)
    cK = (cK0 * mK0 + V(*KK["merkez"]) * KK["kutle_g"] + sum((V(*q["nokta"]) * q["kutle_g"] for q in KE), V(0, 0, 0))) * (1.0 / mK)
    I_t = atalet(L, ("Kafa",), {"Kafa": App.Placement()}, (0, YT, ZT), K["tilt_yon"])
    _kc = V(*KK["merkez"]) - V(0, YT, ZT)
    I_t += KK["kutle_g"] / 1000.0 * ((_kc.y ** 2 + _kc.z ** 2) * 1e-6)
    for q in KE:
        _kc2 = V(*q["nokta"]) - V(0, YT, ZT)
        I_t += q["kutle_g"] / 1000.0 * ((_kc2.y ** 2 + _kc2.z ** 2) * 1e-6)
    egri = []
    for th in range(int(TAR[0]), int(TAR[1]) + 1, 5):
        c = Ptilt(th).multVec(cK)
        egri.append(mK * (c.z - ZT) / 1e4)
    tg_max = max(abs(x) for x in egri)
    ti = I_t * ALFA / 9.81 * 100
    tg15 = max(abs(mK * (Ptilt(th).multVec(cK).z - ZT) / 1e4) for th in (-15, 15))
    I_pan = []
    for th in (TAR[0], 0, TAR[1]):
        Ip = atalet(L, ("Pan", "Kafa"), {"Pan": App.Placement(), "Kafa": Ptilt(th)}, (0, 0, 0), K["pan_yon"])
        _pl = Ptilt(th)
        _up = V(*K["pan_yon"])
        for q in KE:
            _qp = _pl.multVec(V(*q["nokta"]))
            Ip += q["kutle_g"] * (_qp - _up * _qp.dot(_up)).Length ** 2 * 1e-9
        I_pan.append(Ip)
    mPK = GR["Pan"][0] + mK
    cPK = (GR["Pan"][1] * GR["Pan"][0] + cK * mK) * (1.0 / mPK)
    F_ax = mPK / 1000 * G
    M_dev = mPK / 1000 * G * math.hypot(cPK.x, cPK.z) / 1000
    ARA = (KP.Y_R2[0] + KP.Y_R2[1]) / 2 - (KP.Y_R1[0] + KP.Y_R1[1]) / 2
    T_rul = 0.0015 * (F_ax + 2 * M_dev / (ARA / 1000)) * 0.023
    pan_t = (max(I_pan) * ALFA + T_rul + 0.03) / 9.81 * 100
    return dict(kafa_grubu_g=round(mK, 1), kafa_parca_g=round(mK0, 1), am=[round(cK.x, 2), round(cK.y, 2), round(cK.z, 2)],
                statik_tilt15_kgcm=round(tg15, 3), toplam_tilt15_kgcm=round(tg15 + ti, 3), pay_tilt15=round(STALL / (tg15 + ti), 2),
                statik_iki_yon_kgcm=round(tg_max, 3), pay_iki_hane=round(STALL / (tg_max + ti), 2), I_tilt=round(I_t, 6), ivme_kgcm=round(ti, 3),
                pan_toplam_kgcm=round(pan_t, 3), pan_pay_iki_hane=round(STALL / pan_t, 2))


# ---------------------------------------------------------------- 3) erisim: alet silindiri, serbest boy (ikiye bolme, 0,05 mm)
def serbest(p0, yon, r, L_max, L, atla):
    d = V(*yon)
    d.normalize()
    aday = [q for q in L if q["tur"] != "Referans" and q["ad"] not in atla]

    def carpar(Lx):
        c = Part.makeCylinder(r, Lx, p0, d)
        bb = c.BoundBox
        for q in aday:
            if bb.intersect(q["bb"]) and c.common(q["shape"]).Volume > 0.01:
                return q["ad"]
        return None
    if carpar(L_max) is None:
        return dict(serbest_mm=L_max, engel=None, not_=">= %s (tavan aranmadi)" % L_max)
    a, b = 0.05, L_max
    if carpar(a):
        return dict(serbest_mm=0.0, engel=carpar(a))
    while b - a > 0.05:
        m = (a + b) / 2
        if carpar(m):
            b = m
        else:
            a = m
    return dict(serbest_mm=round(a, 2), engel=carpar(b))


def en_yakin(sh, L, k=5, atla=()):
    out = []
    bb = sh.BoundBox
    for q in L:
        if q["tur"] == "Referans" or q["ad"].startswith(tuple(atla) or ("\0",)):
            continue
        qb = q["bb"]
        g = max(bb.XMin - qb.XMax, qb.XMin - bb.XMax, bb.YMin - qb.YMax, qb.YMin - bb.YMax, bb.ZMin - qb.ZMax, qb.ZMin - bb.ZMax, 0)
        if g > 40:
            continue
        out.append((q["ad"], round(sh.distToShape(q["shape"])[0], 2)))
    out.sort(key=lambda r: r[1])
    return out[:k]


S = dict(tarih=time.strftime("%Y-%m-%d %H:%M"), secenek=SEC, ayar=AYAR, varsayilan=VARS, kaynak="kafa_parcalar (kafa10_lib.SECENEK) + bu betikteki AI HAT+ takimi",
         hat=dict(olcu="65 x 56,5 kart, delik 58 x 49, centik 10 x 16, yigin 16 (uretici RP-008133-DS-1)", kutle_g=HAT_KUTLE,
                  varsayim="kutle 30 g, bilesen zarfi 3,0 mm, yigin basligi HAT ustunde 8,5 mm, FFC halkasi 5 x 18 mm, ayak O5",
                  pi_ust_vidalari_kaldirildi=len(KALDIR)))
L0 = parca_listesi(False)
L1 = parca_listesi(True)
S["gecersiz"] = [p["ad"] for p in L1 if not p["shape"].isValid()]
S["coklu_kati"] = [(p["ad"], len(p["shape"].Solids)) for p in L1 if len(p["shape"].Solids) != 1 and p["tur"] != "Referans"]
log("gecerlilik", S["gecersiz"], S["coklu_kati"])
# yerlesim: boss ve dikis civatasi
_boss_c = [p for p in L1 if p["ad"].startswith("Kabuk civatasi M3x6 ISO 7380 (kafa sag/sol arka duvar ust")]
S["arka_ust_civata_bb"] = [[round(x, 2) for x in (b["bb"].XMin, b["bb"].XMax, b["bb"].YMin - YT, b["bb"].YMax - YT, b["bb"].ZMin - ZT, b["bb"].ZMax - ZT)] for b in _boss_c]
S["log_uyari"] = [s_ for s_ in KP.LOG if "UYARI" in s_]
# 1) cakisma
c1, n1 = cakisma(L1)
S["cakisma_hatli"] = c1
S["cift_hatli"] = n1
log("cakisma hatli", c1)
c0, n0 = cakisma(L0)
S["cakisma_hatsiz"] = c0
log("cakisma hatsiz", c0)
# eski zarf (yerlesim_lib.ai_hat_zarf: kart + 3 mm, Pi ustunden 16) ile ayni cift olcumu (77,69 mm3 tekrar)
ah = Part.makeBox(65.0, 1.6 + 3.0, 56.5, V(-42.5, 41.6 + 16.0, -27.893 + DZ - 56.5) + VB)
S["eski_zarf_cakisma"] = sorted([(q["ad"], round(q["shape"].common(ah).Volume, 2)) for q in L0 if q["tur"] != "Referans" and q["bb"].intersect(ah.BoundBox)
                                 and not q["ad"].startswith("Raspberry") and q["shape"].common(ah).Volume > 0.5], key=lambda r: -r[1])
log("eski zarf", S["eski_zarf_cakisma"])
# zarflar (yer ayirma: fan yeri, kablo yollari, fis zarflari) x HAT
HATSH = Part.makeCompound([sh for _, sh, _ in HAT_P])
S["hat_x_zarf"] = []
for z_ in KP.ZARF:
    zs = z_["shape"]
    v = HATSH.common(zs).Volume if HATSH.BoundBox.intersect(zs.BoundBox) else 0.0
    S["hat_x_zarf"].append((z_["ad"], round(HATSH.distToShape(zs)[0], 2), round(v, 2)))
pi_sh = next(p for p in L1 if p["ad"].startswith("Raspberry"))["shape"]
S["pi_x_zarf"] = [(z_["ad"], round(pi_sh.distToShape(z_["shape"])[0], 2), round(pi_sh.common(z_["shape"]).Volume, 2)) for z_ in KP.ZARF
                  if pi_sh.BoundBox.intersect(z_["shape"].BoundBox) or pi_sh.distToShape(z_["shape"])[0] < 10]
log("zarf", S["hat_x_zarf"])
# 2) hava yolu ve acikliklar
dz = next(p for p in L1 if p["ad"].startswith("ReSpeaker"))
fan = next(z_ for z_ in KP.ZARF if z_["ad"].startswith("Fan yeri"))
yar = []
for (y0, n) in ((36.0, 3), (72.0, 4)):
    for (x0, x1) in ((-45.0, -10.0), (10.0, 45.0)):
        for k in range(n):
            yar.append(Part.makeBox(x1 - x0, 3.0, KT + 2, V(x0, y0 + 7.0 * k, ZB - 1) + VB))
YAR = Part.makeCompound(yar)
hat_ust = Part.makeCompound([hat_bil, baslik])
S["aciklik"] = dict(
    hat_dizi_mm=round(HATSH.distToShape(dz["shape"])[0], 2),
    hat_kart_dizi_mm=round(Part.makeCompound([hat_pcb, hat_bil]).distToShape(dz["shape"])[0], 2),
    hat_fan_yeri_mm=round(HATSH.distToShape(fan["shape"])[0], 2), hat_fan_yeri_kesisim_mm3=round(HATSH.common(fan["shape"]).Volume, 2),
    hat_kart_fan_yeri_kesisim_mm3=round(Part.makeCompound([hat_pcb, hat_bil]).common(fan["shape"]).Volume, 2),
    hat_yarik_mm=round(HATSH.distToShape(YAR)[0], 2),
    hat_alti_sogutucu_mm=round(hat_pcb.distToShape(pi_sh)[0], 2),
    hat_arka_kenar_duvar_ic_mm=round((hat_pcb.BoundBox.ZMin - ZT) - (ZB + KT), 2),
    pi_arka_kenar_duvar_ic_mm=round((pi_sh.BoundBox.ZMin - ZT) - (ZB + KT), 2),
    hat_ust_en_yakin=en_yakin(hat_ust, L1, k=5, atla=("AI HAT+", "Raspberry")),
    hat_en_yakin=en_yakin(HATSH, L1, k=8, atla=("AI HAT+", "Raspberry", "Burc M2,5", "Vida M2,5")),
    pi_en_yakin=en_yakin(pi_sh, L1, k=6, atla=("AI HAT+", "Burc M2,5", "Vida M2,5", "Kopuk bant")))
log("aciklik", S["aciklik"])
# 3) erisim
ER = {}
for k_ in range(4):
    vi = next(p for p in L1 if p["ad"] == "AI HAT+ vidasi M2,5x5 (%d)" % k_)
    c = vi["bb"].Center
    ER["HAT vidasi %d (yukari, O6)" % k_] = serbest(V(c.x, vi["bb"].YMax + 0.05, c.z), (0, 1, 0), 3.0, 80.0, L1, ())
for p in [p for p in L1 if p["ad"].startswith("Dizi vidasi")]:
    c = p["bb"].Center
    ER[p["ad"] + " (asagi, O8)"] = serbest(V(c.x, p["bb"].YMin - 0.05, c.z), (0, -1, 0), 4.0, 120.0, L1, ())
for b in _boss_c:
    c = b["bb"].Center
    ER[b["ad"] + " (disaridan, O6)"] = serbest(V(c.x, c.y, b["bb"].ZMin - 0.05), (0, 0, -1), 3.0, 60.0, L1, ())
S["erisim"] = ER
log("erisim", ER)
# 4) tilt sinirinda arka kabuk ve dikis civatasi x boyun (Pan + Govde)
sab = [p for p in L1 if p["grup"] in ("Pan", "Govde") and p["tur"] != "Referans"]
TL = {}
for th in (-15, 15):
    pl = Ptilt(th)
    en = (1e9, None)
    for p in [p for p in L1 if p["ad"].startswith(("Arka kafa kabugu", "Kabuk civatasi M3x6 ISO 7380 (kafa sag/sol arka duvar", "AI HAT+"))]:
        sh = p["shape"].copy()
        sh.transformShape(pl.toMatrix())
        for q in sab:
            if q["bb"].isValid() and sh.BoundBox.intersect(q["bb"]) and sh.common(q["shape"]).Volume > 0.5:
                en = min(en, (0.0, (p["ad"], q["ad"], "CAKISMA")))
            g = sh.BoundBox
            qb = q["bb"]
            if max(g.XMin - qb.XMax, qb.XMin - g.XMax, g.YMin - qb.YMax, qb.YMin - g.YMax, g.ZMin - qb.ZMax, qb.ZMin - g.ZMax, 0) > 30:
                continue
            d = sh.distToShape(q["shape"])[0]
            if d < en[0]:
                en = (d, (p["ad"], q["ad"]))
    TL[str(th)] = (round(en[0], 2), en[1])
S["tilt_sinir_en_yakin"] = TL
log("tilt", TL)
# 5) kutle ve tork
S["tork_hatsiz"] = tork(L0)
S["tork_hatli"] = tork(L1)
log("tork", S["tork_hatsiz"], S["tork_hatli"])
# 6) baski (degisen kabuk parcalari; KL.baski_analiz, kafa_montaj ile ayni doluluk)
S["baski"] = {}
for ad in ("Arka kafa kabugu sag", "Arka kafa kabugu sol", "Kafa iskeleti"):
    p = next(q for q in P if q["ad"] == ad)
    by = p["baski"]["yukari"]
    r = KL.baski_analiz(ad, p["shape"], by, p["doluluk"] or K10.DOLULUK)
    S["baski"][ad] = {k: r[k] for k in ("olcu", "sigar", "destek_sorun_sayi", "desteksiz", "destek_sorun", "kutle_g", "sure_saat")}
log("baski", {k: (v["destek_sorun_sayi"], v["kutle_g"]) for k, v in S["baski"].items()})
S["sure_s"] = round(time.time() - t0, 1)
json.dump(S, open(os.path.join(HERE, "hat-secenek-%s.json" % SEC), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
# gorsel icin gecici FCStd (depo disi; HAT_FCSTD verilirse)
_fc = os.environ.get("HAT_FCSTD")
if _fc:
    doc = App.newDocument("hat_%s" % SEC)
    for p in L1:
        if p["tur"] == "Referans":
            continue
        o = doc.addObject("Part::Feature", "P")
        o.Label = p["ad"]
        o.Shape = p["shape"]
        o.addProperty("App::PropertyString", "Grup")
        o.Grup = p["grup"]
    for z_ in KP.ZARF:
        o = doc.addObject("Part::Feature", "Z")
        o.Label = "ZARF " + z_["ad"]
        o.Shape = z_["shape"]
        o.addProperty("App::PropertyString", "Grup")
        o.Grup = "Zarf"
    doc.saveAs(_fc)
    App.closeDocument(doc.Name)
log("BITTI")
