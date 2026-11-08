# F3a (P3.1, P3.2): elde yuk tablosu ve servo paylari. FreeCAD'SIZ, saf Python; yalniz okur, ciktisi yaninda F3a-yuk.json.
#
# Yontem kaynaklari (kopyalandi, degistirilmedi):
#   devrilme / fren / rampa : tasarim/freecad/lale158/kafa-yerlesim/uygulama_ivme.py (Y2b-ivme.py kopyasi)
#                             a_dev = g (d cos th - h sin th) / h; izgara S1 -45..135/15 x S2 5,30,60,90,120 x dirsek 0,35,70,105,
#                             kip simetrik / sag (sol kol ev), yuk her iki elin ucunda (arayuz.DIRSEK el_ucu), +400 g kablo payi.
#   servo torku             : tasarim/freecad/dirsek/dirsek_montaj.py bolum 5 (tork(phi, th, al, be)): S1 = g*sum(m z),
#                             S2 / dirsek / bilek eksen etrafinda (r x F).a; izgara S1/S2 5 derece, dirsek 5, bilek -90/0/90.
#   tilt / pan              : tasarim/freecad/kafa/kafa_montaj.py bolum 6 (tilt: yercekimi + I*alfa; pan: I*alfa + rulman + kablo).
# Girdi verisi (FreeCAD ciktilari, okunur):
#   tasarim/freecad/montaj/montaj-analiz.json  parcalar[] (modul, grup, kutle_g, merkez: global, sifir eklem acisi)
#   tasarim/freecad/dirsek/dirsek-analiz.json  arayuz (eksen noktalari, el_ucu), tork (dogrulama referansi)
#   tasarim/freecad/kafa/kafa-analiz.json      tork.tilt / tork.pan
#   tasarim/freecad/lale158/kafa-yerlesim/hat-secenek-{0,a,b}.json  tork_hatli / tork_hatsiz
#   tasarim/freecad/lale158/kafa-yerlesim/uygulama-ivme.json        dogrulama referansi (0 / 100 / 500 g)
# FreeCAD placement'lari (Pp, Pr, Pe, Pb, Ptilt; moduller.global_poz aynasi) burada Rodrigues donusumuyle yeniden yazildi;
# dogrulama bolumu ayni girdilerle FreeCAD ciktilarini yeniden uretir (fark F3a-yuk.json "dogrulama" altinda).
import os, sys, json, math, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FC = os.path.join(ROOT, "tasarim", "freecad")
KY = os.path.join(FC, "lale158", "kafa-yerlesim")


def jl(*p):
    return json.load(open(os.path.join(*p), encoding="utf-8"))


MON = jl(FC, "montaj", "montaj-analiz.json")
DIR = jl(FC, "dirsek", "dirsek-analiz.json")
KAF = jl(FC, "kafa", "kafa-analiz.json")
IVM = jl(KY, "uygulama-ivme.json")
HAT = {s: jl(KY, "hat-secenek-%s.json" % s) for s in "0ab"}

# ------------------------------------------------------------------ arayuz.py sabitleri (okunan degerler; satir no yorumda)
S3 = 1270.0                    # arayuz.MODULLER omuz/dirsek konum y (montaj-analiz moduller[].konum)
XR = 185.0                     # omuz_parcalar.XR (yana acma ekseni x)
D = DIR["arayuz"]
YE, ZE, XW = D["eksen_y"], D["eksen_z"], D["bilek_x"]
EL_UCU = tuple(D["el_ucu"])    # (185, -406.9, -1.25) = dirsek-analiz tork.yuk_noktasi
KANCA = tuple(DIR["tork"]["kanca_noktasi"])
X_WH, L0 = 216.0, 500.0        # arayuz._X_WH (262), L0 (15); ZC = L0/2 - 65 (uygulama_ivme.py)
XC, ZC = X_WH, L0 / 2 - 65
G = 9.81
KP = IVM["kablo_payi"]         # 400 g @ (0, 150, -60)
STALL_DS3235 = 30.4            # arayuz.py:184 servo_stall_kgcm
STALL_MG996R = 9.4             # dirsek_montaj.py STALL, kafa_montaj.py STALL (datasheet @4,8 V)
CAD = dict(s1=(-45.0, 135.0), s2=(5.0, 120.0), dirsek=(0.0, 105.0), bilek=(-90.0, 90.0), tilt=(-13.0, 13.0), pan=(-90.0, 90.0))
# kod (main:kod/jestler/kanallar.yaml, F5 / servo-10-oneri.md tablo 1 ve Ç2-Ç5): omuz 0..160, dirsek 0..110, tilt +-20, pan +-45;
# S2 ve bilek kodda yok (oneri = CAD). Bugunku tanimla kod = CAD isareti (servo-10-oneri.md "Kodun 0-180 robot acisina cevrim").
KOD = dict(s1=(0.0, 160.0), s2=(5.0, 120.0), dirsek=(0.0, 110.0), bilek=(-90.0, 90.0), tilt=(-20.0, 20.0), pan=(-45.0, 45.0))


# ------------------------------------------------------------------ kucuk vektor / donusum
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def rot(axis, deg):
    """FreeCAD App.Rotation(axis, deg) matrisi (sag el kurali)."""
    n = math.sqrt(dot(axis, axis)); x, y, z = (axis[0] / n, axis[1] / n, axis[2] / n)
    t = math.radians(deg); c, s = math.cos(t), math.sin(t); C = 1 - c
    return ((c + x * x * C, x * y * C - z * s, x * z * C + y * s),
            (y * x * C + z * s, c + y * y * C, y * z * C - x * s),
            (z * x * C - y * s, z * y * C + x * s, c + z * z * C))


def mv(R, v): return (dot(R[0], v), dot(R[1], v), dot(R[2], v))
def mm(A, B): return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)) for i in range(3))


class Pl:
    """Kati donusum p -> R p + t (FreeCAD Placement(base, rot, merkez): t = base + c - R c)."""
    def __init__(self, R=((1, 0, 0), (0, 1, 0), (0, 0, 1)), t=(0.0, 0.0, 0.0)):
        self.R, self.t = R, t

    @staticmethod
    def donme(axis, deg, merkez=(0.0, 0.0, 0.0)):
        R = rot(axis, deg)
        return Pl(R, sub(merkez, mv(R, merkez)))

    def __mul__(self, o):          # self.multiply(o): once o, sonra self
        return Pl(mm(self.R, o.R), add(mv(self.R, o.t), self.t))

    def v(self, p):
        return add(mv(self.R, p), self.t)

    def eksen(self, a):
        return mv(self.R, a)


def Pp(phi): return Pl.donme((-1, 0, 0), phi)                       # omuz_parcalar.Pp
def Pr(th): return Pl.donme((0, 0, 1), th, (XR, 0, 0))               # omuz_parcalar.Pr
def Pe(al): return Pl.donme(tuple(D["eksen_yon"]), al, (0, YE, ZE))  # dirsek_parcalar.Pe
def Pb(be): return Pl.donme(tuple(D["bilek_yon"]), be, (XW, 0, ZE))  # dirsek_parcalar.Pb


def grup_pl(modul, grup, s1, s2, dr, bl):
    """moduller.yukle_omuz / yukle_dirsek beklenen(): yerel grup donusumu (sag kol yereli)."""
    if modul.startswith("omuz"):
        if grup == "Gobek": return Pp(s1)
        if grup == "Kol": return Pp(s1) * Pr(s2)
        return None
    if grup == "UstKol": return Pp(s1) * Pr(s2)
    if grup == "OnKol": return Pp(s1) * Pr(s2) * Pe(dr)
    if grup == "El": return Pp(s1) * Pr(s2) * Pe(dr) * Pb(bl)
    return None


def g2l(p, sol): return ((-p[0]) if sol else p[0], p[1] - S3, p[2])     # yerelden_globale tersi
def l2g(p, sol): return ((-p[0]) if sol else p[0], p[1] + S3, p[2])


# ------------------------------------------------------------------ 1) devrilme (uygulama_ivme.py yontemi)
# kol parcalari grup bazinda topla (kati grup: grup ici dagilim donusumle degismez, AM toplami ayni)
SABIT_M, SABIT_MOM = 0.0, (0.0, 0.0, 0.0)
KOL = {}   # (modul, grup) -> (m, yerel merkez)
for p in MON["parcalar"]:
    m, c = p["kutle_g"], tuple(p["merkez"])
    if p["modul"].startswith(("omuz", "dirsek")) and p["grup"] in ("Gobek", "Kol", "UstKol", "OnKol", "El"):
        k = (p["modul"], p["grup"])
        m0, s0 = KOL.get(k, (0.0, (0.0, 0.0, 0.0)))
        KOL[k] = (m0 + m, add(s0, mul(g2l(c, p["modul"].endswith("_sol")), m)))
    else:
        SABIT_M += m; SABIT_MOM = add(SABIT_MOM, mul(c, m))
KOL = {k: (m, mul(s, 1.0 / m)) for k, (m, s) in KOL.items()}
SABIT_M += KP["kutle_g"]; SABIT_MOM = add(SABIT_MOM, mul(tuple(KP["merkez"]), KP["kutle_g"]))


def am(poz_sag, poz_sol, yuk_g=0.0):
    """poz = (s1, s2, dirsek, bilek). yuk_g HER IKI elin ucunda (uygulama_ivme.am ile ayni)."""
    m, mom = SABIT_M, SABIT_MOM
    for mk, c in EK:               # duyarlilik: ek sabit nokta kutle (AI HAT+); ana tabloda bos
        m += mk; mom = add(mom, mul(c, mk))
    for (mod, g), (mk, c) in KOL.items():
        sol = mod.endswith("_sol"); pz = poz_sol if sol else poz_sag
        q = grup_pl(mod, g, *pz)
        cl = q.v(c) if q is not None else c
        m += mk; mom = add(mom, mul(l2g(cl, sol), mk))
    if yuk_g:
        for sol, pz in ((False, poz_sag), (True, poz_sol)):
            e = grup_pl("dirsek", "El", *pz).v(EL_UCU)
            m += yuk_g; mom = add(mom, mul(l2g(e, sol), yuk_g))
    return m, mul(mom, 1.0 / m)


def dev(C, rampa):
    th = math.radians(rampa); h = C[1]
    f = lambda d: G * (d * math.cos(th) - h * math.sin(th)) / h
    return dict(ileri=f(ZC - C[2]), geri=f(ZC + C[2]), yan=f(XC - abs(C[0])))


EV = (0.0, 5.0, 0.0, 0.0)
PAY, FREN = 1.5, 1.8
EK = []


def izgara(yuk, s1_ust=135):
    en = {}
    s1_list = list(range(-45, 136, 15)) if s1_ust == 135 else sorted(set(range(-45, 136, 15)) | {150, 160})
    for s1, s2, dr in itertools.product(s1_list, (5, 30, 60, 90, 120), (0, 35, 70, 105)):
        if s1 >= 120 and s2 > 117: s2 = 117
        for kip in ("simetrik", "sag"):
            p_ = (s1, s2, dr, 0.0)
            m, C = am(p_, p_ if kip == "simetrik" else EV, yuk)
            for zem, th in (("duz", 0.0), ("rampa5", 5.0)):
                for k, v in dev(C, th).items():
                    key = zem + "_" + k
                    if key not in en or v < en[key][0]:
                        en[key] = (round(v, 3), kip, (s1, s2, dr), [round(c, 2) for c in C], round(m, 1))
    sinir = {k: round(v[0] / PAY, 3) for k, v in en.items()}
    fren = {k: round(v[0] / FREN, 3) for k, v in en.items() if k.startswith("duz")}
    # ek (bilgi): rampada kural "kollar ev pozunda" (karar 29.10, Y2a KZ1) -> ev pozunda yuklu rampa payi
    m, C = am(EV, EV, yuk)
    ev_r = dev(C, 5.0)
    return dict(en_kotu=en, a_sinir_pay15=sinir,
                duz_a_sinir_min=round(min(v for k, v in sinir.items() if k.startswith("duz")), 3),
                rampa5_a_sinir_min=round(min(v for k, v in sinir.items() if k.startswith("rampa5")), 3),
                fren_pay=dict(fren_m_s2=FREN, duz=fren, duz_min=min(fren.values()), gecer=min(fren.values()) >= PAY),
                ev_pozu_rampa5=dict(am=[round(c, 2) for c in C], a_dev={k: round(v, 3) for k, v in ev_r.items()},
                                    pay15={k: round(v / PAY, 3) for k, v in ev_r.items()}, pay15_min=round(min(ev_r.values()) / PAY, 3)))


# ------------------------------------------------------------------ 2) kol servo torku (dirsek_montaj.py bolum 5)
GR = {}
for g in ("Gobek", "Kol", "UstKol", "OnKol", "El"):
    mod = "omuz_sag" if g in ("Gobek", "Kol") else "dirsek_sag"
    GR[g] = KOL[(mod, g)]


def tork(phi, th, al, be):
    """Isaretli torklar (g*mm): yuksuz ve 1 g'lik el ucu yuku icin [S1, S2, dirsek, bilek]."""
    T_g = Pp(phi); T_k = Pp(phi) * Pr(th); T_o = T_k * Pe(al); T_e = T_o * Pb(be)
    pts = [("Gobek",) + (GR["Gobek"][0], T_g.v(GR["Gobek"][1])),
           ("Kol", GR["Kol"][0], T_k.v(GR["Kol"][1])),
           ("Kol", GR["UstKol"][0], T_k.v(GR["UstKol"][1])),
           ("OnKol", GR["OnKol"][0], T_o.v(GR["OnKol"][1])),
           ("El", GR["El"][0], T_e.v(GR["El"][1]))]
    ax_r = T_g.eksen((0, 0, 1)); p_r = (XR, 0, 0)
    ax_e = T_k.eksen(tuple(D["eksen_yon"])); p_e = T_k.v((0, YE, ZE))
    ax_b = T_o.eksen(tuple(D["bilek_yon"])); p_b = T_o.v((XW, 0, ZE))

    def tau(m, c, grp):
        f = (0, -m, 0)
        t1 = m * c[2]
        t2 = dot(cross(sub(c, p_r), f), ax_r) if grp in ("Kol", "OnKol", "El", "yuk") else 0.0
        t3 = dot(cross(sub(c, p_e), f), ax_e) if grp in ("OnKol", "El", "yuk") else 0.0
        t4 = dot(cross(sub(c, p_b), f), ax_b) if grp in ("El", "yukb") else 0.0
        return [t1, t2, t3, t4]
    t0 = [0.0] * 4
    for g, m, c in pts:
        t0 = [a + b for a, b in zip(t0, tau(m, c, g))]
    t1 = tau(1.0, T_e.v(EL_UCU), "yuk")
    t1[3] = tau(1.0, T_e.v(KANCA), "yukb")[3]
    return t0, t1


def izg(lo, hi, adim=5):
    lo_, hi_ = int(math.ceil(lo)), int(math.floor(hi))
    return sorted({lo_, hi_} | set(range(-(-lo_ // adim) * adim, hi_ + 1, adim)))


def tork_tablo(sinir):
    TK = []
    for phi in izg(*sinir["s1"]):
        for th in izg(*sinir["s2"]):
            for al in range(int(sinir["dirsek"][0]), int(sinir["dirsek"][1]) + 1, 5):
                for be in (-90, 0, 90):
                    t0, t1 = tork(phi, th, al, be)
                    TK.append(((phi, th, al, be), t0, t1))
    return TK


EKLEM = ["S1", "S2", "dirsek", "bilek"]
STALL = dict(S1=STALL_DS3235, S2=STALL_DS3235, dirsek=STALL_MG996R, bilek=STALL_MG996R)


def en_kotu(TK, j, m):
    best = (-1.0, None)
    for pose, t0, t1 in TK:
        t = abs(t0[j] + m * t1[j]) / 1e4
        if t > best[0]: best = (t, pose)
    return best


def izinli(TK, j, hedef_pay):
    lim = STALL[EKLEM[j]] / hedef_pay
    if en_kotu(TK, j, 0.0)[0] > lim: return 0.0
    lo, hi = 0.0, 5000.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if en_kotu(TK, j, mid)[0] <= lim: lo = mid
        else: hi = mid
    return lo


def kol_kaldirac(pose, j):
    """En kotu pozda el ucu yukunun eklem eksenine yatay kaldiraci (mm): 1 g yukun torku = kaldirac (g*mm)."""
    return abs(tork(*pose)[1][j])


# ------------------------------------------------------------------ 3) tilt / pan (kafa_montaj.py bolum 6)
YT, ZT = KAF["tork"]["tilt"]["eksen"]
ALFA = 4 * math.radians(60) / 0.4 ** 2


def tilt_statik(mK, am_, th):
    c = Pl.donme((1, 0, 0), th, (0, YT, ZT)).v(tuple(am_))       # Ptilt: tilt_yon (1,0,0), merkez (0, YT, ZT)
    return mK * (c[2] - ZT) / 1e4


def tilt_pay(t, aralik):
    st = max(abs(tilt_statik(t["kafa_grubu_g"], t["am"], th)) for th in (aralik[0], aralik[1]))
    return dict(statik_kgcm=round(st, 3), toplam_kgcm=round(st + t["ivme_kgcm"], 3), pay=round(STALL_MG996R / (st + t["ivme_kgcm"]), 2))


# pan: I_pan kafa_montaj'da tilt -13 / 0 / +13'te; kod siniri +-20 icin I(th) = A + B cos2th + C sin2th uydurulup +-20'ye uzatilir
_Ip = {float(k): v for k, v in KAF["tork"]["pan"]["I_kgm2"].items()}


def _fit3(pts):
    (a1, b1), (a2, b2), (a3, b3) = pts
    rows = [[1, math.cos(2 * math.radians(a)), math.sin(2 * math.radians(a)), b] for a, b in pts]
    # 3x3 Gauss
    for i in range(3):
        piv = max(range(i, 3), key=lambda r: abs(rows[r][i])); rows[i], rows[piv] = rows[piv], rows[i]
        for r in range(3):
            if r != i:
                f = rows[r][i] / rows[i][i]
                rows[r] = [x - f * y for x, y in zip(rows[r], rows[i])]
    return [rows[i][3] / rows[i][i] for i in range(3)]


_A, _B, _C = _fit3(sorted(_Ip.items()))
def I_pan(th): return _A + _B * math.cos(2 * math.radians(th)) + _C * math.sin(2 * math.radians(th))


def pan_pay(pan_toplam, tilt_aralik):
    """kafa_montaj: pan_t = (I_max*alfa + rulman + kablo) / 9.81 * 100; tilt araligi genisleyince yalniz I_max degisir."""
    I13 = max(_Ip.values())
    Imax = max(I_pan(th) for th in (tilt_aralik[0], 0.0, tilt_aralik[1]))
    dT = (max(Imax, I13) - I13) * ALFA / 9.81 * 100
    t = pan_toplam + dT
    return dict(I_max_kgm2=round(max(Imax, I13), 6), toplam_kgcm=round(t, 3), pay=round(STALL_MG996R / t, 2))


# ================================================================== kosu
OUT = dict(tarih="2026-11-09", paket="F3a (P3.1, P3.2)", freecad=False,
           yontem=dict(devrilme="uygulama_ivme.py: a_dev = g (d cos th - h sin th) / h; 'pay' = a_sinir_pay15 = a_dev_min / 1,5 "
                                "(K3 ve regresyon.py ile ayni anahtar; sayi ayni zamanda 1,5 m/s2 referans ivmede pay); fren pay = a_dev_min / 1,8",
                       servo="dirsek_montaj.py tork(): statik yercekimi torku, el ucu yuku (her elde) ile; pay = stall / en kotu tork",
                       kafa="kafa_montaj.py bolum 6: tilt = yercekimi(sinir) + I*alfa; pan = I_max*alfa + rulman + kablo; stall 9,4"),
           girdi=dict(montaj="tasarim/freecad/montaj/montaj-analiz.json", toplam_kutle_g=round(SABIT_M + sum(m for m, _ in KOL.values()), 2)))

# --- dogrulama A: uygulama-ivme.json (0 / 100 / 500 g)
dog = dict(ivme={}, tork={}, kafa={})
mE, CE = am(EV, EV)
dog["ivme"]["ev"] = dict(bu=dict(kutle_g=round(mE, 1), am=[round(c, 2) for c in CE]), ref=IVM["ev"])
IZ = {}
for yuk in (0, 50, 100, 200, 500):
    IZ[yuk] = izgara(float(yuk))
    print("izgara", yuk, IZ[yuk]["a_sinir_pay15"], flush=True)
en_fark = 0.0
for yuk in (0, 100, 500):
    ref = IVM["izgara_yuk_%dg" % yuk]
    satir = {}
    for k, v in ref["en_kotu"].items():
        b = IZ[yuk]["en_kotu"][k]
        fark = round(b[0] - v[0], 4)
        en_fark = max(en_fark, abs(fark), max(abs(x - y) for x, y in zip(b[3], v[3])) / 100)
        satir[k] = dict(ref=v[0], bu=b[0], fark=fark, poz_ayni=list(b[2]) == list(v[2]) and b[1] == v[1],
                        am_fark_mm=round(max(abs(x - y) for x, y in zip(b[3], v[3])), 3))
    dog["ivme"]["%dg" % yuk] = satir
dog["ivme"]["en_buyuk_fark_m_s2"] = round(en_fark, 4)

# --- servo izgaralari
TK_CAD = tork_tablo(CAD)
TK_KOD = tork_tablo(KOD)
ref_t = {r["eklem"].split(" ")[0].replace("Dirsek", "dirsek").replace("Bilek", "bilek"): r for r in DIR["tork"]["sonuc"]}
for j, e in enumerate(EKLEM):
    t0, p0 = en_kotu(TK_CAD, j, 0.0); t5, p5 = en_kotu(TK_CAD, j, 500.0)
    r = ref_t[e]
    dog["tork"][e] = dict(ref_yuksuz=r["yuksuz_kgcm"], bu_yuksuz=round(t0, 2), ref_yuklu500=r["yuklu_kgcm"], bu_yuklu500=round(t5, 2),
                          ref_poz=[r["yuksuz_poz"], r["yuklu_poz"]], bu_poz=[list(p0), list(p5)],
                          ref_izinli_2x=r["izinli_yuk_2x_g"], bu_izinli_2x=round(izinli(TK_CAD, j, 2.0), 0))
    print("tork dogrulama", e, dog["tork"][e], flush=True)

# --- kafa dogrulama: kafa-analiz pay_tilt15 / egri ve hat JSON'lari
k0 = dict(kafa_grubu_g=KAF["tork"]["tilt"]["kutle_g"], am=KAF["tork"]["tilt"]["am"], ivme_kgcm=KAF["tork"]["tilt"]["ivme_kgcm"])
dog["kafa"]["kafa_analiz_tilt15"] = dict(ref=KAF["tork"]["tilt"]["pay_tilt15"], bu=tilt_pay(k0, (-15, 15))["pay"])
dog["kafa"]["egri"] = [dict(th=e["th"], ref=e["yercekimi_kgcm"], bu=round(tilt_statik(k0["kafa_grubu_g"], k0["am"], e["th"]), 3))
                       for e in KAF["tork"]["tilt"]["egri"]]
for s in "0ab":
    for hk in ("tork_hatsiz", "tork_hatli"):
        t = HAT[s][hk]
        dog["kafa"]["%s_%s" % (s, hk)] = dict(ref=t["pay_tilt15"], bu=tilt_pay(t, (-15, 15))["pay"])
dog["kafa"]["pan_I_uydurma"] = dict(A=_A, B=_B, C=_C, kontrol={str(k): [v, round(I_pan(k), 6)] for k, v in _Ip.items()})
OUT["dogrulama"] = dog

# --- P3.1 tablo
YUKLER = (0, 50, 100, 200, 500)
tab = []
for y in YUKLER:
    z = IZ[y]
    dmin_k = min((k for k in z["a_sinir_pay15"] if k.startswith("duz")), key=lambda k: z["a_sinir_pay15"][k])
    rmin_k = min((k for k in z["a_sinir_pay15"] if k.startswith("rampa5")), key=lambda k: z["a_sinir_pay15"][k])
    satir = dict(yuk_g_her_elde=y, toplam_yuk_g=2 * y,
                 duz_devrilme=dict(pay=z["a_sinir_pay15"][dmin_k], anahtar=dmin_k, poz=z["en_kotu"][dmin_k][2], kip=z["en_kotu"][dmin_k][1]),
                 fren18=dict(pay=z["fren_pay"]["duz_min"], anahtar=min(z["fren_pay"]["duz"], key=z["fren_pay"]["duz"].get)),
                 rampa5=dict(pay=z["a_sinir_pay15"][rmin_k], anahtar=rmin_k, poz=z["en_kotu"][rmin_k][2], kip=z["en_kotu"][rmin_k][1]),
                 rampa5_ev_pozu=z["ev_pozu_rampa5"]["pay15_min"], servo={})
    for j, e in enumerate(EKLEM):
        t, p = en_kotu(TK_CAD, j, float(y))
        satir["servo"][e] = dict(tork_kgcm=round(t, 2), pay=round(STALL[e] / t, 2), poz=list(p), kaldirac_mm=round(kol_kaldirac(p, j), 1))
    tab.append(satir)
OUT["P3_1"] = dict(tablo=tab, izgara={str(y): IZ[y] for y in YUKLER})

# yuk siniri taramasi (her elde, 10 g adim): her olcutun gectigi en buyuk yuk
def sinir_ara():
    s = {}
    for j, e in enumerate(EKLEM):
        s["servo_%s_pay1" % e] = round(izinli(TK_CAD, j, 1.0), 0)
        s["servo_%s_pay2" % e] = round(izinli(TK_CAD, j, 2.0), 0)
        s["servo_%s_pay1_kod" % e] = round(izinli(TK_KOD, j, 1.0), 0)
    for ad, f in (("duz_devrilme_1_5", lambda z: min(v for k, v in z["a_sinir_pay15"].items() if k.startswith("duz")) >= 1.5),
                  ("fren18_1_5", lambda z: z["fren_pay"]["duz_min"] >= 1.5),
                  ("rampa5_izgara_1_5", lambda z: z["rampa5_a_sinir_min"] >= 1.5),
                  ("rampa5_ev_pozu_1_5", lambda z: z["ev_pozu_rampa5"]["pay15_min"] >= 1.5)):
        son = None
        for y in range(0, 1001, 10):
            z = IZ[y] if y in IZ else izgara(float(y))
            if y not in IZ and y % 50 == 0: IZ[y] = z
            if f(z): son = y
            else: break
        s[ad] = son
    return s
OUT["P3_1"]["sinir_her_elde_g"] = sinir_ara()
print("sinir", OUT["P3_1"]["sinir_her_elde_g"], flush=True)

# --- P3.2 servo paylari (yuksuz + 100 g; CAD ve kod siniri)
p32 = {}
for j, e in enumerate(EKLEM):
    satir = {}
    for ad, TK in (("cad", TK_CAD), ("kod", TK_KOD)):
        for y in (0.0, 100.0, 500.0):
            t, p = en_kotu(TK, j, y)
            satir["%s_%dg" % (ad, y)] = dict(tork_kgcm=round(t, 2), pay=round(STALL[e] / t, 2), poz=list(p))
    p32[e] = dict(servo="DS3235" if e in ("S1", "S2") else "MG996R", stall_kgcm=STALL[e], **satir)
kafa = {}
for ad, src in (("bugunku_model", dict(kafa_grubu_g=KAF["tork"]["tilt"]["kutle_g"], am=KAF["tork"]["tilt"]["am"],
                                       ivme_kgcm=KAF["tork"]["tilt"]["ivme_kgcm"], pan_toplam_kgcm=KAF["tork"]["pan"]["toplam_kgcm"])),
                ("K2a_hatli", HAT["a"]["tork_hatli"]), ("K2b_hatli", HAT["b"]["tork_hatli"]), ("K2_0_hatli", HAT["0"]["tork_hatli"])):
    kafa[ad] = dict(kaynak=ad, kutle_g=src["kafa_grubu_g"],
                    tilt_cad13=tilt_pay(src, CAD["tilt"]), tilt_15=tilt_pay(src, (-15, 15)), tilt_kod20=tilt_pay(src, KOD["tilt"]),
                    pan_cad=pan_pay(src["pan_toplam_kgcm"], CAD["tilt"]), pan_kod=pan_pay(src["pan_toplam_kgcm"], KOD["tilt"]))
p32["kafa"] = kafa
OUT["P3_2"] = p32

# --- duyarlilik: AI HAT+ (K2) ana modelde yok; hat-secenek JSON'larindaki kafa grubu kutle/AM farki nokta kutle olarak eklenir
#     (taban: secenek 0 HAT'siz = bugunku model; kafa modul konumu montaj-analiz moduller[kafa].konum)
KAFA_KONUM = [x for x in MON["moduller"] if x["ad"] == "kafa"][0]["konum"]
h0 = HAT["0"]["tork_hatsiz"]
hat_d = {}
for s in "ab":
    h1 = HAT[s]["tork_hatli"]
    dm = h1["kafa_grubu_g"] - h0["kafa_grubu_g"]
    c = mul(sub(mul(tuple(h1["am"]), h1["kafa_grubu_g"]), mul(tuple(h0["am"]), h0["kafa_grubu_g"])), 1.0 / dm)
    cg = add(c, tuple(KAFA_KONUM))
    EK = [(dm, cg)]
    r = {}
    for y in (0, 100):
        z = izgara(float(y))
        r["%dg" % y] = dict(duz_min=z["duz_a_sinir_min"], fren_min=z["fren_pay"]["duz_min"], rampa5_min=z["rampa5_a_sinir_min"],
                            rampa5_ev_pozu=z["ev_pozu_rampa5"]["pay15_min"])
    EK = []
    hat_d["K2" + s] = dict(ek_kutle_g=round(dm, 1), ek_nokta_global=[round(v, 1) for v in cg], **r)
OUT["duyarlilik_AI_HAT"] = hat_d
print("HAT", hat_d, flush=True)

# --- yan bilgi: kod siniri S1 0..160 ile devrilme (izgaraya 150, 160 eklenir); brief disi, yalniz not
OUT["not_kod_s1_160_devrilme"] = {str(y): dict(duz_min=izgara(float(y), 160)["duz_a_sinir_min"],
                                               rampa5_min=izgara(float(y), 160)["rampa5_a_sinir_min"]) for y in (0, 100)}

json.dump(OUT, open(os.path.join(HERE, "F3a-yuk.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("yazildi F3a-yuk.json")
