# Lale 1,70 m TASLAK - devrilme, taban motoru, servo torku, kol orani hesabi (sistem Python'u, FreeCAD gerekmez)
# Analiz ajani (21 Ekim 2026). Girdi: analiz/girdi-<robot>-<W>.json (taslak_analiz.py 'kutle' bolumu: grup kutle / AM / atalet
# tensoru, eklem eksenleri). Yontemler mevcut projedekiyle AYNI (karsilastirilabilir):
#   devrilme  taban/taban_montaj.py denge(): esik = g (d cos t - h sin t) / h, temas teker merkez duzlemleri (x +-178(+DX), z +-185),
#             pay = esik / 1,5 m/s2 (acil stop freni, tahmini); kol pozlari ayni liste + tum izgara taramasi
#   motor     taban_montaj.py tork(): F = m (a + g sin t + Crr g cos t), 4 motor, r 62,5; surekli = durma x 0,30 (6,3 kg cm)
#             yerinde donus taban/donus_hesap.py (Coulomb modeli + ust sinir), teker duzlemi genislige gore
#   servo     dirsek/dirsek_montaj.py tork(): yercekimi torku S1 x S2 x dirsek x bilek izgarasinda (5 derece), pay = stall / tork;
#             kafa kafa/kafa_montaj.py: tilt = yercekimi (+25 g kablo) + I alfa, pan = I alfa + rulman + kablo, alfa 26,2 rad/s2
#             (60 derece 0,4 s'de ucgen profil, tahmini). Kollara ayni alfa ile ivme torku ek bilgi olarak.
#   kol orani x1,00 / x1,15 / x1,25 / x1,36. Kontrol ajani (24 Ekim 2026, karar Duffy: x1,25 + omuz DS3235): taslak geometrisi TASLAK_KOL
#             secimine gore (girdi ile tutarlilik assert'li). '125': x1,25 taslak geometrisi (ek on kolda); x1,15 = on kol uzatmasi geri alinir,
#             x1,36 = ek boy yine on kola (dogrusal); omuz stall'i servo geriliminde (OMUZ_SERVO_VERI, kol-analiz modeli). '115' + DS3218MG:
#             eski yol (ek boy tup:yaka 30:19, stall 20) -> ayni girdiyle eski hesap.json bayt bayt ayni cikar (regresyon, 24 Ekim 2026).
#             Regresyon: TASLAK_KOL=115 TASLAK_OMUZ_SERVO=DS3218MG TASLAK_HESAP_AN=<eski girdi klasoru> python taslak_hesap.py
# Cikti: analiz/hesap.json
import os, sys, json, math, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "taban")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A
import taslak_ayar as TA
import donus_hesap as DH

G = 9.81
FREN = 1.5
ALFA = 4 * math.radians(60) / 0.4 ** 2           # kafa_montaj.py ile ayni profil
STALL_DS, STALL_MG = 20.0, 9.4                  # DS3218MG (omuz raporu), MG996R @4,8 V (datasheet)
AN = os.environ.get("TASLAK_HESAP_AN", os.path.join(HERE, "analiz"))     # girdi/cikti klasoru (regresyon icin degistirilebilir)

# Omuz servosu verisi (kontrol ajani, 24 Ekim 2026; karar Duffy 24 Ekim: S1/S2 DS3235). Veri kol-analiz/NOTLAR.md "1) Servo verisi":
#   DS3218MG: proje degeri 20 kg*cm sabit (125 cm ve x1,15 hesaplari bununla; birebir korunur).
#   DS3235  : 29 / 32 / 35 kg*cm @5 / 6 / 7,4 V (Robocombo tablosu + datasheet), 60 g; stall akimi tasarimda 3,0 A @6 V (tahmini, ihtiyatli).
#             Stall, servonun S1 kalkisinda gordugu gerilimde (kol-analiz/kol_analiz.py ile ayni model): hat 6,0 V - 16 AWG ana hat
#             (8 mOhm x gercekci tepe akim, en cok 8 A) - S1/S2 uzatmasi 22 AWG (0,0529 Ohm/m x 1,45 m, gidis-donus, iki omuz servosu stall akimi).
#   MG996R  : 9,4 kg*cm @4,8 V (proje degeri, STALL_MG); hat akimi icin 11 kg*cm / 2,5 A @6 V (datasheet).
OMUZ_SERVO_VERI = {
    "DS3218MG": dict(stall_sabit=STALL_DS, kaynak="omuz raporu / proje degeri (6 V civari, tahmini)"),
    "DS3235": dict(tork=[(5.0, 29.0), (6.0, 32.0), (7.4, 35.0)], akim=[(5.0, 1.9), (6.0, 2.1), (7.4, 2.3)], akim_tasarim_6v=3.0,
                   kaynak="Robocombo DS3235 tablosu (29/32/35 kg*cm @5/6/7,4 V) + DS3235 datasheet (Rochester ME240 kopyasi); stall akimi "
                          "tasarimda 3,0 A @6 V (tahmini); kol-analiz/NOTLAR.md"),
}
MG_HAT = dict(tork=[(4.8, 9.4), (6.0, 11.0)], akim=[(4.8, 2.0), (6.0, 2.5)])
HAT = dict(v_set=6.0, R_ana=0.008, r_22awg=0.0529, xl_tepe=8.0, uzatma_S1_m=1.45, I_bilek=0.4, I_pan=0.6, I0=0.15,
           kaynak="planlama/adim3/elektrik.md E1 + kol-analiz/kol_analiz.py HAT (ayni model)")


def interp(pts, v):
    xs, ys = zip(*pts)
    if v <= xs[0]:
        return ys[0] + (ys[1] - ys[0]) * (v - xs[0]) / (xs[1] - xs[0])
    for i in range(len(xs) - 1):
        if v <= xs[i + 1]:
            return ys[i] + (ys[i + 1] - ys[i]) * (v - xs[i]) / (xs[i + 1] - xs[i])
    return ys[-2] + (ys[-1] - ys[-2]) * (v - xs[-2]) / (xs[-1] - xs[-2])


def omuz_stall(ad, T_dirsek_kgcm=0.0):
    """Omuz servosunun stall torku (kg*cm) ve hesaplandigi servo gerilimi (V; sabit degerde None).
    T_dirsek_kgcm: dirsek statik + ivme torku (gercekci tepe akimdaki dirsek payi icin, kol-analiz modeli)."""
    s = OMUZ_SERVO_VERI[ad]
    if "stall_sabit" in s:
        return s["stall_sabit"], None
    I_st = s["akim_tasarim_6v"] * interp(s["akim"], HAT["v_set"]) / interp(s["akim"], 6.0)
    Ts_mg, Is_mg = interp(MG_HAT["tork"], HAT["v_set"]), interp(MG_HAT["akim"], HAT["v_set"])
    I_d = min(Is_mg, HAT["I0"] + (Is_mg - HAT["I0"]) * max(T_dirsek_kgcm, 0.0) / Ts_mg)
    tepe = I_st * 2 + I_d + HAT["I_bilek"] + HAT["I_pan"]
    v = HAT["v_set"] - min(tepe, HAT["xl_tepe"]) * HAT["R_ana"] - I_st * 2 * HAT["r_22awg"] * HAT["uzatma_S1_m"]
    return interp(s["tork"], v), v


def oku(ad):
    return json.load(open(os.path.join(AN, ad), encoding="utf-8"))


def rodrigues(u, a):
    u = np.asarray(u, float)
    u = u / np.linalg.norm(u)
    c, s = math.cos(a), math.sin(a)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K


def rot(ax, deg):
    M = np.eye(4)
    if abs(deg) < 1e-12:
        return M
    R = rodrigues(ax["u"], math.radians(deg))
    n = np.asarray(ax["n"], float)
    M[:3, :3] = R
    M[:3, 3] = n - R @ n
    return M


def tp(M, p):
    return M[:3, :3] @ np.asarray(p, float) + M[:3, 3]


class Robot:
    def __init__(self, gd, ad, paylar):
        self.ad = ad
        self.g = {k: dict(m=v["m"], c=np.array(v["c"]), cs=np.array(v["c_sekil"]), I=np.array(v["I"])) for k, v in gd["gruplar"].items()}
        self.ax = gd["eksen"]
        self.paylar = paylar                                          # [(m, (x, y, z))]
        self.xc, self.zc = gd["destek_x"], gd["destek_z"]
        self.tw = gd["taban_w"]
        self.I_top = np.array(gd["toplam"]["I"])
        self.ozel = gd["ozel_parca"]
        self.alt = gd.get("alt_kume", {})                             # bilek servosu alt kumesi (OnKol icinde), on kol varyantlari icin
        s3 = self.ax["omuz_sag|one_arka"]["n"][1]
        self.s3 = s3
        if ad.startswith("yeni"):
            # girdi (taslak_analiz.py kutle) ile taslak_ayar kol secimi ayni geometri mi? (ornek: TASLAK_KOL=125 iken x1,15 girdisi)
            on = (self.ax["dirsek_sag|dirsek"]["n"][1] - self.ax["dirsek_sag|bilek"]["n"][1]) - (A.DIRSEK["eksen_y"] - A.DIRSEK["bilek_nokta"][1])
            assert abs(on - TA.ON_KOL_UZAMA) < 0.05, ("girdi on kol uzamasi %.2f mm, taslak_ayar (TASLAK_KOL=%s) %.2f mm: taslak_analiz.py "
                                                     "kutle bolumu bu kol secimiyle yeniden kosulmali" % (on, TA.KOL_SECIM, TA.ON_KOL_UZAMA))
        L = TA.KOL_BOY_YENI if ad.startswith("yeni") else TA.KOL_BOY_ESKI
        self.kol_boy = L
        uz = (TA.KOL_BOY_YENI - TA.KOL_BOY_ESKI) if ad.startswith("yeni") else 0.0     # tup + on kol + yaka (taslak_ayar)
        self.uc = np.array([A.DIRSEK["el_ucu"][0], s3 + A.DIRSEK["el_ucu"][1] - uz, A.DIRSEK["el_ucu"][2]])

    # ---- kol zinciri
    def kol_M(self, taraf, sp):
        phi, th, al, be = (list(sp) + [0.0] * 4)[:4]
        a = self.ax
        M1 = rot(a["omuz_%s|one_arka" % taraf], phi)
        M2 = M1 @ rot(a["omuz_%s|yana" % taraf], th)
        M3 = M2 @ rot(a["dirsek_%s|dirsek" % taraf], al)
        M4 = M3 @ rot(a["dirsek_%s|bilek" % taraf], be)
        return {"Gobek": M1, "Kol": M2, "UstKol": M2, "OnKol": M3, "El": M4}, (M1, M2, M3)

    def grup_mod(self, k):
        m, g = k.split("|")
        return m, g

    def kutle_am(self, poz=None, yuk=0.0):
        """Toplam kutle ve AM; poz = dict(sag=(phi, th, al, be), sol=...). yuk: her elde g."""
        poz = poz or {}
        M, mc = 0.0, np.zeros(3)
        Ms = {t: self.kol_M(t, poz.get(t, (0, 0, 0, 0)))[0] for t in ("sag", "sol")}
        for k, g in self.g.items():
            m, gr = self.grup_mod(k)
            c = g["c"]
            if m.startswith(("omuz_", "dirsek_")) and gr != "Govde":
                c = tp(Ms[m.split("_")[1]][gr], c)
            M += g["m"]
            mc += g["m"] * c
        for m, c in self.paylar:
            M += m
            mc += m * np.asarray(c, float)
        if yuk:
            for t in ("sag", "sol"):
                u = self.uc * (np.array([1, 1, 1]) if t == "sag" else np.array([-1, 1, 1]))
                M += yuk
                mc += yuk * tp(Ms[t]["El"], u)
        return M, mc / M

    def denge(self, M, C, rampa=0.0):
        th = math.radians(rampa)
        dF, dR, dS = self.zc - C[2], self.zc + C[2], self.xc - abs(C[0])
        h = C[1]
        f = lambda d: G * (d * math.cos(th) - h * math.sin(th)) / h
        return dict(ileri=round(f(dF), 2), geri=round(f(dR), 2), yan=round(f(dS), 2),
                    pay_ileri=round(f(dF) / FREN, 2), pay_geri=round(f(dR) / FREN, 2), pay_yan=round(f(dS) / FREN, 2),
                    egim_ileri=round(math.degrees(math.atan2(dF, h)), 1), egim_geri=round(math.degrees(math.atan2(dR, h)), 1),
                    egim_yan=round(math.degrees(math.atan2(dS, h)), 1), dF=round(dF, 1), dR=round(dR, 1), dS=round(dS, 1), h=round(h, 1))


POZLAR = [("ev", "Ev pozu (kollar aşağıda)", (0, 0, 0, 0), (0, 0, 0, 0), 0.0),
          ("one", "İki kol öne uzanmış (S1 90, düz)", (90, 5, 0, 0), (90, 5, 0, 0), 0.0),
          ("one_yuk", "İki kol öne uzanmış + her elde 0,5 kg (bilgi)", (90, 5, 0, 0), (90, 5, 0, 0), 500.0),
          ("one_yukari", "İki kol öne-yukarı (S1 135)", (135, 5, 0, 0), (135, 5, 0, 0), 0.0),
          ("geri", "İki kol geride (S1 −45)", (-45, 5, 0, 0), (-45, 5, 0, 0), 0.0),
          ("yan_tek", "Sağ kol yana açık (S2 90), sol aşağıda", (0, 90, 0, 0), (0, 0, 0, 0), 0.0),
          ("yan_cift", "İki kol yana açık (S2 90)", (0, 90, 0, 0), (0, 90, 0, 0), 0.0)]


def devrilme(rb):
    satir = []
    for kod, ad, ps, pl, yk in POZLAR:
        M, C = rb.kutle_am(dict(sag=ps, sol=pl), yk)
        satir.append(dict(kod=kod, ad=ad, kutle_g=round(M, 1), am=[round(x, 1) for x in C], duz=rb.denge(M, C, 0.0), rampa5=rb.denge(M, C, 5.0)))
    # izgara: iki kol ayni poz, tek kol, zit (yuksuz)
    PH = list(range(-45, 136, 15))
    TH = [5, 15, 30, 45, 60, 75, 90, 105, 120]
    AL = [0, 30, 60, 90, 105]
    en = {}
    for phi in PH:
        for th in TH:
            for al in AL:
                for tip, ps, pl in (("simetrik", (phi, th, al, 0), (phi, th, al, 0)), ("tek", (phi, th, al, 0), (0, 0, 0, 0)),
                                    ("zit", (phi, th, al, 0), (90 - phi, 5, 0, 0))):
                    M, C = rb.kutle_am(dict(sag=ps, sol=pl))
                    for rampa in (0.0, 5.0):
                        d = rb.denge(M, C, rampa)
                        for yon in ("ileri", "geri", "yan"):
                            k = (rampa, yon)
                            if d["pay_" + yon] < en.get(k, (1e9,))[0]:
                                en[k] = (d["pay_" + yon], dict(tip=tip, sag=list(ps), sol=list(pl), esik=d[yon], pay=d["pay_" + yon],
                                                               am=[round(x, 1) for x in C]))
    izgara = {("duz" if r == 0 else "rampa5") + "_" + y: v[1] for (r, y), v in en.items()}
    return dict(pozlar=satir, izgara_en_kotu=izgara,
                ev=satir[0], en_kucuk_pay_duz=round(min(min(s["duz"]["pay_ileri"], s["duz"]["pay_geri"], s["duz"]["pay_yan"]) for s in satir if not s["kod"].endswith("yuk")), 2),
                en_kucuk_pay_rampa=round(min(min(s["rampa5"]["pay_ileri"], s["rampa5"]["pay_geri"], s["rampa5"]["pay_yan"]) for s in satir if not s["kod"].endswith("yuk")), 2),
                izgara_en_kucuk_duz=round(min(v["pay"] for k, v in izgara.items() if k.startswith("duz")), 2),
                izgara_en_kucuk_rampa=round(min(v["pay"] for k, v in izgara.items() if k.startswith("rampa")), 2))


# ====================================================================== motor
MOT = DH.motor_degerleri()
R_T = A.TEKER_D / 2 / 1000.0


def tork(m_kg, rampa, a=0.5, crr=0.03, surekli=None):
    surekli = surekli or MOT["surekli_kgcm"]
    th = math.radians(rampa)
    F = m_kg * (a + G * math.sin(th) + crr * G * math.cos(th))
    T = F * R_T / 4 * 10.197
    return dict(rampa=rampa, a=a, F_N=round(F, 1), T_kgcm=round(T, 2), oran=round(T / surekli, 3))


def a_sinir(m_kg, rampa, oran, surekli=None):
    surekli = surekli or MOT["surekli_kgcm"]
    th = math.radians(rampa)
    F = oran * surekli / 10.197 * 4 / R_T
    return round(F / m_kg - G * math.sin(th) - 0.03 * G * math.cos(th), 3)


def motor(rb, Mg, C):
    m = Mg / 1000.0
    out = dict(kutle_kg=round(m, 3), duz=tork(m, 0.0), rampa5=tork(m, 5.0), rampa5_yavas=tork(m, 5.0, a=0.25), rampa5_durus=tork(m, 5.0, a=0.0),
               rampa5_yuk2=tork(m + 2.0, 5.0), a_sinir_rampa5_80=a_sinir(m, 5.0, 0.80), a_sinir_rampa5_77=a_sinir(m, 5.0, 0.77),
               a_sinir_duz_80=a_sinir(m, 0.0, 0.80), surekli_kgcm=MOT["surekli_kgcm"], stall_kgcm=MOT["stall_kgcm"])
    # 9 kg cm durma senaryosu (K3/T2 uyarisi): surekli 2,7
    out["stall9"] = dict(duz=tork(m, 0.0, surekli=2.7), rampa5_yavas=tork(m, 5.0, a=0.25, surekli=2.7), rampa5_durus=tork(m, 5.0, a=0.0, surekli=2.7))
    dF, dR = rb.zc - C[2], rb.zc + C[2]
    out["aks"] = dict(on_N=round(m * G * dR / (dF + dR), 1), arka_N=round(m * G * dF / (dF + dR), 1),
                      mu_gereken_rampa5=round(out["rampa5"]["F_N"] / (m * G * math.cos(math.radians(5))), 3))
    # yerinde donus: donus_hesap (teker duzlemi genislige gore)
    DH.X_W = DH.X_OMNI = rb.xc / 1000.0
    am = [float(C[0]), float(C[1]), float(C[2])]
    yer = []
    for mu in (0.4, 0.5, 0.6):
        a_ = DH.model_a(m, am, mu, -1.0, False)
        o_ = DH.model_a(m, am, mu, -1.0, True)
        b_ = DH.model_b(m, am, mu, 0.0)
        yer.append(dict(mu=mu, standart_kgcm=a_["en_cok_kgcm"], standart_oran=a_["en_cok_oran_surekli"], standart_stall=a_["en_cok_oran_stall"],
                        akim_A=a_["en_cok_akim_A"], ust_sinir_kgcm=b_["en_cok_kgcm"], ust_sinir_stall=b_["oran_stall"],
                        omni_kgcm=o_["en_cok_kgcm"], omni_oran=o_["en_cok_oran_surekli"]))
    DH.X_W = DH.X_OMNI = 0.178
    # yaw ivmesi payi: kutu formulu (donus_hesap) ve parcalardan gercek I_y
    Iz_kutu = m * (0.444 ** 2 + 0.525 ** 2) / 12.0
    Iy = rb.I_top[1][1] * 1e-9                                     # g mm2 -> kg m2 (dikey eksen, AM'den)
    # kablo paylari nokta kutle olarak (AM'ye gore)
    for mp, cp in rb.paylar:
        d = np.asarray(cp, float) - C
        Iy += mp / 1000.0 * (d[0] ** 2 + d[2] ** 2) * 1e-6
    x_w = rb.xc / 1000.0
    yaw = dict(Iy_parca_kgm2=round(Iy, 4), Iz_kutu_kgm2=round(Iz_kutu, 4), yaw_ivme=A.TABAN["donus"]["yaw_ivme"],
               ivme_payi_kgcm=round(Iy * A.TABAN["donus"]["yaw_ivme"] / (4 * x_w) * R_T * 10.197, 3),
               ivme_payi_kutu_kgcm=round(Iz_kutu * A.TABAN["donus"]["yaw_ivme"] / (4 * x_w) * R_T * 10.197, 3))
    out["yerinde_donus"] = yer
    out["yaw"] = yaw
    return out


# ====================================================================== servolar
def eksen_torku(r, m, a, u):
    """Yercekimi (0, -m, 0) g; torkun eksene izdusumu, g mm."""
    return float(np.cross(np.asarray(r) - a, np.array([0.0, -m, 0.0])) @ u)


def pm(m, r):
    """Nokta kutle ataleti (orijine gore), g mm2."""
    r = np.asarray(r, float)
    return m * (np.dot(r, r) * np.eye(3) - np.outer(r, r))


# On kol uzatmasi (KOL_SECENEK 125: ek on kola). Uzatilan bolum alt U kesiti (3 mm yan duvarlar + on duvar, 339,3 mm2; CAD dilimi,
# kontrol ajani 24 Ekim 2026): agirlik merkezi x 195,15 (bilek servosu govde ekseni), z 5,06 (global, sag kol). Kesit dirsek ekseninden
# s = TA.ON_KOL_KES_S'te basliyor; bilek servosu alt kumesi (OnKol grubunda) + El grubu + bilek ekseni uzamayla asagi kayar.
ON_KOL_U_XZ = (195.15, 5.06)


def on_kol_ek(rb, rb_e, d):
    """On kol uzamasini d mm degistiren varyant (rb geometrisine gore; d < 0 kisaltir). Birim kutle taslak uzatmasindan (rb_e: 125 cm)."""
    mu = (rb.ozel["dirsek_sag|On kol govdesi"]["kutle"] - rb_e.ozel["dirsek_sag|On kol govdesi"]["kutle"]) / TA.ON_KOL_UZAMA
    y_dir = rb.ax["dirsek_sag|dirsek"]["n"][1]
    y_seg = y_dir - TA.ON_KOL_KES_S - TA.ON_KOL_UZAMA - d / 2.0             # eklenen / cikarilan bolumun ortasi
    return dict(tip="on_kol", d=d, mu_on=mu, m_on=mu * d, y_on=y_seg, x_on=ON_KOL_U_XZ[0], z_on=ON_KOL_U_XZ[1])


def on_kol_uygula(gr, ax, alt, taraf, ek):
    """gr: {grup: [m, c, cs, I]} (yerinde degisir); ax: {anahtar: dict(n, u)} (yerinde); alt: girdi alt_kume. Kayma vektoru doner."""
    d = ek["d"]
    dv = np.array([0.0, -d, 0.0])
    sx = 1.0 if taraf == "sag" else -1.0
    # kayan alt kumeler: bilek servosu (+ mil, 4 M4 + somun) ve on kol govdesinin uzatmanin altindaki bolumu (taslak_analiz.py kutle)
    kay = [alt["dirsek_%s|OnKol|%s" % (taraf, k)] for k in ("bilek_ile", "on_kol_alt")]
    m0, c0, cs0, I0 = gr["OnKol"]
    ms = ek["m_on"]
    cseg = np.array([sx * ek["x_on"], ek["y_on"], ek["z_on"]])
    m1 = m0 + ms
    mk = sum(a["m"] for a in kay)
    c1 = (m0 * c0 + mk * dv + ms * cseg) / m1
    cs1 = (m0 * cs0 + mk * dv + ms * cseg) / m1
    IO = I0 + pm(m0, cs0) + pm(ms, cseg)                                     # bolum nokta kutle
    for a in kay:                                                            # alt kumeler otelenir (kendi ataletleri ayni)
        csb = np.array(a["c_sekil"], float)
        IO = IO - pm(a["m"], csb) + pm(a["m"], csb + dv)
    gr["OnKol"] = [m1, c1, cs1, IO - pm(m1, cs1)]
    m0, c0, cs0, I0 = gr["El"]
    gr["El"] = [m0, c0 + dv, cs0 + dv, I0]                                   # oteleme: sekil merkezine gore atalet degismez
    k = "dirsek_%s|bilek" % taraf
    ax[k] = dict(n=np.asarray(ax[k]["n"], float) + dv, u=ax[k]["u"])
    return dv


def kol_gruplari(rb, taraf="sag", ek=None):
    """Kol gruplari, eksenler, el ucu ve kanca (ev pozu); ek: kol orani varyanti (tup_yaka: x1,15 yontemi; on_kol: x1,25 yontemi)."""
    gr = {}
    for g in ("Gobek", "Kol", "UstKol", "OnKol", "El"):
        k = ("omuz_%s|%s" if g in ("Gobek", "Kol") else "dirsek_%s|%s") % (taraf, g)
        d = rb.g[k]
        gr[g] = [d["m"], d["c"].copy(), d["cs"].copy(), d["I"].copy()]
    ax = {k: dict(n=np.array(v["n"], float), u=np.array(v["u"], float)) for k, v in rb.ax.items()}
    uc = rb.uc.copy()
    kanca = rb.uc + np.array([172.0 - 185.0, 20.0, 0.0])                      # dirsek_parcalar YUK_KANCA - YUK_UC (172; -305,5 vs -325,5)
    if ek and ek.get("tip", "tup_yaka") == "tup_yaka":
        dyD, dyE = ek["dy_dirsek"], ek["dy_el"]
        for g in ("UstKol", "OnKol", "El"):
            gr[g][1][1] -= dyD
            gr[g][2][1] -= dyD
        gr["El"][1][1] -= dyE
        gr["El"][2][1] -= dyE
        # ek tup kutlesi (Kol grubu), ek yaka kutlesi (El grubu)
        for g, mk, yk in (("Kol", ek["m_tup"], ek["y_tup"]), ("El", ek["m_el"], ek["y_el"])):
            m0, c0, cs0, I0 = gr[g]
            c_ek = np.array([c0[0], yk, c0[2]])
            m1 = m0 + mk
            gr[g] = [m1, (m0 * c0 + mk * c_ek) / m1, (m0 * cs0 + mk * c_ek) / m1, I0]
        for k in ("dirsek_%s|dirsek" % taraf, "dirsek_%s|bilek" % taraf):
            ax[k] = dict(n=ax[k]["n"] - np.array([0, dyD, 0]), u=ax[k]["u"])
        uc = uc - np.array([0, dyD + dyE, 0])
        kanca = kanca - np.array([0, dyD + dyE, 0])
    elif ek:
        dv = on_kol_uygula(gr, ax, rb.alt, taraf, ek)
        uc = uc + dv
        kanca = kanca + dv
    return gr, ax, uc, kanca


def kol_servo(rb, taraf="sag", kanca=None, ek=None, omuz=None):
    """ek: kol orani varyanti (kol_gruplari). omuz: omuz servosu (varsayilan 125 cm robotta DS3218MG, taslakta taslak_ayar.OMUZ_SERVO)."""
    omuz = omuz or ("DS3218MG" if rb.ad.startswith("eski") else TA.OMUZ_SERVO["ad"])
    gr, ax, uc, kanca = kol_gruplari(rb, taraf, ek)
    a = {k: dict(n=list(v["n"]), u=list(v["u"])) for k, v in ax.items()}

    def M_al(sp):
        phi, th, al, be = sp
        M1 = rot(a["omuz_%s|one_arka" % taraf], phi)
        M2 = M1 @ rot(a["omuz_%s|yana" % taraf], th)
        M3 = M2 @ rot(a["dirsek_%s|dirsek" % taraf], al)
        M4 = M3 @ rot(a["dirsek_%s|bilek" % taraf], be)
        return M1, M2, M3, M4

    eks = [("S1 (omuz öne-arka)", "omuz_%s|one_arka" % taraf, 0, ("Gobek", "Kol", "UstKol", "OnKol", "El"), None, omuz),
           ("S2 (omuz yana açma)", "omuz_%s|yana" % taraf, 1, ("Kol", "UstKol", "OnKol", "El"), None, omuz),
           ("Dirsek", "dirsek_%s|dirsek" % taraf, 2, ("OnKol", "El"), STALL_MG, "MG996R"),
           ("Bilek", "dirsek_%s|bilek" % taraf, 3, ("El",), STALL_MG, "MG996R")]
    PH = sorted(set(list(range(-45, 136, 5)) + [135]))
    TH = sorted(set([5] + list(range(10, 121, 5))))
    AL = list(range(0, 106, 5))
    BE = [-90, 0, 90]
    en0 = [(-1, None)] * 4
    en1 = [(-1, None)] * 4
    kayit = {}
    for phi in PH:
        for th in TH:
            for al in AL:
                for be in BE:
                    Ms = M_al((phi, th, al, be))
                    T = {"Gobek": Ms[0], "Kol": Ms[1], "UstKol": Ms[1], "OnKol": Ms[2], "El": Ms[3]}
                    for j, (ad, key, lvl, gl, st, sv) in enumerate(eks):
                        Mp = np.eye(4) if lvl == 0 else Ms[lvl - 1]
                        ap, up = tp(Mp, ax[key]["n"]), Mp[:3, :3] @ ax[key]["u"]
                        t0 = sum(eksen_torku(tp(T[g], gr[g][1]), gr[g][0], ap, up) for g in gl)
                        if j < 3:
                            t1 = eksen_torku(tp(Ms[3], uc), 1.0, ap, up)
                        else:
                            t1 = eksen_torku(tp(Ms[3], kanca), 1.0, ap, up)
                        kayit[(j, phi, th, al, be)] = (t0, t1)
                        if abs(t0) > en0[j][0]:
                            en0[j] = (abs(t0), (phi, th, al, be))
                        tt = abs(t0 + 500.0 * t1)
                        if tt > en1[j][0]:
                            en1[j] = (tt, (phi, th, al, be))
    # 1) her eksende en kotu statik poz + ivme torku
    ara = []
    for j, (ad, key, lvl, gl, st, sv) in enumerate(eks):
        t_yuksuz = en0[j][0] / 1e4
        poz = en0[j][1]
        # ivme torku: en kotu statik pozda eksene gore atalet x alfa
        Ms = M_al(poz)
        T = {"Gobek": Ms[0], "Kol": Ms[1], "UstKol": Ms[1], "OnKol": Ms[2], "El": Ms[3]}
        Mp = np.eye(4) if lvl == 0 else Ms[lvl - 1]
        ap, up = tp(Mp, ax[key]["n"]), Mp[:3, :3] @ ax[key]["u"]
        up = up / np.linalg.norm(up)
        I = 0.0
        for g in gl:
            m, c, cs, Ig = gr[g]
            Rg = T[g][:3, :3]
            Iw = Rg @ Ig @ Rg.T
            r = tp(T[g], cs) - ap
            rp = r - up * (r @ up)
            I += up @ Iw @ up + m * (rp @ rp)
        I_kgm2 = I * 1e-9
        t_iv = I_kgm2 * ALFA / G * 100
        ara.append((t_yuksuz, poz, I_kgm2, t_iv))
    # 2) omuz stall: sabit (DS3218MG) ya da servo geriliminde (DS3235; dirsek statik + ivme torku hat tepe akimina girer)
    st_omuz, v_omuz = omuz_stall(omuz, ara[2][0] + ara[2][3])

    def izin_yuk(j, st):
        # 2x pay icin izinli yuk (statik)
        lo, hi = 0.0, 5000.0
        vals = [(v[0], v[1]) for kk, v in kayit.items() if kk[0] == j]
        f = lambda mm: max(abs(t0 + mm * t1) for t0, t1 in vals) / 1e4
        if f(0.0) > st / 2:
            return 0.0
        for _ in range(28):
            mid = (lo + hi) / 2
            if f(mid) <= st / 2:
                lo = mid
            else:
                hi = mid
        return lo

    sonuc = []
    for j, (ad, key, lvl, gl, st, sv) in enumerate(eks):
        t_yuksuz, poz, I_kgm2, t_iv = ara[j]
        st = st_omuz if st is None else st
        izin = izin_yuk(j, st)
        sonuc.append(dict(eklem=ad, servo=sv, stall_kgcm=st, yuksuz_kgcm=round(t_yuksuz, 2), yuksuz_poz=list(poz), yuksuz_pay=round(st / max(t_yuksuz, 1e-9), 2),
                          yuklu_kgcm=round(en1[j][0] / 1e4, 2), yuklu_poz=list(en1[j][1]), yuklu_pay=round(st / max(en1[j][0] / 1e4, 1e-9), 2),
                          I_kgm2=round(I_kgm2, 5), ivme_kgcm=round(t_iv, 2), toplam_kgcm=round(t_yuksuz + t_iv, 2),
                          toplam_pay=round(st / max(t_yuksuz + t_iv, 1e-9), 2), izinli_yuk_2x_g=round(izin, 0)))
        if j < 2 and v_omuz is not None:
            # gerilime bagli stall (DS3235): kaynak + alternatif servo (DS3218MG proje degeri) ayni izgarayla
            sonuc[-1].update(stall_kgcm=round(st, 3), servo_gerilimi_V=round(v_omuz, 3), stall_6V_kgcm=interp(OMUZ_SERVO_VERI[sv]["tork"], 6.0),
                             stall_kaynak="stall servo geriliminde (hat 6,0 V - ana hat - 22 AWG uzatma dusumu, S1 kalkisi; kol-analiz modeli)")
            alt_ = {}
            for sv2 in OMUZ_SERVO_VERI:
                if sv2 == sv:
                    continue
                s2, v2 = omuz_stall(sv2, ara[2][0] + ara[2][3])
                alt_[sv2] = dict(stall_kgcm=round(s2, 3), yuksuz_pay=round(s2 / max(t_yuksuz, 1e-9), 2), toplam_pay=round(s2 / max(t_yuksuz + t_iv, 1e-9), 2),
                                 yuklu_pay=round(s2 / max(en1[j][0] / 1e4, 1e-9), 2), izinli_yuk_2x_g=round(izin_yuk(j, s2), 0))
            sonuc[-1]["alternatif"] = alt_
    return sonuc


def kafa_servo(rb, tilt_aralik, kablo_ofs=(65.0, -10.0)):
    ax_t, ax_p = rb.ax["kafa|tilt"], rb.ax["kafa|pan"]
    nT, uT = np.array(ax_t["n"]), np.array(ax_t["u"])
    nP, uP = np.array(ax_p["n"]), np.array(ax_p["u"])
    bas, boy = rb.g["kafa|Bas"], rb.g["kafa|Boyun"]
    mk = 25.0                                                     # kafa ici kablo payi (kafa-analiz.json), tahmini
    ck = nT + np.array([-10.0 - nT[0], kablo_ofs[0], kablo_ofs[1]])
    m = bas["m"] + mk
    c = (bas["c"] * bas["m"] + ck * mk) / m
    egri = []
    for th in range(int(tilt_aralik[0]), int(tilt_aralik[1]) + 1, 5):
        R = rot(dict(n=list(nT), u=list(uT)), th)
        cc = tp(R, c)
        egri.append((th, m * (cc[2] - nT[2]) / 1e4))
    tg = max(abs(e[1]) for e in egri)
    th_g = max(egri, key=lambda e: abs(e[1]))[0]
    r = bas["cs"] - nT
    rp = r - uT * (r @ uT)
    I = uT @ bas["I"] @ uT + bas["m"] * (rp @ rp)
    rk = ck - nT
    rkp = rk - uT * (rk @ uT)
    I += mk * (rkp @ rkp)
    I_t = I * 1e-9
    ti = I_t * ALFA / G * 100
    tilt = dict(kutle_g=round(m, 1), am_eksen_mm=round(float(np.linalg.norm((c - nT) - uT * ((c - nT) @ uT))), 2), yercekimi_kgcm=round(tg, 2),
                yercekimi_th=th_g, I_kgm2=round(I_t, 5), ivme_kgcm=round(ti, 2), toplam_kgcm=round(tg + ti, 2), stall_kgcm=STALL_MG,
                pay=round(STALL_MG / (tg + ti), 2), aralik=list(tilt_aralik))
    # pan: Boyun + Bas (tilt 3 acida), eksene gore atalet
    Ip = {}
    for th in (tilt_aralik[0], 0.0, tilt_aralik[1]):
        R = rot(dict(n=list(nT), u=list(uT)), th)
        tot = 0.0
        for gd, MM in ((boy, np.eye(4)), (bas, R)):
            Rg = MM[:3, :3]
            Iw = Rg @ gd["I"] @ Rg.T
            r = tp(MM, gd["cs"]) - nP
            rp = r - uP * (r @ uP)
            tot += uP @ Iw @ uP + gd["m"] * (rp @ rp)
        r = tp(R, ck) - nP
        rp = r - uP * (r @ uP)
        tot += mk * (rp @ rp)
        Ip[str(th)] = tot * 1e-9
    I_pm = max(Ip.values())
    mP = boy["m"] + m
    cP = (boy["c"] * boy["m"] + c * m) / mP
    F_ax = mP / 1000 * G
    off = math.hypot(cP[0] - nP[0], cP[2] - nP[2])
    M_dev = F_ax * off / 1000
    F_rad = M_dev / 0.011
    T_rul = 0.0015 * (F_ax + 2 * F_rad) * 0.023
    T_kab = 0.03
    T_iv = I_pm * ALFA
    pan_t = (T_iv + T_rul + T_kab) / G * 100
    pan = dict(kutle_g=round(mP, 1), am_eksen_mm=round(off, 1), I_kgm2={k: round(v, 5) for k, v in Ip.items()}, ivme_kgcm=round(T_iv / G * 100, 2),
               rulman_kgcm=round(T_rul / G * 100, 3), kablo_kgcm=round(T_kab / G * 100, 2), toplam_kgcm=round(pan_t, 2), stall_kgcm=STALL_MG,
               pay=round(STALL_MG / pan_t, 2), rulman_eksenel_N=round(F_ax, 1), rulman_radyal_N=round(F_rad, 1))
    return dict(tilt=tilt, pan=pan)


# ====================================================================== kol orani varyantlari (hesap, modelleme yok)
def robot_on_kol(rb, ek):
    """Robotun iki kolunda on kol uzamasini ek['d'] kadar degistirir (kopya; devrilme icin)."""
    rbv = Robot.__new__(Robot)
    rbv.__dict__ = dict(rb.__dict__)
    rbv.g = {k: dict(v) for k, v in rb.g.items()}
    rbv.ax = {k: dict(v) for k, v in rb.ax.items()}
    dv = np.zeros(3)
    for t in ("sag", "sol"):
        gr = {g: [rb.g["dirsek_%s|%s" % (t, g)][x] for x in ("m", "c", "cs", "I")] for g in ("OnKol", "El")}
        kb = "dirsek_%s|bilek" % t
        ax = {kb: dict(n=np.array(rb.ax[kb]["n"], float), u=rb.ax[kb]["u"])}
        dv = on_kol_uygula(gr, ax, rb.alt, t, ek)
        for g in ("OnKol", "El"):
            kk = "dirsek_%s|%s" % (t, g)
            rbv.g[kk] = dict(rbv.g[kk], m=gr[g][0], c=gr[g][1], cs=gr[g][2], I=gr[g][3])
        rbv.ax[kb] = dict(rbv.ax[kb], n=[float(x) for x in ax[kb]["n"]])
    rbv.uc = rb.uc + dv
    return rbv


def kol_orani_on_kol(RB, out):
    """Kol orani varyantlari, taslak geometrisi x1,25 (ek on kolda) iken: x1,00 = 125 cm robot, x1,15 = on kol uzatmasi geri alinir
    (x1,15 taslak geometrisi: tup +30, yaka +19), x1,25 = taslak geometrisi (hesap yok), x1,36 = ek boy yine on kola (dogrusal, tahmini)."""
    ry, re_ = RB["yeni-444"], RB["eski-444"]
    S = TA.KOL_SECENEK["115"]
    L115 = TA.KOL_BOY_ESKI + S["ust_kol"] + S["on_kol"] + S["el"]
    oz_y, oz_e = ry.ozel, re_.ozel
    mu_t = (oz_y["omuz_sag|Ust kol tupu"]["kutle"] - oz_e["omuz_sag|Ust kol tupu"]["kutle"]) / TA.UST_KOL_UZAMA
    mu_e = (oz_y["dirsek_sag|El"]["kutle"] - oz_e["dirsek_sag|El"]["kutle"]) / TA.EL_UZAMA
    mu_o = (oz_y["dirsek_sag|On kol govdesi"]["kutle"] - oz_e["dirsek_sag|On kol govdesi"]["kutle"]) / TA.ON_KOL_UZAMA
    kol_g = lambda rb: rb.g["omuz_sag|Kol"]["m"] + sum(rb.g["dirsek_sag|%s" % g]["m"] for g in ("UstKol", "OnKol", "El"))
    var = []
    for oran in (1.0, 1.15, 1.25, 1.36):
        taslak = abs(oran - TA.KOL_ORAN_HEDEF) < 1e-9
        if oran == 1.0:
            Ltop = TA.KOL_BOY_ESKI
        elif taslak:
            Ltop = TA.KOL_BOY_YENI
        elif abs(oran - 1.15) < 1e-9:
            Ltop = L115
        else:
            Ltop = TA.KOL_BOY_ESKI * oran
        d = Ltop - TA.KOL_BOY_YENI if oran != 1.0 else 0.0
        ek = None
        if oran == 1.0:
            sv = out["servo"]["eski-444"]["kol"]
        elif taslak:
            sv = out["servo"]["yeni-444"]["kol"]
        else:
            ek = on_kol_ek(ry, re_, d)
            sv = kol_servo(ry, ek=ek)
        dv = {}
        for wk in ("yeni-444", "yeni-520"):
            if wk not in RB or oran == 1.0:
                continue
            rbv = robot_on_kol(RB[wk], ek) if ek else RB[wk]
            dvv = devrilme(rbv)
            dv[wk] = dict(ev=dvv["ev"]["duz"], one=dvv["pozlar"][1]["duz"], one_rampa=dvv["pozlar"][1]["rampa5"], one_yuk=dvv["pozlar"][2]["duz"],
                          en_kucuk_duz=dvv["en_kucuk_pay_duz"], en_kucuk_rampa=dvv["en_kucuk_pay_rampa"], izgara_duz=dvv["izgara_en_kucuk_duz"],
                          izgara_rampa=dvv["izgara_en_kucuk_rampa"], kutle_g=dvv["ev"]["kutle_g"], am_y=dvv["ev"]["am"][1],
                          izgara_en_kotu=dvv["izgara_en_kotu"])
        el_ucu_y = (TA.S3_YENI if oran != 1.0 else A.S3) - Ltop
        uz = dict(ust_kol=0.0, on_kol=0.0, el=0.0) if oran == 1.0 else dict(ust_kol=TA.UST_KOL_UZAMA, on_kol=round(TA.ON_KOL_UZAMA + d, 2), el=TA.EL_UZAMA)
        var.append(dict(oran=oran, kol_boy_mm=round(Ltop, 1), el_ucu_y=round(el_ucu_y, 0), tup_ek_mm=0.0, el_ek_mm=0.0, on_kol_ek_mm=round(d, 2),
                        uzama_mm=uz, taslak=taslak, modellendi=(taslak or oran == 1.0), servo=sv, devrilme=dv,
                        kol_kutle_ek_g=round(0.0 if oran == 1.0 else kol_g(ry) - kol_g(re_) + mu_o * d, 1)))
        print("kol x%.2f: L %.1f, el ucu y %.0f, on kol +%.1f | S1 %.2f (pay %.2f, ivmeli %.2f) S2 %.2f (%.2f) dirsek %.2f (%.2f) | %s" % (
            oran, Ltop, el_ucu_y, uz["on_kol"], sv[0]["yuksuz_kgcm"], sv[0]["yuksuz_pay"], sv[0]["toplam_pay"], sv[1]["yuksuz_kgcm"], sv[1]["yuksuz_pay"],
            sv[2]["yuksuz_kgcm"], sv[2]["yuksuz_pay"], {k2: (v["en_kucuk_duz"], v["en_kucuk_rampa"]) for k2, v in dv.items()}))
    return dict(varyant=var, dagilim="on_kol", birim_kutle=dict(tup_g_mm=round(mu_t, 3), yaka_g_mm=round(mu_e, 3), on_kol_g_mm=round(mu_o, 4)),
                taslak_oran=TA.KOL_ORAN_HEDEF, omuz_servo=TA.OMUZ_SERVO["ad"],
                not_="x%.2f = taslak geometrisi (tup +%.0f, on kol +%.1f, yaka +%.0f; parcalardan). x1,15 = on kol uzatmasi geri alinir (x1,15 taslak "
                     "geometrisi, on kol birim kutlesi %.3f g/mm). x1,36 = ek boy yine on kola (dogrusal, geometri modellenmedi, tahmini). x1,00 = 125 cm kolu "
                     "(omuz 955'te, DS3218MG). Omuz servosu %s (stall servo geriliminde); 125 cm satiri DS3218MG 20 kg*cm." % (
                         TA.KOL_ORAN_HEDEF, TA.UST_KOL_UZAMA, TA.ON_KOL_UZAMA, TA.EL_UZAMA, mu_o, TA.OMUZ_SERVO["ad"]))


def main():
    gy = oku("girdi-yeni-444.json")
    ge = oku("girdi-eski-444.json")
    pay_y = [(TA.KABLO_PAY_TABAN["kutle_g"], TA.KABLO_PAY_TABAN["merkez"]), (TA.KABLO_PAY_UZAMA["kutle_g"], TA.KABLO_PAY_UZAMA["merkez"])]
    pay_e = [(TA.KABLO_PAY_TABAN["kutle_g"], TA.KABLO_PAY_TABAN["merkez"])]
    RB = {"eski-444": Robot(ge, "eski-444", pay_e)}
    for f in sorted(glob.glob(os.path.join(AN, "girdi-yeni-*.json"))):
        w = int(os.path.basename(f).split("-")[-1].split(".")[0])
        RB["yeni-%d" % w] = Robot(oku(os.path.basename(f)), "yeni-%d" % w, pay_y)
    out = dict(yontem=dict(devrilme="taban_montaj.py denge(): esik = g (d cos t - h sin t) / h; pay = esik / 1,5 m/s2 (acil stop freni, tahmini); "
                                     "temas teker merkez duzlemleri", motor="taban_montaj.py tork() + donus_hesap.py", servo="dirsek_montaj.py tork() izgarasi; "
                                     "kafa_montaj.py tilt/pan; ivme profili 60 derece 0,4 s (alfa %.1f rad/s2, tahmini)" % ALFA,
                       olcut=dict(devrilme_pay=2.0, devrilme_uyari=1.2, motor_iyi=0.80, motor_uyari=1.0, servo_pay=2.0,
                                  not_="devrilme ve servo: projede pay >= 2 yesil, 1,2-2 uyari (taban_rapor.pay_sinif, viewer-template); motor: "
                                       "surekli torkun <= %80'i iyi, <= %100 uyari (viewer-template stMot)")),
               robot={})
    for k, rb in RB.items():
        M, C = rb.kutle_am()
        r = dict(kutle_g=round(M, 1), am=[round(x, 2) for x in C], taban_w=rb.tw, destek_x=rb.xc, devrilme=devrilme(rb), motor=motor(rb, M, C))
        out["robot"][k] = r
        print("%-9s M %.2f kg AM %s | ev pay %.2f/%.2f/%.2f rampa %.2f/%.2f/%.2f | izgara min duz %.2f rampa %.2f | motor duz %.0f%% rampa5 %.0f%% (0,25: %.0f%%) yerinde mu0,5 x%.2f" % (
            k, M / 1000, [round(x, 1) for x in C], r["devrilme"]["ev"]["duz"]["pay_ileri"], r["devrilme"]["ev"]["duz"]["pay_geri"], r["devrilme"]["ev"]["duz"]["pay_yan"],
            r["devrilme"]["ev"]["rampa5"]["pay_ileri"], r["devrilme"]["ev"]["rampa5"]["pay_geri"], r["devrilme"]["ev"]["rampa5"]["pay_yan"],
            r["devrilme"]["izgara_en_kucuk_duz"], r["devrilme"]["izgara_en_kucuk_rampa"], r["motor"]["duz"]["oran"] * 100, r["motor"]["rampa5"]["oran"] * 100,
            r["motor"]["rampa5_yavas"]["oran"] * 100, r["motor"]["yerinde_donus"][1]["standart_oran"]))
    # devrilme onlemleri (tahmini; geometri degismedi): AM'yi one / asagi almak, Nextion'u kaldirmak
    AKU = (2800.0, (0.0, 133.0, -121.45))                    # kutle.json 'Aku LiFePO4 12,8 V (yatik)'
    NEX = (535.0, (-0.08, 1253.55, 90.2))                    # kutle.json 'Nextion NX1060P101_011'
    ONLEM = [("yok", []),
             ("akü 75 mm öne", [(-AKU[0], AKU[1]), (AKU[0], (0.0, 133.0, -121.45 + 75.0))]),
             ("akü 100 mm öne", [(-AKU[0], AKU[1]), (AKU[0], (0.0, 133.0, -121.45 + 100.0))]),
             ("1,5 kg balast ön-alt (y 60, z +150)", [(1500.0, (0.0, 60.0, 150.0))]),
             ("Nextion kaldırılır (−535 g)", [(-NEX[0], NEX[1])]),
             ("akü 75 mm öne + Nextion kaldırılır", [(-AKU[0], AKU[1]), (AKU[0], (0.0, 133.0, -121.45 + 75.0)), (-NEX[0], NEX[1])])]
    out["onlem"] = []
    for wk in [k for k in RB if k.startswith("yeni")]:
        for ad, ek in ONLEM:
            rbv = Robot.__new__(Robot)
            rbv.__dict__ = dict(RB[wk].__dict__)
            rbv.paylar = list(RB[wk].paylar) + ek
            M, C = rbv.kutle_am()
            dvv = devrilme(rbv)
            iz = dvv["izgara_en_kotu"]
            out["onlem"].append(dict(taban=wk, onlem=ad, kutle_g=round(M, 0), am=[round(x, 1) for x in C],
                                     ev_duz=[dvv["ev"]["duz"]["pay_" + y] for y in ("ileri", "geri", "yan")],
                                     ev_rampa=[dvv["ev"]["rampa5"]["pay_" + y] for y in ("ileri", "geri", "yan")],
                                     izgara_duz=[iz["duz_" + y]["pay"] for y in ("ileri", "geri", "yan")],
                                     izgara_rampa=[iz["rampa5_" + y]["pay"] for y in ("ileri", "geri", "yan")],
                                     motor_rampa5_025=tork(M / 1000, 5.0, a=0.25)["oran"]))
            o = out["onlem"][-1]
            print("onlem %s %-40s AM z %.1f y %.0f | izgara duz %s rampa %s" % (wk, ad, C[2], C[1], o["izgara_duz"], o["izgara_rampa"]))
    # servolar (125 ve 170 @444; genislik servoyu etkilemez)
    out["servo"] = {}
    for k in ("eski-444", "yeni-444"):
        rb = RB[k]
        ta = (-25.0, 30.0) if k.startswith("eski") else TA.TILT_ARALIK
        out["servo"][k] = dict(kol=kol_servo(rb), kafa=kafa_servo(rb, ta))
        for s in out["servo"][k]["kol"]:
            print("  %s %-20s yuksuz %.2f pay %.2f | ivme %.2f -> toplam %.2f pay %.2f | 0,5 kg %.2f pay %.2f | 2x icin yuk %.0f g" % (
                k, s["eklem"], s["yuksuz_kgcm"], s["yuksuz_pay"], s["ivme_kgcm"], s["toplam_kgcm"], s["toplam_pay"], s["yuklu_kgcm"], s["yuklu_pay"], s["izinli_yuk_2x_g"]))
        kf = out["servo"][k]["kafa"]
        print("  %s tilt %.2f (g %.2f + iv %.2f) pay %.2f | pan %.2f pay %.2f, radyal %.1f N" % (
            k, kf["tilt"]["toplam_kgcm"], kf["tilt"]["yercekimi_kgcm"], kf["tilt"]["ivme_kgcm"], kf["tilt"]["pay"], kf["pan"]["toplam_kgcm"], kf["pan"]["pay"], kf["pan"]["rulman_radyal_N"]))
    if TA.OMUZ_SERVO["ad"] != "DS3218MG" or TA.ON_KOL_UZAMA > 0:
        # karar 24 Ekim 2026 (x1,25 + DS3235): kol orani bolumu on kol dagilimiyla (x1,15 secimi asagidaki eski yolla, birebir)
        out["kol_secim"] = dict(secim=TA.KOL_SECIM, karar=TA.KOL_KARAR, boy_mm=round(TA.KOL_BOY_YENI, 1), ust_kol_uzama=TA.UST_KOL_UZAMA,
                                on_kol_uzama=TA.ON_KOL_UZAMA, el_uzama=TA.EL_UZAMA)
        out["omuz_servo"] = dict(ad=TA.OMUZ_SERVO["ad"], eski=TA.OMUZ_SERVO_ESKI["ad"], veri=OMUZ_SERVO_VERI, hat=HAT)
        out["kol_orani"] = kol_orani_on_kol(RB, out)
        json.dump(out, open(os.path.join(AN, "hesap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
        print("analiz/hesap.json yazildi")
        return
    # kol orani
    ry = RB["yeni-444"]
    oz_y, oz_e = ry.ozel, RB["eski-444"].ozel
    mu_t = (oz_y["omuz_sag|Ust kol tupu"]["kutle"] - oz_e["omuz_sag|Ust kol tupu"]["kutle"]) / TA.UST_KOL_UZAMA
    mu_e = (oz_y["dirsek_sag|El"]["kutle"] - oz_e["dirsek_sag|El"]["kutle"]) / TA.EL_UZAMA
    y_tup_alt = TA.S3_YENI + A.DIRSEK["tup_uc_y"] - TA.UST_KOL_UZAMA        # tupun alt ucu (yeni), global y
    y_bilek = ry.ax["dirsek_sag|bilek"]["n"][1]
    var = []
    for oran in (1.0, 1.15, 1.25, 1.36):
        Ltop = TA.KOL_BOY_ESKI * oran
        d = Ltop - TA.KOL_BOY_YENI
        dt = d * TA.UST_KOL_UZAMA / (TA.UST_KOL_UZAMA + TA.EL_UZAMA)
        de = d - dt
        if abs(oran - 1.0) < 1e-9:
            rb_k, ek = RB["eski-444"], None
            sv = out["servo"]["eski-444"]["kol"]
        elif abs(oran - 1.15) < 1e-9:
            rb_k, ek = ry, None
            sv = out["servo"]["yeni-444"]["kol"]
        else:
            ek = dict(dy_dirsek=dt, dy_el=de, m_tup=mu_t * dt, y_tup=y_tup_alt - dt / 2, m_el=mu_e * de, y_el=y_bilek - 60.0 - de / 2)
            sv = kol_servo(ry, ek=ek)
        # devrilme: kol gruplarini kaydirip robotu yeniden hesapla (444 ve 520)
        dv = {}
        for wk in ("yeni-444", "yeni-520"):
            if wk not in RB:
                continue
            base = RB[wk] if oran != 1.0 else None
            if oran == 1.0:
                continue
            rbv = Robot.__new__(Robot)
            rbv.__dict__ = dict(RB[wk].__dict__)
            rbv.g = {k2: dict(v) for k2, v in RB[wk].g.items()}
            rbv.ax = {k2: dict(v) for k2, v in RB[wk].ax.items()}
            if ek:
                for t, sx in (("sag", 1), ("sol", -1)):
                    for g in ("UstKol", "OnKol", "El"):
                        kk = "dirsek_%s|%s" % (t, g)
                        c = rbv.g[kk]["c"].copy()
                        c[1] -= dt + (de if g == "El" else 0.0)
                        rbv.g[kk] = dict(rbv.g[kk], c=c, cs=c)
                    for gk, mk, yk in (("omuz_%s|Kol" % t, ek["m_tup"], ek["y_tup"]), ("dirsek_%s|El" % t, ek["m_el"], ek["y_el"] - de / 2)):
                        g0 = rbv.g[gk]
                        c_ek = np.array([g0["c"][0], yk, g0["c"][2]])
                        m1 = g0["m"] + mk
                        cn = (g0["c"] * g0["m"] + c_ek * mk) / m1
                        rbv.g[gk] = dict(g0, m=m1, c=cn, cs=cn)
                    for ak in ("dirsek_%s|dirsek" % t, "dirsek_%s|bilek" % t):
                        n = list(rbv.ax[ak]["n"])
                        n[1] -= dt
                        rbv.ax[ak] = dict(rbv.ax[ak], n=n)
                rbv.uc = RB[wk].uc - np.array([0, d, 0])
            dvv = devrilme(rbv)
            dv[wk] = dict(ev=dvv["ev"]["duz"], one=dvv["pozlar"][1]["duz"], one_rampa=dvv["pozlar"][1]["rampa5"], one_yuk=dvv["pozlar"][2]["duz"],
                          en_kucuk_duz=dvv["en_kucuk_pay_duz"], en_kucuk_rampa=dvv["en_kucuk_pay_rampa"], izgara_duz=dvv["izgara_en_kucuk_duz"],
                          izgara_rampa=dvv["izgara_en_kucuk_rampa"], kutle_g=dvv["ev"]["kutle_g"], am_y=dvv["ev"]["am"][1])
        if abs(oran - 1.15) < 1e-9:
            Ltop = TA.KOL_BOY_YENI                              # taslaktaki gercek boy (x1,1505)
        el_ucu_y = (TA.S3_YENI if oran != 1.0 else A.S3) - Ltop
        var.append(dict(oran=oran, kol_boy_mm=round(Ltop, 1), el_ucu_y=round(el_ucu_y, 0), tup_ek_mm=round(dt if oran != 1.0 else 0.0, 1), el_ek_mm=round(de if oran != 1.0 else 0.0, 1),
                        servo=sv, devrilme=dv, kol_kutle_ek_g=round(0.0 if oran == 1.0 else (RB["yeni-444"].g["omuz_sag|Kol"]["m"] + sum(RB["yeni-444"].g["dirsek_sag|%s" % g]["m"] for g in ("UstKol", "OnKol", "El"))
                                                                     - RB["eski-444"].g["omuz_sag|Kol"]["m"] - sum(RB["eski-444"].g["dirsek_sag|%s" % g]["m"] for g in ("UstKol", "OnKol", "El"))
                                                                     + mu_t * dt + mu_e * de), 1)))
        print("kol x%.2f: L %.1f, el ucu y %.0f | S1 %.2f (pay %.2f, ivmeli %.2f) S2 %.2f (%.2f) dirsek %.2f (%.2f) | %s" % (
            oran, Ltop, el_ucu_y, sv[0]["yuksuz_kgcm"], sv[0]["yuksuz_pay"], sv[0]["toplam_pay"], sv[1]["yuksuz_kgcm"], sv[1]["yuksuz_pay"],
            sv[2]["yuksuz_kgcm"], sv[2]["yuksuz_pay"], {k2: (v["en_kucuk_duz"], v["en_kucuk_rampa"]) for k2, v in dv.items()}))
    out["kol_orani"] = dict(varyant=var, birim_kutle=dict(tup_g_mm=round(mu_t, 3), yaka_g_mm=round(mu_e, 3)),
                            not_="x1,25 / x1,36: x1,15 taslagindan dogrusal (ek boy tup:yaka = 30:19, birim kutleler taslak uzatmalarindan); "
                                 "geometri modellenmedi, tahmini. x1,00 = mevcut 125 cm kolu (omuz 955'te).")
    json.dump(out, open(os.path.join(AN, "hesap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
    print("analiz/hesap.json yazildi")


if __name__ == "__main__":
    main()
