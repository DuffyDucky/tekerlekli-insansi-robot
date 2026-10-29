# Kafa modulu (1,65 m; boyun + pan + tilt + 10,1" kafa) - PARCALAR, kutle ve kinematik (FreeCAD 1.1, Part)
# Import edilebilir: kafa_montaj.py (kontroller + kayit), ../carpisma.py, ../montaj/moduller.py.
# Koordinat (kafa yereli, arayuz.MODULLER["kafa"]): orijin = traversin ust yuzu ortasi (global 0, S3 + 20 = 1360, 0), X sag, Y yukari,
# Z ileri. Pan ekseni yerel Y ekseni (x = z = 0), tilt ekseni X'e paralel (arayuz.KAFA tilt_nokta: y 188,255, z 25). Ev pozu: duz bakis.
#
# Y2a (26 Ekim 2026; karar 21 Ekim 2026 "yuz ekrani 10 inc sinifi HDMI", Duffy 25 Ekim "ana projeye 170den devam"): taslak-170'deki yeni kafa
# modulun kendisi oldu. Yapi:
#   Govde (traverse sabit) : 125 cm kafasinin Govde grubu AYNEN (kafa7_parcalar): boyun plakasi, servo yuvasi, rulman yuvasi, 6808 cifti,
#                            pan MG996R + baglantilari.
#   Pan (pan ekseninde)    : 125 cm Pan grubu; egme catali + tilt MG996R + 625ZZ pimi + catal isil gomme somunu adaptor_h YUKARI;
#                            catalin 4x M3x8 mil civatasi yerine boyun yukseltme adaptoru (PETG) + 4x M3 saplama (DIN 976; mil flansindaki
#                            mevcut isil gomme somunlara) + pul + M3 DIN 985 (kafa10_lib.adaptor).
#   Kafa (Pan * tilt)      : 10,1" HDMI ekranli yeni kafa (kafa10_lib.kur): iskelet (tabla + yanaklar), 4 kabuk parcasi (on/arka x sag/sol),
#                            ekran + 4 tutucu tirnak, Camera Module 3, Pi 5 + 5 V cevirici + amfi; 125 cm'den tilt horn'u, horn vidasi, 625ZZ
#                            dis bilezigi ve 4 yanak-horn civatasi (eksene gore ayni yerde). Tilt ekseni Bas grubunun AM'sinden gecer
#                            (arayuz.KAFA denge dy / zb; kafa_montaj olcer).
import os, sys, math, time

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A
import kafa7_parcalar as K7                  # 125 cm kafasi (Govde + Pan buradan)
import kafa10_lib as K10                     # 10,1" kafa (Bas) + boyun adaptoru
from kafa_lib import *   # noqa  (V, App, Part, cyl, box, MG, HORN_MG, washer, nut, ...)

t0 = time.time()
K = A.KAFA
YT, ZT = K["tilt_nokta"][1], K["tilt_nokta"][2]      # tilt ekseni (188,255; 25)
YT7 = A.KAFA7["tilt_nokta"][1]                       # 125 cm tilt ekseni (130)
H_ADAPTOR = YT - YT7                                 # 58,255: catal + tilt servosu + pim bu kadar yukari
assert abs(H_ADAPTOR - K["adaptor_h"]) < 1e-9
V_PAN = V(0, H_ADAPTOR, 0)
DOLULUK = K7.DOLULUK
MG = K7.MG

# Pan grubunda yukari kalkan parcalar (taslak-170 PAN_KALKAN ile ayni) ve kaldirilan civatalar
PAN_KALKAN = ("Egme catali", "Tilt servosu MG996R", "Tilt servosu cikis mili", "Tilt servosu kulak civatasi M4x16", "Tilt servosu kontra somunu M4",
              "625ZZ rulman (ic bilezik)", "Pim pulu M5", "Pim civatasi M5x12", "Isil gomme somun M5 (catal)")
KALDIRILAN = ("Catal-mil civatasi M3x8",)

P = []          # parcalar: ad, grup (Govde / Pan / Kafa), shape, tur, malzeme, kod, renk, patlat, not_, kutle, merkez, hacim, kati, bb
BAG = []        # baglanti kontrolleri (kafa_montaj): 125 cm Govde/Pan baglantilari (indeksler yeniden) + tilt horn + tilt pimi + adaptor saplamalari
BAG_METIN = []  # kafa10 baglantilari (tablo; kafa_montaj temas olcer)
ESKI = {}       # 125 cm indeksi -> yeni indeks
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a) + "  %.1fs" % (time.time() - t0)
    LOG.append(s)
    print(s)


def tasi(sh, v):
    s = sh.copy()
    if v.Length > 1e-12:
        m = App.Matrix()
        m.move(v)
        s.transformShape(m, True)
    return s


def ekle(ad, grup, shape, tur, malzeme, kod, renk, kutle=None, doluluk=None, not_="", patlat=(0, 0, 0), baski=None):
    P.append(dict(ad=ad, grup=grup, shape=shape, tur=tur, malzeme=malzeme, kod=kod, renk=renk, kutle_sabit=kutle, doluluk=doluluk,
                  not_=not_, patlat=list(patlat), baski=baski))
    return len(P) - 1


# ====================================================================== 1) Govde + Pan (125 cm kafasindan)
for i, p in enumerate(K7.P):
    if p["grup"] not in ("Govde", "Pan"):
        continue                          # eski Bas (Kafa) grubu ve kablo gosterimleri: yeni kafa asagida
    if p["ad"] in KALDIRILAN:
        continue
    v = V_PAN if (p["grup"] == "Pan" and p["ad"] in PAN_KALKAN) else V(0, 0, 0)
    ESKI[i] = ekle(p["ad"], p["grup"], tasi(p["shape"], v), p["tur"], p["malzeme"], p["kod"], p["renk"], kutle=p["kutle"],
                   doluluk=p.get("doluluk"), not_=p["not_"] + (" (boyun adaptoruyle %.1f mm yukari)" % H_ADAPTOR if v.Length > 0 else ""),
                   patlat=p["patlat"])
    P[-1]["yukari_kalkti"] = v.Length > 0
n_gp = len(P)

# ====================================================================== 2) boyun yukseltme adaptoru + saplamalar (Pan)
ADAPTOR_IDX = []
for q in K10.adaptor(H_ADAPTOR, log=log):
    ADAPTOR_IDX.append(ekle(q["ad"], "Pan", q["shape"], q["tur"], q["malzeme"], q["kod"], q["renk"], kutle=q["kutle"], doluluk=q.get("doluluk"),
                            not_=q["not_"], patlat=(0, 60, 0), baski=q.get("baski")))

# ====================================================================== 3) 10,1" kafa (Bas = grup "Kafa"), eksen cercevesinden kafa yereline
KD = K["denge"]
P_BAS, BAG10, INFO10 = K10.kur(KD["dy"], KD["zb"], log=log)
V_BAS = V(0, YT, ZT)
BAS_IDX = {}
for q in P_BAS:
    i = ekle(q["ad"], "Kafa", tasi(q["shape"], V_BAS), q["tur"], q["malzeme"], q["kod"], q["renk"], kutle=q["kutle"], doluluk=q.get("doluluk"),
             not_=q["not_"], patlat=(0, 140, 0), baski=q.get("baski"))
    BAS_IDX.setdefault(q["ad"], []).append(i)
for b in BAG10:
    BAG_METIN.append(dict(b))
BAG_METIN.append(dict(ad="Boyun yukseltme adaptoru + egme catali -> boyun mili flansi",
                      tip="4x M3 saplama DIN 976 (mil flansindaki M3 isil gomme somunlara) + pul + M3 DIN 985", adet=4,
                      parcalar=("Egme catali", "Boyun yukseltme adaptoru", "Boyun mili"), nokta=(0.0, K7.Y_FL[1], 0.0)))

# ====================================================================== 4) baglanti kontrol tanimlari (kafa_montaj)
I = {}
for k, p in enumerate(P):
    I.setdefault(p["ad"], k)


def yeni(i_eski):
    return ESKI[i_eski]


for b in K7.BAG:
    alanlar = [k_ for k_ in ("civata", "pul", "somun", "insert", "bas_parca", "govde", "plaka", "servo", "horn", "rul_i", "rul_d", "catal",
                             "kart", "burc", "civata_alt") if b.get(k_) is not None]
    gruplar = {K7.P[b[k_]]["grup"] for k_ in alanlar}
    if not gruplar <= {"Govde", "Pan"}:
        continue                          # 125 cm Bas baglantilari (kabuk, LCD, kamera, Pi, yanak, pim): asagida yeniden
    if any(K7.P[b[k_]]["ad"] in KALDIRILAN for k_ in alanlar):
        continue                          # catal -> mil civatalari kaldirildi (saplama)
    nb = dict(b)
    for k_ in alanlar:
        nb[k_] = yeni(b[k_])
    if any(P[nb[k_]].get("yukari_kalkti") for k_ in alanlar):
        nb["nokta"] = tuple(V(*b["nokta"]) + V_PAN)
        for kk_ in ("yuz_bas", "kasa"):
            if kk_ in nb and abs(b["yon"][1]) > 0.5:
                nb[kk_] = b[kk_] + H_ADAPTOR
        if "horn_yuz" in nb and abs(b["yon"][1]) > 0.5:
            nb["horn_yuz"] = tuple(y_ + H_ADAPTOR for y_ in b["horn_yuz"])
    BAG.append(nb)
# tilt horn: kafa iskeleti sag yanak -> horn (125 cm'deki gibi 4x M3x8; yanak olculeri ayni, eksen H yukari)
I_ISK = I["Kafa iskeleti (10 in)"]
I_HORN_T = I["Tilt horn 25T aluminyum disk"]
I_CATAL = I["Egme catali"]
for b in K7.BAG:
    if b["ad"] == "Kafa iskeleti sag yanak -> tilt horn":
        c0 = V(*b["nokta"]) + V_PAN
        civ = min(BAS_IDX["Yanak-horn civatasi M3x8"], key=lambda i_: (P[i_]["shape"].BoundBox.Center - c0).Length - 0.0)
        nb = dict(b, civata=civ, govde=I_ISK, horn=I_HORN_T, nokta=tuple(c0))
        BAG.append(nb)
    elif b["tip"] == "pim":
        nb = dict(b, civata=yeni(b["civata"]), pul=yeni(b["pul"]), rul_i=yeni(b["rul_i"]), insert=yeni(b["insert"]),
                  rul_d=I["625ZZ rulman (dis bilezik)"], govde=I_CATAL, catal=I_ISK, nokta=(b["nokta"][0], YT, ZT))
        BAG.append(nb)
# adaptor saplamalari: alt ucu mil flansi isil gomme somununda, ust ucu catal tabani ustunde pul + DIN 985 (somunu gecer)
I_MIL = I["Boyun mili"]
I_AD = I["Boyun yukseltme adaptoru"]
for k, (x, z) in enumerate(K7.FL_DEL):
    ins = min([i_ for i_, p in enumerate(P) if p["ad"].startswith("Isil gomme somun M3 (mil") or p["ad"].startswith("Isil gomme somun M3 (catal")],
              key=lambda i_: (P[i_]["shape"].BoundBox.Center - V(x, K7.Y_FL[1], z)).Length, default=None)
    BAG.append(dict(ad="Adaptor saplamasi %d" % k, tip="saplama",
                    civata=next(i_ for i_, p in enumerate(P) if p["ad"].startswith("Saplama M3x") and p["ad"].endswith("(%d)" % k)),
                    pul=I["Pul M3 (saplama %d)" % k], somun=I["Somun M3 DIN 985 (saplama %d)" % k], insert=ins, adaptor=I_AD, catal=I_CATAL,
                    mil=I_MIL, nokta=(x, K7.Y_FL[1], z), yon=(0, 1, 0), d=3))

# ====================================================================== 5) kutle ve merkez
RHO = dict(K7.RHO)
RHO.update({"Celik 10.9": 7.85})
for p in P:
    sh = p["shape"]
    sol = sh.Solids
    p["hacim"] = sh.Volume
    p["kati"] = len(sol)
    if sol:
        vt = sum(s.Volume for s in sol)
        cc = V(0, 0, 0)
        for s in sol:
            cc = cc + s.CenterOfMass * (s.Volume / vt)
        p["merkez"] = cc
    else:
        p["merkez"] = sh.BoundBox.Center
    if p["kutle_sabit"] is not None:
        p["kutle"] = p["kutle_sabit"]
    else:
        d_ = p["doluluk"] if p["doluluk"] else (DOLULUK if p["malzeme"] == "PETG" else 1.0)
        p["kutle"] = p["hacim"] / 1000.0 * RHO.get(p["malzeme"], 1.0) * d_
    p["bb"] = sh.BoundBox
    if p["tur"] == "Baski":
        p["doluluk_baski"] = p["doluluk"] or DOLULUK

# baski parcalari (robot koordinatinda tablaya gore yukari) - Govde/Pan 125 cm tablosundan, adaptor + kafa10 parca bilgisinden
BASKI = {ad: bd for ad, bd in K7.BASKI.items() if ad in I and P[I[ad]]["grup"] in ("Govde", "Pan")}
for p in P:
    if p["tur"] == "Baski" and p["ad"] not in BASKI and p.get("baski"):
        BASKI[p["ad"]] = dict(yukari=tuple(p["baski"]["yukari"]), yon=p["baski"]["yon"])
assert all(p["ad"] in BASKI for p in P if p["tur"] == "Baski"), [p["ad"] for p in P if p["tur"] == "Baski" and p["ad"] not in BASKI]


# ====================================================================== 6) kinematik
def Ppan(psi):      # +psi: yuz (+Z) robotun sagina (+X)
    return App.Placement(V(0, 0, 0), App.Rotation(V(*K["pan_yon"]), psi), V(0, 0, 0))


def Ptilt(th):      # +th: basi one egme (yuz asagi)
    return App.Placement(V(0, 0, 0), App.Rotation(V(*K["tilt_yon"]), th), V(0, YT, ZT))


def grup_yer(grup, psi=0.0, th=0.0):
    if grup == "Pan":
        return Ppan(psi)
    if grup == "Kafa":
        return Ppan(psi).multiply(Ptilt(th))
    return App.Placement()


PSIS = list(range(-90, 91, 15))
THS = list(range(-45, 46, 5))
# kafa_montaj'in kullandigi 125 cm olculeri (Govde / Pan ayni)
Y_PK, Y_R1, Y_R2, Y_FL, Y_CB, Y_OMUZ = K7.Y_PK, K7.Y_R1, K7.Y_R2, K7.Y_FL, K7.Y_CB, K7.Y_OMUZ
X_RUL, X_TH, X_SAG, X_SOL = K7.X_RUL, K7.X_TH, K7.X_SAG, K7.X_SOL
I_MIL, I_RY = I["Boyun mili"], I["Rulman yuvasi"]
INFO = dict(INFO10, adaptor_h=H_ADAPTOR, tilt_y=YT, dy=KD["dy"], zb=KD["zb"])
log("kafa (1,65 m): %d parca (Govde/Pan %d, adaptor %d, Bas %d), %.1f g" % (len(P), n_gp, len(ADAPTOR_IDX), len(P_BAS), sum(p["kutle"] for p in P)))
