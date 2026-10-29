# Y2a kontrol: bagimsiz devrilme hesabi (parca kutle merkezlerinden; poz = moduller.beklenen). Yalniz okur.
import os, sys, json, math, itertools, time
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "..", "tasarim", "freecad")   # planlama/y2 -> proje koku
sys.path.insert(0, os.path.join(R, "montaj")); sys.path.insert(0, R)
import FreeCAD as App
import moduller as MD
A = MD.A; V = App.Vector
G = 9.81
P = []   # (modul, grup, kutle, global merkez, ad)
TUM = {}
for ad in MD.SIRA:
    d = MD.yukle(ad); TUM[ad] = d
    for p in d["parcalar"]:
        if p["haric"]: continue
        P.append((ad, p["grup"], p["kutle"], MD.global_nokta(ad, p["merkez"]), p["ad"]))
KP = dict(kutle_g=400.0, merkez=(0.0, 150.0, -60.0))   # taban_parcalar.KABLO_PAY (tasarim varsayimi)
aku = [x for x in P if x[0] == "taban" and x[4].lower().startswith("aku")]
print("aku parcalari", [(x[4], round(x[2], 1), [round(c, 1) for c in x[3]]) for x in aku])
cache = {}
def pl(ad, grup, poz):
    d = TUM[ad]
    if d["beklenen"] is None: return None
    k = (ad, grup, tuple(sorted(poz.items())))
    if k not in cache:
        q = d["beklenen"](poz, grup)
        cache[k] = None if q.isIdentity() else MD.global_poz(ad, q)
    return cache[k]
def am(poz_sag, poz_sol, yuk_g=0.0, aku_dz=0.0):
    m, mom = 0.0, V(0, 0, 0)
    for (ad, g, k, c, n) in P:
        poz = poz_sol if ad.endswith("_sol") else poz_sag
        if ad.startswith(("omuz", "dirsek")):
            q = pl(ad, g, poz)
            if q is not None: c = q.multVec(c)
        if aku_dz and ad == "taban" and n.lower().startswith("aku"):
            c = c + V(0, 0, aku_dz)
        m += k; mom = mom + c * k
    m += KP["kutle_g"]; mom = mom + V(*KP["merkez"]) * KP["kutle_g"]
    if yuk_g:
        for ad, poz in (("dirsek_sag", poz_sag), ("dirsek_sol", poz_sol)):
            e = MD.global_nokta(ad, A.DIRSEK["el_ucu"])
            q = pl(ad, "El", poz)
            if q is not None: e = q.multVec(e)
            m += yuk_g; mom = mom + e * yuk_g
    return m, mom * (1.0 / m)
XC, ZC = A._X_WH, A.L0 / 2 - 65
def dev(C, rampa):
    th = math.radians(rampa); h = C.y
    f = lambda d: G * (d * math.cos(th) - h * math.sin(th)) / h
    return dict(ileri=f(ZC - C.z), geri=f(ZC + C.z), yan=f(XC - abs(C.x)))
def poz(s1, s2, dr, bl=0.0): return dict(one_arka=s1, yana=s2, dirsek=dr, bilek=bl, pan=0.0, tilt=0.0)
OUT = {}
EV = poz(0, 5, 0)
for ad_, ps, pl_, yk, dz in (("ev", EV, EV, 0, 0), ("ev_S2_0", poz(0, 0, 0), poz(0, 0, 0), 0, 0), ("geri_S1-45", poz(-45, 5, 0), poz(-45, 5, 0), 0, 0),
                             ("one_S1_90", poz(90, 5, 0), poz(90, 5, 0), 0, 0), ("one_yuk_0.5kg", poz(90, 5, 0), poz(90, 5, 0), 500.0, 0),
                             ("ev_aku+75", EV, EV, 0, 75.0), ("geri_aku+75", poz(-45, 5, 0), poz(-45, 5, 0), 0, 75.0)):
    m, C = am(ps, pl_, yk, dz)
    r = {k: round(v, 3) for k, v in dev(C, 5.0).items()}
    OUT[ad_] = dict(kutle_g=round(m, 1), am=[round(C.x, 2), round(C.y, 2), round(C.z, 2)],
                    duz={k: round(v, 3) for k, v in dev(C, 0.0).items()}, rampa5=r, rampa5_pay={k: round(v / 1.5, 3) for k, v in r.items()})
    print(ad_, OUT[ad_], flush=True)
# en kotu: simetrik + tek kol izgarasi (yuksuz), rampa 5
en = {}
for s1, s2, dr in itertools.product(range(-45, 136, 15), (5, 30, 60, 90, 120), (0, 35, 70, 105)):
    if s1 >= 120 and s2 > 117: s2 = 117
    for kip in ("simetrik", "sag"):
        p_ = poz(s1, s2, dr)
        m, C = am(p_, p_ if kip == "simetrik" else EV)
        r = dev(C, 5.0)
        for k, v in r.items():
            if k not in en or v < en[k][0]: en[k] = (round(v, 3), kip, (s1, s2, dr), [round(c, 2) for c in C])
OUT["en_kotu_rampa5_yuksuz"] = en
print("en kotu", en, flush=True)
json.dump(OUT, open(os.path.join(HERE, "Y2a-K-devrilme.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
