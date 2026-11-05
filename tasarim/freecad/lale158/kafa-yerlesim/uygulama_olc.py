# -*- coding: utf-8 -*-
# Lale 1,58 m - secim B + R1 uygulamasi: son modelde olcum (freecadcmd). Yalniz uygulama-olcum.json yazar; modele dokunmaz. Ana montajdan sonra.
# FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
import os, sys, json, math, time
sys.dont_write_bytecode = True
import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
for p_ in (LALE, UST):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import arayuz as A
import kablo_yolu_ekran as KY

t0 = time.time()
K, SU = A.KAFA, A.SES_USB
Y0 = K["taban_y"]
YT, ZT = K["tilt_nokta"][1], K["tilt_nokta"][2]
DY = K["denge"]["dy"]
ZB = K["denge"]["zb"]
YU = DY + K["govde_y"][1]
Y_IC_UST = YU - 2.5
D_ = SU["dizi"]
Y_PCB = Y_IC_UST - D_["gap_jak"] - D_["jak_ust"]


def log(*a):
    print(" ".join(str(x) for x in a), "[%.0fs]" % (time.time() - t0), flush=True)


doc = App.openDocument(os.path.join(UST, "montaj", "robot-montaj.FCStd"))
P = []
for o in doc.Objects:
    if o.TypeId == "Part::Feature" and hasattr(o, "Tur") and getattr(o, "Tur", "") != "Referans":
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        s = s.copy()
        P.append(dict(ad=o.Label, sh=s, bb=s.BoundBox))
App.closeDocument(doc.Name)
log("parca", len(P))


def bul(bas):
    return [p for p in P if p["ad"].startswith(bas)]


def tek(bas):
    r = bul(bas)
    assert r, bas
    return r[0]


def tup(yol, r):
    t = None
    for a_, b_ in zip(yol[:-1], yol[1:]):
        a_, b_ = V(*a_), V(*b_)
        if (b_ - a_).Length < 1e-6:
            continue
        c = Part.makeCylinder(r, (b_ - a_).Length, a_, b_ - a_).fuse(Part.makeSphere(r, b_))
        t = c if t is None else t.fuse(c)
    return t


def bbgap(a, b):
    dx = max(a.XMin - b.XMax, b.XMin - a.XMax, 0.0)
    dy = max(a.YMin - b.YMax, b.YMin - a.YMax, 0.0)
    dz = max(a.ZMin - b.ZMax, b.ZMin - a.ZMax, 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def en_yakin(sh, k=6, atla=()):
    bb = sh.BoundBox
    aday = sorted(((bbgap(bb, h["bb"]), i) for i, h in enumerate(P) if not h["ad"].startswith(tuple(atla) if atla else ("\0",))))
    r = []
    for g, i in aday:
        if len(r) >= k and g > r[k - 1][1]:
            break
        r.append((P[i]["ad"], round(sh.distToShape(P[i]["sh"])[0], 3)))
        r.sort(key=lambda q: q[1])
    return r[:k]


def cakisma(sh, atla=(), esik=0.5):
    bb = sh.BoundBox
    out = []
    for h in P:
        if h["ad"].startswith(tuple(atla) if atla else ("\0",)) or not bb.intersect(h["bb"]):
            continue
        v = sh.common(h["sh"]).Volume
        if v > esik:
            out.append((h["ad"], round(v, 2)))
    return sorted(out, key=lambda q: -q[1])


def bas_g(x, y, z):
    return V(x, Y0 + YT + y, ZT + z)


S = dict(tarih="2026-11-05", kaynak="montaj/robot-montaj.FCStd + kablo_yolu_ekran.py")
# ------------------------------------------------------------------- 1) cikanlar / girenler
S["model_adlar"] = dict(max98357a=[p["ad"] for p in P if "MAX98357" in p["ad"]],
                        hub=[p["ad"] for p in P if "Hub" in p["ad"]],
                        ses=[p["ad"] for p in P if p["ad"].startswith("USB ses") or "USB ses" in p["ad"]],
                        pam=[p["ad"] for p in P if "PAM8403" in p["ad"]],
                        dizi=[p["ad"] for p in P if p["ad"].startswith(("ReSpeaker", "Dizi"))],
                        hoparlor=[p["ad"] for p in P if p["ad"].startswith("Hoparlor")])
# ------------------------------------------------------------------- 2) mikrofon-hoparlor
hc = KY.hoparlor_merkez()
C_h = V(*hc["C"]) - V(*hc["n"]) * 0.5                 # diyafram onu (global)
c_h_ky = C_h - V(0, Y0, 0)
mics = [V(D_["cx"] - m[1], Y_PCB + m[2] + YT, D_["cz"] - m[0] + ZT) for m in D_["mic"]]


def Ptilt(th):
    return App.Placement(V(0, 0, 0), App.Rotation(V(*K["tilt_yon"]), th), V(0, YT, ZT))


def Ppan(psi):
    return App.Placement(V(0, 0, 0), App.Rotation(V(*K["pan_yon"]), psi), V(0, 0, 0))


en, ev, enb = 1e9, None, -1.0
for psi in range(-90, 91, 15):
    for th in (-15, -10, -5, 0, 5, 10, 15):
        pl = Ppan(psi).multiply(Ptilt(th))
        for m in mics:
            d = (pl.multVec(m) - c_h_ky).Length
            if d < en:
                en, ev = d, (psi, th)
            enb = max(enb, d)
S["mic_hoparlor"] = dict(ev_min_mm=round(min((m - c_h_ky).Length for m in mics), 1), poz_min_mm=round(en, 1), poz=ev, poz_max_mm=round(enb, 1), h1_40cm=bool(en >= 400.0), izgara="pan -90...90 / 15, tilt -15...15 / 5 (ayrik)")
S["hoparlor_duvar"] = dict(C=[round(x, 2) for x in hc["C"]], n=[round(x, 3) for x in hc["n"]], yatay_alti_derece=round(math.degrees(hc["alfa"]), 1))
log("mic", S["mic_hoparlor"])
# ------------------------------------------------------------------- 3) kablolar: tup x SY8205 + tum parcalar; guc ayrimi
sy = tek("SY8205")
yollar = KY.yollar()
kab = {}
for ad, yol in yollar.items():
    t = tup(yol, KY.KABLO[ad][0] / 2)
    v_sy = t.common(sy["sh"]).Volume if t.BoundBox.intersect(sy["bb"]) else 0.0
    kab[ad] = dict(sy8205_mm=round(t.distToShape(sy["sh"])[0], 2), sy8205_kesisim_mm3=round(v_sy, 2))
K_ic = {}
for ad, (yol_b, liste) in KY.kafa_ici_qled().items():
    t = tup([bas_g(*q) for q in yol_b], 2.0)
    K_ic[ad] = dict(sy8205_mm=round(t.distToShape(sy["sh"])[0], 2), sy8205_kesisim_mm3=round(t.common(sy["sh"]).Volume, 2),
                    cakisma=cakisma(t, atla=("Yuz ekrani", "Kafa iskeleti", "Yuz kabugu")))
S["kablo_sy8205"] = kab
S["kafa_ici_qled_kablo"] = K_ic
log("SY", kab, K_ic)
_guc = {}
tdz = tup(yollar["Dizi USB"], 2.0)
for adg, sh in (("SY8205", sy["sh"]), ("D24V50F5", tek("5 V cevirici")["sh"]), ("TVS", tek("TVS P6KE6V8A")["sh"]),
                ("PAM 5 V", tup(yollar["PAM 5 V"], 1.5)), ("Hoparlor kablosu", tup(yollar["Hoparlor"], 2.0))):
    _guc[adg] = round(tdz.distToShape(sh)[0], 2)
S["dizi_usb_guc_mm"] = _guc
# koridor: boyuna inen USB, tabla ve Pi'ye aciklik
tk = tup([bas_g(*q) for q in SU["koridor"]], 2.0)
S["koridor_en_yakin"] = en_yakin(tk, k=6)
# ------------------------------------------------------------------- 4) dizi
dz = tek("ReSpeaker")
S["dizi"] = dict(bb_bas=[round(x, 2) for x in (dz["bb"].XMin, dz["bb"].XMax, dz["bb"].YMin - Y0 - YT, dz["bb"].YMax - Y0 - YT, dz["bb"].ZMin - ZT, dz["bb"].ZMax - ZT)],
                 en_yakin=en_yakin(dz["sh"], k=6), cakisma=cakisma(dz["sh"]), kati=len(dz["sh"].Solids), yuz=len(dz["sh"].Faces),
                 kabuk_mm=round(dz["sh"].distToShape(tek("Arka kafa kabugu sag")["sh"])[0], 3), kabuk_kesisim_mm3=round(dz["sh"].common(tek("Arka kafa kabugu sag")["sh"]).Volume, 4), not_="ev pozu; boss PCB ustune degdigi icin mesafe 0 beklenir; kesisim esiksiz (0,799 mm3 duzeltmesinin dogrulamasi)")
# ------------------------------------------------------------------- 5) AI HAT+ zarfi: modelde yok, yeri korunuyor mu (VARSAYIM 65 x 56,5, yigin 16)
x0, z1 = -42.5, -27.893
ah = Part.makeBox(65.0, 1.6 + 3.0, 56.5, bas_g(x0, 41.6 + 16.0, z1 - 56.5))     # yerlesim_lib.ai_hat_zarf ile ayni: kart + bilesen 4,6 mm, Pi ustunden yigin 16 mm
S["ai_hat_zarfi"] = dict(en_yakin=en_yakin(ah, k=5, atla=("Raspberry",)), cakisma=cakisma(ah, atla=("Raspberry",)), dizi_mm=round(ah.distToShape(dz["sh"])[0], 2), not_="v4 satir 114 listede, CAD modelinde yok; zarf VARSAYIM. Zarf Pi'nin ustunde (yerlesim_lib.ai_hat_zarf)")
log("AI", S["ai_hat_zarfi"])
# ------------------------------------------------------------------- 6) hub + kapak
HB = SU["hub"]
hub = tek("USB Hub 4 lu (kapak ici)")
kap = tek("Ust arka servis kapagi")
fz = Part.makeBox(HB["x"][1] - HB["x"][0], HB["y"][1] - HB["y"][0], HB["fis_payi"], V(HB["x"][0], HB["y"][0], HB["z_alt"] + HB["h"]))
_c = kap["sh"].common(Part.makeLine(V(47.5, 1125, -120), V(47.5, 1125, 0)))
S["hub"] = dict(bb_g=[round(x, 2) for x in (hub["bb"].XMin, hub["bb"].XMax, hub["bb"].YMin, hub["bb"].YMax, hub["bb"].ZMin, hub["bb"].ZMax)], en_yakin=en_yakin(hub["sh"], k=6), cakisma=cakisma(hub["sh"]),
                fis_payi_en_yakin=en_yakin(fz, k=5, atla=("USB Hub", "Ust arka servis")), fis_payi_cakisma=cakisma(fz, atla=("USB Hub",)),
                kapak_kati=len(kap["sh"].Solids), kapak_gecerli=kap["sh"].isValid(), kapak_kutle_olcu=None, ic_z_y1125=[round(v.Z, 2) for v in _c.Vertexes],
                bos_port=2, not_="hub kapakla birlikte sokulur; kablolara kapak sokme payi 150 mm (TAHMIN)")
log("hub", S["hub"])
# ------------------------------------------------------------------- 7) hoparlor
for ad_ in ("Hoparlor 40 x 20", "Hoparlor kabi on halka", "Hoparlor kabi arka (flansli)"):
    h_ = tek(ad_)
    S["hop_" + ad_] = dict(bb_g=[round(x, 2) for x in (h_["bb"].XMin, h_["bb"].XMax, h_["bb"].YMin, h_["bb"].YMax, h_["bb"].ZMin, h_["bb"].ZMax)], en_yakin=en_yakin(h_["sh"], k=5), cakisma=cakisma(h_["sh"]))
_ob = tek("Govde orta bandi sag")
S["orta_bant"] = dict(gecerli=_ob["sh"].isValid(), kati=len(_ob["sh"].Solids))
_ar = tek("Arka kafa kabugu sag")
S["arka_sag"] = dict(gecerli=_ar["sh"].isValid(), kati=len(_ar["sh"].Solids))
# ------------------------------------------------------------------- 8) ses karti, PAM
for ad_ in ("USB ses karti", "PAM8403 amfi"):
    h_ = tek(ad_)
    S[ad_] = dict(bb_bas=[round(x, 2) for x in (h_["bb"].XMin, h_["bb"].XMax, h_["bb"].YMin - Y0 - YT, h_["bb"].YMax - Y0 - YT, h_["bb"].ZMin - ZT, h_["bb"].ZMax - ZT)], en_yakin=en_yakin(h_["sh"], k=4, atla=("Kopuk bant",)), cakisma=cakisma(h_["sh"], atla=("Kopuk bant",)))
# ------------------------------------------------------------------- 9) boyun, kablo listesi (saf hesap)
oz = KY.ozet()
S["boyun"] = dict(alan_mm2=oz["boyun_demet_alan_mm2"], gecis=[dict(ad=g["ad"], doluluk=g["doluluk"]) for g in oz["gecis"]])
S["kablo_listesi"] = oz["kablo"]
S["kafa_ici_kablo_listesi"] = oz["kafa_ici_qled"]
S["kafa_ici_kablo_kutle"] = [list(q[:3]) for q in KY.kafa_ici_kablo_kutle()]
S["pi_portlari"] = {"1": "ReSpeaker", "2": "USB ses karti (uzatma + L dirsek)", "3": "Hub (hub 130 mm + uzatma)", "4": "Kafa ekrani dokunmatik"}
S["hub_portlari"] = {"1": "Gogus dokunmatik", "2": "ESP32", "3": "bos", "4": "bos"}
S["sure_s"] = round(time.time() - t0, 1)
json.dump(S, open(os.path.join(HERE, "uygulama-olcum.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("BITTI")
