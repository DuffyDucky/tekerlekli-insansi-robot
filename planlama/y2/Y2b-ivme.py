# Y2b: duz zemin ivme siniri (devrilme payi >= 1,5). Yontem Y2a kontrolununki (Y2a-K-devrilme.py) ile ayni:
# parca kutle merkezlerinden robot AM'si (poz = moduller.beklenen), a_dev = g (d cos th - h sin th) / h, d = AM'nin teker merkez
# hattina yatay uzakligi (on/arka z +-185, yan x +-216), h = AM yuksekligi. Pay = a_dev / a_robot; olcut pay >= 1,5
# => izin verilen ivme a_sinir = a_dev_min / 1,5. Yalniz okur; cikti yaninda Y2b-ivme.json. FreeCAD ile calisir (run_fc.py).
import os, sys, json, math, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "..", "tasarim", "freecad")
sys.path.insert(0, os.path.join(R, "montaj")); sys.path.insert(0, R)
import FreeCAD as App
import moduller as MD
A = MD.A; V = App.Vector
G = 9.81
PAY = 1.5
FREN = 1.8   # acil stop / yazilim freni ust siniri (karar 29.10, Duffy): duzde pay = a_dev_min / FREN >= 1,5 olmali
P = []
TUM = {}
for ad in MD.SIRA:
    d = MD.yukle(ad); TUM[ad] = d
    for p in d["parcalar"]:
        if p["haric"]: continue
        P.append((ad, p["grup"], p["kutle"], MD.global_nokta(ad, p["merkez"]), p["ad"]))
KP = dict(kutle_g=400.0, merkez=(0.0, 150.0, -60.0))   # taban_parcalar.KABLO_PAY (Y2a kontroluyle ayni varsayim)
cache = {}
def pl(ad, grup, poz):
    d = TUM[ad]
    if d["beklenen"] is None: return None
    k = (ad, grup, tuple(sorted(poz.items())))
    if k not in cache:
        q = d["beklenen"](poz, grup)
        cache[k] = None if q.isIdentity() else MD.global_poz(ad, q)
    return cache[k]
def am(poz_sag, poz_sol, yuk_g=0.0):
    m, mom = 0.0, V(0, 0, 0)
    for (ad, g, k, c, n) in P:
        poz = poz_sol if ad.endswith("_sol") else poz_sag
        if ad.startswith(("omuz", "dirsek")):
            q = pl(ad, g, poz)
            if q is not None: c = q.multVec(c)
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
    # ileri = one devrilme (ileri giderken fren / geri giderken hizlanma), geri = arkaya devrilme (ileri hizlanma), yan = donus
    return dict(ileri=f(ZC - C.z), geri=f(ZC + C.z), yan=f(XC - abs(C.x)))
def poz(s1, s2, dr, bl=0.0): return dict(one_arka=s1, yana=s2, dirsek=dr, bilek=bl, pan=0.0, tilt=0.0)
EV = poz(0, 5, 0)
OUT = dict(yontem="a_dev = g (d cos th - h sin th) / h; a_sinir = a_dev_min / %.1f" % PAY,
           teker_hatti=dict(x=XC, z=ZC, iz_genisligi=2 * XC), kablo_payi=KP)
m, C = am(EV, EV)
OUT["ev"] = dict(kutle_g=round(m, 1), am=[round(C.x, 2), round(C.y, 2), round(C.z, 2)],
                 duz={k: round(v, 3) for k, v in dev(C, 0).items()}, rampa5={k: round(v, 3) for k, v in dev(C, 5).items()})
print("ev", OUT["ev"], flush=True)
for yuk in (0.0, 100.0, 500.0):
    en = {}
    for s1, s2, dr in itertools.product(range(-45, 136, 15), (5, 30, 60, 90, 120), (0, 35, 70, 105)):
        if s1 >= 120 and s2 > 117: s2 = 117
        for kip in ("simetrik", "sag"):
            p_ = poz(s1, s2, dr)
            m, C = am(p_, p_ if kip == "simetrik" else EV, yuk)
            for zem, th in (("duz", 0.0), ("rampa5", 5.0)):
                for k, v in dev(C, th).items():
                    key = zem + "_" + k
                    if key not in en or v < en[key][0]:
                        en[key] = (round(v, 3), kip, (s1, s2, dr), [round(c, 2) for c in C], round(m, 1))
    sinir = {k: round(v[0] / PAY, 3) for k, v in en.items()}
    fren = {k: round(v[0] / FREN, 3) for k, v in en.items() if k.startswith("duz")}
    OUT["izgara_yuk_%dg" % int(yuk)] = dict(en_kotu=en, a_sinir_pay15=sinir,
                                            duz_a_sinir_min=round(min(v for k, v in sinir.items() if k.startswith("duz")), 3),
                                            fren_pay=dict(fren_m_s2=FREN, duz=fren, duz_min=min(fren.values()),
                                                          gecer=min(fren.values()) >= PAY))
    print("yuk", yuk, OUT["izgara_yuk_%dg" % int(yuk)], flush=True)
json.dump(OUT, open(os.path.join(HERE, "Y2b-ivme.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("yazildi Y2b-ivme.json")
