# Iskelet modulu (V3) - PARCALAR: sase sigma cercevesi, govde diregi, omuz traversi, kose baglantilari ve tum
# baglanti elemanlari. Import edilebilir: iskelet_montaj.py (kontroller + kayit) ve ../carpisma.py kullanir.
# Koordinat = global (arayuz.py): orijin zemin + robot merkezi, +X sag, +Y yukari, +Z ileri, mm.
# Plakalar, motorlar, teker, aku, elektronik burada YOK (taban modulu); onlarin yeri arayuz.BOLGELER'de.
import os, sys, math, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from ortak_lib import *   # noqa
import arayuz as A

t0 = time.time()
P = []        # parcalar
BAG = []      # baglantilar (rapor tablosu + baglanti kontrolleri)
H = A.SG / 2


def add(ad, grup, shape, tur, malzeme, kod=None, renk="gri", patlat=(0, 0, 0), not_="", kutle=None):
    P.append(dict(ad=ad, grup=grup, shape=shape, tur=tur, malzeme=malzeme, kod=kod or ad, renk=renk,
                  patlat=list(patlat), not_=not_, kutle_sabit=kutle))
    return len(P) - 1


def sigma_kod(L):
    return "Sigma 40x40 agir kanal 10, %s mm" % (("%.1f" % L).rstrip("0").rstrip("."))


# ====================================================================== SASE (rc:706-712, V3 olcekli)
RAY = {}
for s, ad in ((1, "sag"), (-1, "sol")):
    RAY[s] = add("Sase uzun rayi " + ad, "Sase", sigma_z(-A.UZUN_RAY_L / 2, A.UZUN_RAY_L / 2, x=s * A.UZUN_RAY_X, y=A.RAY_YC),
                 "Satin", "Aluminyum 6063", kod=sigma_kod(A.UZUN_RAY_L), renk="alu", patlat=(s * 90, 0, 0))
ARA = {}
for z, ad in zip(A.ARA_RAY_Z, ("arka", "orta", "on")):
    ARA[z] = add("Sase ara rayi " + ad, "Sase", yerlestir(sigma_x(-A.ARA_RAY_L / 2, A.ARA_RAY_L / 2), App.Placement(V(0, A.RAY_YC, z), App.Rotation())),
                 "Satin", "Aluminyum 6063", kod=sigma_kod(A.ARA_RAY_L), renk="alu", patlat=(0, 0, z * 0.35))

# ====================================================================== DIREK + TRAVERS (rc:759-766)
DIREK = add("Govde diregi", "Direk", sigma_y(A.DIREK_Y0, A.DIREK_Y1), "Satin", "Aluminyum 6063",
            kod=sigma_kod(A.DIREK_L), renk="alu", patlat=(0, 120, 0))
TRAVERS = add("Omuz traversi", "Travers", yerlestir(sigma_x(-A.TRAVERS_L / 2, A.TRAVERS_L / 2), App.Placement(V(0, A.TRAVERS_Y, 0), App.Rotation())),
              "Satin", "Aluminyum 6063", kod=sigma_kod(A.TRAVERS_L), renk="alu", patlat=(0, 330, 0),
              not_="omuz modulunun traversiyle ayni geometri (arayuz kontrolu carpisma.py'de)")

# ====================================================================== 40x40 genis kose baglantilar (rc:762-768)
ROT = {"I": App.Rotation(), "Ry180": App.Rotation(V(0, 1, 0), 180), "Rx180": App.Rotation(V(1, 0, 0), 180),
       "Rz180": App.Rotation(V(0, 0, 1), 180)}
KB_GOVDE = kose_baglanti()
KB_ELEMAN = kose_baglanti_elemanlari()
KD, KL = A.KOSE["civata"]
for (ad, kose, rot) in A.KOSE_YER:
    pl = App.Placement(V(*kose), ROT[rot])
    alt = "Direk" if "ray" in ad else "Travers"
    profil_a = ARA[0.0] if alt == "Direk" else TRAVERS          # ayak A'nin yattigi profil
    sx = 1 if kose[0] > 0 else -1
    pk = (sx * 45, 40, 0) if alt == "Direk" else (sx * 45, 240, 0)
    ib = add("Kose baglanti 40x40 genis (%s)" % ad, alt, yerlestir(KB_GOVDE, pl), "Satin", "Aluminyum dokum",
             kod="40x40 genis kose baglanti (Robolink)", renk="alu2", patlat=pk, kutle=A.KOSE["kutle_g"])
    eleman = []
    for k, (tur, sh) in enumerate(KB_ELEMAN):
        ayak = "A" if k < 3 else "B"
        nv = pl.Rotation.multVec(V(0, 1, 0) if ayak == "A" else V(1, 0, 0))   # ayagin profil disina bakan normali
        if tur == "pul":
            e = add("Pul M6 (%s, ayak %s)" % (ad, ayak), alt, yerlestir(sh, pl), "Baglanti", "Celik", kod="M6 DIN 125 pul",
                    renk="celik", patlat=tuple(V(*pk) + nv * 30))
        elif tur == "civata":
            e = add("Civata M6x%d (%s, ayak %s)" % (KL, ad, ayak), alt, yerlestir(sh, pl), "Baglanti", "Celik 8.8",
                    kod="M6x%d DIN 912" % KL, renk="celik", patlat=tuple(V(*pk) + nv * 55))
        else:
            e = add("Cekic somun M6 (%s, ayak %s)" % (ad, ayak), alt, yerlestir(sh, pl), "Baglanti", "Celik",
                    kod="M6 cekic somun, kanal 10", renk="celik", patlat=tuple(V(*pk) - nv * 25))
        eleman.append(e)
    BAG.append(dict(ad=ad, tip="kose", govde=ib, profiller=[profil_a, DIREK], eleman=eleman, yer=pl,
                    aciklama="Ayak A %s, ayak B direk x yuzu; kamalar kanal agzinda" %
                    ("orta ara rayin ust yuzunde" if alt == "Direk" else "traversin alt yuzunde")))

# ====================================================================== ic kose baglantilar (sase T birlesimleri)
# Ara raylar uzun raylarin ic yuzune alin alin dayanir. Dis kose baglanti icin yer yok: ic koselerde aku
# (arka), BTS7960 (on) ve XL4016 / aku (orta) ayrilmis bolgeleri var (arayuz.BOLGELER). Bu yuzden kanal ici
# ic kose baglanti: ayaklar ara rayin z yuzu kanalinda ve uzun rayin ic yuz kanalinda, disari tasmaz.
IK_GOVDE, IK_VIDA = ic_kose_baglanti()
for z in A.ARA_RAY_Z:
    taraflar = (1,) if z < 0 else ((-1,) if z > 0 else (1, -1))
    for s in (1, -1):
        for t in taraflar:
            c = (s * (A.ARA_RAY_L / 2), A.RAY_YC, z + t * H)
            e1, e2 = V(-s, 0, 0), V(0, 0, t)
            e3 = e2.cross(e1)
            m = matris(e1, e3, e2, c)
            ad = "Sase %s %s %s" % ("sag" if s > 0 else "sol", {-1: "arka", 0: "orta", 1: "on"}[int(math.copysign(1, z)) if z else 0],
                                    "on yuz" if t > 0 else "arka yuz")
            pk = (s * 90 + s * 0, 0, z * 0.35 + t * 25)
            ib = add("Ic kose baglanti kanal 10 (%s)" % ad, "Sase", yerlestir(IK_GOVDE, m), "Satin", "Celik (tahmini)",
                     kod="Ic kose baglanti kanal 10 (tahmini olcu)", renk="celik2", patlat=pk)
            ev = []
            for k, v in enumerate(IK_VIDA):
                ev.append(add("Set vida M6x10 (%s, %s)" % (ad, "ara ray" if k == 0 else "uzun ray"), "Sase", yerlestir(v, m),
                              "Baglanti", "Celik 45H", kod="M6x10 DIN 913 set vida", renk="siyah",
                              patlat=tuple(V(*pk) + (e2 if k == 0 else e1) * 20)))
            BAG.append(dict(ad=ad, tip="ic_kose", govde=ib, profiller=[ARA[z], RAY[s]], eleman=ev, yer=m,
                            aciklama="Ayak 1 ara rayin %s kanalinda, ayak 2 uzun rayin ic yuz kanalinda" % ("on" if t > 0 else "arka")))

# ====================================================================== kutle ve merkez
RHO = {"Aluminyum 6063": A.SG_RHO, "Celik": 7.85, "Celik 8.8": 7.85, "Celik 45H": 7.85, "Celik (tahmini)": A.IC_KOSE["rho"]}
for p in P:
    sh = p["shape"]
    p["hacim"] = sh.Volume
    p["kati"] = len(sh.Solids)
    p["merkez"] = sh.Solids[0].CenterOfMass if p["kati"] == 1 else sh.BoundBox.Center
    p["kutle"] = p["kutle_sabit"] if p["kutle_sabit"] is not None else p["hacim"] / 1000.0 * RHO[p["malzeme"]]
    p["bb"] = sh.BoundBox
