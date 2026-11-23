# E0 (duzeltme plani, 15 Ekim 2026): yerinde donus ve yay donusu motor yuku. Saf Python (FreeCAD gerekmez).
# Kullanim: taban_montaj.py bunu import eder (robot kutlesi + AM ile); tek basina calisinca taban-analiz.json'daki ev pozu
# kutlesi/AM'si ile tabloyu basar:  python taban/donus_hesap.py
#
# Sabitler arayuz.TABAN['donus'] (mu senaryolari, durma torku/akimi, surekli oran, Crr, omni yanal direnc). OLCUM GELINCE
# yalniz arayuz'daki *_olculen alanlari doldurulur; hesap 'olculen' senaryosunu ekler ve karari ona gore verir.
#
# Model A (ana): Coulomb surtunmesi, her teker temasinda kuvvet |f| <= mu N, yonu kayma hizinin tersi (izotrop teker: surtunme
#   dairesi; omni: eliptik, yanal mu_yan << boyuna mu). Her yandaki iki motor ayni surucuden paralel -> ayni cevre hizi (u_sol,
#   u_sag komut). Govde hareketi (vx, vz, w) kuvvet ve moment dengesinden Newton ile cozulur (yari statik). Motor torku =
#   r * (f_boyuna + Crr N) . Yerinde donus (u_sol = -u_sag) ve yay donusleri (u_sol = k u_sag).
# Model B (ust sinir, tutucu): yanal surtunme tam mu N (boyuna kuvvetten bagimsiz), donus direnci momenti M = mu_t(R) sum N|z|,
#   dis yan kuvveti M / B; mu_t(R) = mu / (0,925 + 0,15 R/B) (Wong, Theory of Ground Vehicles, kizakli/tekerli kayarak yonlenme
#   yari ampirik bagintisi). Model A, yanal ve boyuna kuvvetin ayni surtunme dairesini paylastigini varsaydigi icin dusuk taraftir.
import os, sys, math, json

_HERE = os.path.dirname(os.path.abspath(__file__))
_UST = os.path.dirname(_HERE)
if _UST not in sys.path:
    sys.path.insert(0, _UST)
import arayuz as A

G = 9.81
D = A.TABAN["donus"]
R_W = A.TEKER_D / 2 / 1000.0                     # m
X_W = A._X_WH / 1000.0                           # teker merkez duzlemi (taban_parcalar X_WH; 520 taban 0,216, 125 cm 0,178)
Z_W = 0.185                                      # aks (taban_parcalar Z_WH)
X_OMNI = A.OMNI_X / 1000.0                       # on omni merkez duzlemi (tek kaynak arayuz.OMNI_X: 0,2015; lastik 0,216). Ayni yanda
                                                 # on/arka teker x'i farkli: yerinde donuste ayni motor hizinda on teker boyuna kayar ve
                                                 # arkaya karsi calisir (eski not: 163,5'te arka fren goruldu); bu fark burada hesaba girer
R_OMNI = A.TABAN["omni"]["cap"] / 2 / 1000.0      # 63,5 mm: ayni motor hizinda on teker %1,6 hizli -> duz giderken cekisme


def motor_degerleri():
    st = D["stall_kgcm_olculen"] or D["stall_kgcm"]
    sa = D["stall_A_olculen"] or D["stall_A"]
    return dict(stall_kgcm=st, surekli_kgcm=round(st * D["surekli_oran"], 2), stall_A=sa, bos_A=D["bos_A"],
                kaynak_stall="olculen" if D["stall_kgcm_olculen"] else "Direnc.net sayfasi (21 kg, durma)",
                kaynak_akim="olculen" if D["stall_A_olculen"] else "tahmini (06-aku-secimi.md 2,4-2,8 A)")


def akim(T_kgcm, mot):
    """DC motor: akim torkla dogrusal (bosta akimdan durma akimina)."""
    return mot["bos_A"] + (mot["stall_A"] - mot["bos_A"]) * abs(T_kgcm) / mot["stall_kgcm"]


def teker_listesi(m_kg, am_x, am_z, mu, omni=False):
    """4 teker: (ad, x, z, N, mu_yan, mu_boy, yan). Yukler AM'ye gore iki eksende dogrusal dagitilir (4 teker statikce belirsiz,
    rijit plaka varsayimi)."""
    W = m_kg * G
    T = []
    for sz, onarka in ((1, "on"), (-1, "arka")):
        for sx, yan in ((1, "sag"), (-1, "sol")):
            om = omni and sz > 0
            x = sx * (X_OMNI if om else X_W)
            fz = 0.5 + sz * am_z / 1000.0 / (2 * Z_W)
            fx = 0.5 + sx * am_x / 1000.0 / (2 * abs(x))
            N = W * fz * fx
            T.append(dict(ad="%s %s" % (onarka, yan), x=x, z=sz * Z_W, N=N, mu_yan=(D["omni_mu_yan"] if om else mu), mu_boy=mu,
                          yan=yan, omni=om, r=(R_OMNI if om else R_W)))
    return T


def _kuvvet(t, vx, vz, w, u, eps=None):
    """Govde hizi (vx, vz) + w (Y ekseni) altinda tekerin temas noktasi kayma hizi ve surtunme kuvveti. eps = kayma_c x referans
    hiz (standart teker cevre hizi 1): kucuk kaymada kuvvet kaymayla orantili (lastik esnemesi), buyukte mu N'e doyar."""
    eps = D["kayma_c"] if eps is None else eps
    sx = vx + w * t["z"]
    sz = vz - w * t["x"] - u * t["r"] / R_W          # u: standart tekerin cevre hizi; ayni motor hizinda cap orani
    ax, az = t["mu_yan"], t["mu_boy"]
    n = math.sqrt((ax * sx) ** 2 + (az * sz) ** 2 + eps ** 2)
    return -t["N"] * ax * ax * sx / n, -t["N"] * az * az * sz / n


def _artik(T, q, uL, uR):
    vx, vz, w = q
    Fx = Fz = M = 0.0
    for t in T:
        fx, fz = _kuvvet(t, vx, vz, w, uR if t["yan"] == "sag" else uL)
        Fx += fx
        Fz += fz
        M += t["x"] * fz - t["z"] * fx
    return [Fx, Fz, M]


def _coz3(J, b):
    a = [row[:] + [b[i]] for i, row in enumerate(J)]
    for c in range(3):
        p = max(range(c, 3), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        if abs(a[c][c]) < 1e-14:
            raise ZeroDivisionError
        for r in range(3):
            if r != c:
                k = a[r][c] / a[c][c]
                for cc in range(c, 4):
                    a[r][cc] -= k * a[c][cc]
    return [a[i][3] / a[i][i] for i in range(3)]


def coz(T, uL, uR):
    """Govde hareketi (vx, vz, w): sum F = 0, sum M = 0 (sabit hizli donus). Newton + sayisal Jacobian + adim kisma; birkac
    baslangic (kinematik donus hizinin kesirleri) denenir, en kucuk artikli cozum alinir."""
    en = None
    for f in (0.5, 0.3, 0.7, 0.9, 0.1):
        q0 = [0.0, 0.5 * (uL + uR) * (1 if uL * uR >= 0 else f), -(uR - uL) / (2 * X_W) * f]
        r = _coz1(T, uL, uR, q0)
        if en is None or r[1] < en[1]:
            en = r
        if en[1] < 1e-9:
            break
    return en


def _coz1(T, uL, uR, q):
    for it in range(300):
        r = _artik(T, q, uL, uR)
        nr = math.sqrt(sum(x * x for x in r))
        if nr < 1e-9:
            break
        J = [[0.0] * 3 for _ in range(3)]
        for j in range(3):
            h = 1e-7 * max(1.0, abs(q[j]))
            qq = q[:]
            qq[j] += h
            rr = _artik(T, qq, uL, uR)
            for i in range(3):
                J[i][j] = (rr[i] - r[i]) / h
        try:
            dq = _coz3(J, [-x for x in r])
        except ZeroDivisionError:
            break
        lam = 1.0
        while lam > 1e-12:
            qn = [q[i] + lam * dq[i] for i in range(3)]
            if math.sqrt(sum(x * x for x in _artik(T, qn, uL, uR))) < nr:
                q = qn
                break
            lam *= 0.5
        else:
            break
    return q, nr, it


def model_a(m_kg, am, mu, k=-1.0, omni=False, mot=None, r_omni=None):
    """k = u_sol / u_sag (-1 yerinde donus). Doner teker basina tork (kg cm, + surus), akim, govdenin gercek donus yaricapi."""
    mot = mot or motor_degerleri()
    T = teker_listesi(m_kg, am[0], am[2], mu, omni)
    if r_omni:
        for t in T:
            if t["omni"]:
                t["r"] = r_omni
    uR, uL = 1.0, k
    q, nr, it = coz(T, uL, uR)
    vx, vz, w = q
    tek = []
    for t in T:
        u = uR if t["yan"] == "sag" else uL
        fx, fz = _kuvvet(t, vx, vz, w, u)
        sgn = 1.0 if u > 0 else (-1.0 if u < 0 else 0.0)
        Tm = (fz + sgn * D["crr"] * t["N"]) * t["r"] * 10.197         # N m -> kg cm
        # surus: motor torku tekerin donme yonunde (enerji verir); fren: tersi
        rol = "surus" if Tm * sgn > 0 else ("fren" if sgn != 0 else "tutma")
        tek.append(dict(teker=t["ad"], omni=t["omni"], N=round(t["N"], 1), T_kgcm=round(abs(Tm), 2), rol=rol,
                        oran_surekli=round(abs(Tm) / mot["surekli_kgcm"], 2), oran_stall=round(abs(Tm) / mot["stall_kgcm"], 2),
                        akim_A=round(akim(Tm, mot), 2)))
    R_ger = abs(vz / w * 1000.0) if abs(w) > 1e-12 else float("inf")      # govde merkezinin donus yaricapi (isaretsiz)
    # donus ivmesi payi (bilgi): I_z ~ m (a^2 + b^2) / 12, ayak izi 0,45 x 0,53 m (etek), ivme D['yaw_ivme']
    Iz = m_kg * (0.444 ** 2 + 0.525 ** 2) / 12.0
    T_iv = Iz * D["yaw_ivme"] / (4 * X_W) * R_W * 10.197
    tmax = max(tek, key=lambda e: e["T_kgcm"])
    return dict(mu=mu, k=k, omni=omni, yaricap_mm=(round(R_ger, 0) if math.isfinite(R_ger) else None),
                ani_merkez_z_mm=round(-vx / w * 1000.0, 1) if abs(w) > 1e-12 else None,   # ani donme merkezinin z'si (- = arkada)
                tekerler=tek, en_cok_kgcm=tmax["T_kgcm"], en_cok_teker=tmax["teker"],
                en_cok_oran_surekli=tmax["oran_surekli"], en_cok_oran_stall=tmax["oran_stall"], en_cok_akim_A=tmax["akim_A"],
                ivme_payi_kgcm=round(T_iv, 2), yakinsama=dict(artik_N=round(nr, 6), iterasyon=it))


def model_b(m_kg, am, mu, R_m=0.0, mot=None):
    """Ust sinir: yanal tam mu_t(R) N, dis yan teker basina (agir teker) tork."""
    mot = mot or motor_degerleri()
    T = teker_listesi(m_kg, am[0], am[2], mu)
    B = 2 * X_W
    mu_t = mu / (0.925 + 0.15 * R_m / B)
    M = mu_t * sum(t["N"] * abs(t["z"]) for t in T)
    F_yan = M / B
    sonuc = []
    for yan in ("sag", "sol"):
        Ty = [t for t in T if t["yan"] == yan]
        Ny = sum(t["N"] for t in Ty)
        for t in Ty:
            F = F_yan * t["N"] / Ny + D["crr"] * t["N"]
            sonuc.append((F * R_W * 10.197, t["ad"]))
    Tm, ad = max(sonuc)
    return dict(mu=mu, R_mm=round(R_m * 1000), mu_t=round(mu_t, 3), M_Nm=round(M, 2), en_cok_kgcm=round(Tm, 2), teker=ad,
                oran_surekli=round(Tm / mot["surekli_kgcm"], 2), oran_stall=round(Tm / mot["stall_kgcm"], 2), akim_A=round(akim(Tm, mot), 2))


# Model C (2. asama omni kontrolu, 23.11.2026): motor hiz-tork egrisi. Model A her yandaki iki tekere AYNI cevre hizini dayatir
# (sonsuz sert motor): on omni x 201,5, arka lastik x 216 oldugunda yerinde donuste ayni yandaki iki teker kinematik olarak farkli
# hiz ister (cap orani dahil on teker acisal hizi %8,2 dusuk), ikisi birbirine karsi calisir ve on motor torku sisirilir (UST SINIR).
# Gercekte her teker ayri JGB37 ile, yan basina ayni PWM'le (ayni gerilim) surulur; DC motor T = Ts (d - wm / w0): hiz farki
# kucuk bir tork farkina doner. Bilinmeyenler govde (vx, vz, w) + 4 teker cevre hizi; denklemler kuvvet / moment dengesi (yari
# statik) + her teker icin motor torku = r (f_boyuna + Crr N). Temas modeli Model A ile ayni (_kuvvet; eps = kayma_c x bos cevre
# hizi x d). Bos hiz kod/fizik/fizik_parametreleri.json motor_bos_hiz_dev_dk 60 (TAHMIN, BOM "12 V 60 dev/dk"); gerilim
# olceklemesi (13,1 V) bu el hesabinda yok (fizik modelinde var); disli surtunmesi fizikteki TAHMIN ile ayni (0,05 N m).
W_HEDEF = 0.9                                   # rad/s: Model C isletme noktasi (fizik ONERI-ADAY / ONERI-MAKARA yerinde w 0,89-0,93)
BOS_HIZ_RAD_S = 60.0 * 2 * math.pi / 60.0       # 60 dev/dk, 12 V (TAHMIN; fizik_parametreleri.json ile ayni kaynak)
DISLI_NM = 0.05                                 # teker milinde disli kutusu Coulomb surtunmesi (TAHMIN; fizik_parametreleri.json motor_disli_surtunme_Nm)


def _cozn(J, b):
    n = len(b)
    a = [row[:] + [b[i]] for i, row in enumerate(J)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        if abs(a[c][c]) < 1e-14:
            raise ZeroDivisionError
        for r in range(n):
            if r != c:
                k = a[r][c] / a[c][c]
                for cc in range(c, n + 1):
                    a[r][cc] -= k * a[c][cc]
    return [a[i][n] / a[i][i] for i in range(n)]


def model_c(m_kg, am, mu, d=1.0, k=-1.0, omni=True, mot=None, x_omni=None):
    """Motor egrili yari statik model. d: sag yanin PWM orani (0..1), sol = k d (k = -1 yerinde donus). x_omni: on omni merkez
    duzlemi (m; varsayilan arayuz.OMNI_X). Doner: govde w (rad/s), teker basina tork (kg cm), rol, teker cevre hizi."""
    mot = mot or motor_degerleri()
    Ts = mot["stall_kgcm"] / 10.197                              # N m
    T = teker_listesi(m_kg, am[0], am[2], mu, omni)
    if x_omni is not None:
        for t in T:
            if t["omni"]:
                t["x"] = math.copysign(x_omni, t["x"])
    dd = [d if t["yan"] == "sag" else k * d for t in T]
    eps = D["kayma_c"] * abs(d) * BOS_HIZ_RAD_S * R_W              # Model A ile ayni olcek (bos cevre hizi x d)

    def kuv(t, vx, vz, w, s):
        sx = vx + w * t["z"]
        sz = vz - w * t["x"] - s
        ax, az = t["mu_yan"], t["mu_boy"]
        n = math.sqrt((ax * sx) ** 2 + (az * sz) ** 2 + eps ** 2)
        return -t["N"] * ax * ax * sx / n, -t["N"] * az * az * sz / n

    def artik(q):
        vx, vz, w = q[:3]
        Fx = Fz = M = 0.0
        r = []
        for i, t in enumerate(T):
            s = q[3 + i]
            fx, fz = kuv(t, vx, vz, w, s)
            Fx += fx
            Fz += fz
            M += t["x"] * fz - t["z"] * fx
            wm = s / t["r"]
            sg = math.tanh(s / (0.01 * BOS_HIZ_RAD_S * R_W))
            r.append(Ts * (dd[i] - wm / BOS_HIZ_RAD_S) - (fz + sg * D["crr"] * t["N"]) * t["r"] - sg * DISLI_NM)
        return [Fx, Fz, M] + r

    en = None
    for f0 in (0.5, 0.2, 0.8, 0.05):
        s0 = [dd[i] * BOS_HIZ_RAD_S * t["r"] * (1 - f0) for i, t in enumerate(T)]
        v0 = BOS_HIZ_RAD_S * R_W * (1 - f0)                       # cevre hizi tahmini (bos hizin kesri)
        q = [0.0, 0.5 * (d + k * d) * v0, -(d - k * d) * v0 / (2 * X_W)] + s0
        for it in range(200):
            r = artik(q)
            nr = math.sqrt(sum(x * x for x in r))
            if nr < 1e-10:
                break
            J = [[0.0] * 7 for _ in range(7)]
            for j in range(7):
                h = 1e-7 * max(1.0, abs(q[j]))
                qq = q[:]
                qq[j] += h
                rr = artik(qq)
                for i in range(7):
                    J[i][j] = (rr[i] - r[i]) / h
            try:
                dq = _cozn(J, [-x for x in r])
            except ZeroDivisionError:
                break
            lam = 1.0
            while lam > 1e-12:
                qn = [q[i] + lam * dq[i] for i in range(7)]
                if math.sqrt(sum(x * x for x in artik(qn))) < nr:
                    q = qn
                    break
                lam *= 0.5
            else:
                break
        if en is None or nr < en[1]:
            en = (q, nr, it)
        if en[1] < 1e-8:
            break
    q, nr, it = en
    vx, vz, w = q[:3]
    tek = []
    for i, t in enumerate(T):
        s = q[3 + i]
        Tm = Ts * (dd[i] - (s / t["r"]) / BOS_HIZ_RAD_S) * 10.197
        rol = "surus" if Tm * s > 0 else "fren"
        tek.append(dict(teker=t["ad"], omni=t["omni"], x_mm=round(t["x"] * 1000, 1), N=round(t["N"], 1), T_kgcm=round(abs(Tm), 2), rol=rol,
                        cevre_hizi_m_s=round(s, 4), oran_surekli=round(abs(Tm) / mot["surekli_kgcm"], 2),
                        oran_stall=round(abs(Tm) / mot["stall_kgcm"], 2), akim_A=round(akim(Tm, mot), 2)))
    tmax = max(tek, key=lambda e: e["T_kgcm"])
    return dict(model="C (motor egrisi)", mu=mu, d=d, k=k, omni=omni, x_omni_mm=round((x_omni if x_omni is not None else X_OMNI) * 1000, 1),
                w_rad_s=round(-w, 4), tekerler=tek, en_cok_kgcm=tmax["T_kgcm"], en_cok_teker=tmax["teker"],
                en_cok_oran_surekli=tmax["oran_surekli"], en_cok_oran_stall=tmax["oran_stall"],
                yakinsama=dict(artik=round(nr, 9), iterasyon=it))


def model_c_w(m_kg, am, mu, w_hedef, omni=True, mot=None, x_omni=None):
    """Yerinde donuste w_hedef'i (rad/s) veren PWM oranini ikiye bolmeyle bulur (kapali cevrim firmware'in yerlesik hali). d <= 1."""
    lo, hi = 0.02, 1.0
    r_hi = model_c(m_kg, am, mu, hi, -1.0, omni, mot, x_omni)
    if r_hi["w_rad_s"] < w_hedef:
        return dict(r_hi, doyum=True)
    for _ in range(40):
        md = 0.5 * (lo + hi)
        if model_c(m_kg, am, mu, md, -1.0, omni, mot, x_omni)["w_rad_s"] < w_hedef:
            lo = md
        else:
            hi = md
    return dict(model_c(m_kg, am, mu, hi, -1.0, omni, mot, x_omni), doyum=False)


def hesapla(m_kg, am):
    """taban_montaj.py bunu cagirir. am = (x, y, z) mm (robot ev pozu, kablo payi dahil)."""
    mot = motor_degerleri()
    mus = list(D["mu_senaryo"])
    etiket = {m: "senaryo" for m in mus}
    if D["mu_olculen"]:
        mus.append(D["mu_olculen"])
        etiket[D["mu_olculen"]] = "olculen"
    out = dict(motor=mot, kutle_kg=round(m_kg, 3), am_mm=[round(v, 1) for v in am], teker_x_mm=X_W * 1000, aks_z_mm=Z_W * 1000,
               r_teker_mm=R_W * 1000, varsayim=dict(D, not_=D["not_"]), yerinde=[], yerinde_omni=[], yay=[], ust_sinir=[])
    for mu in mus:
        a = model_a(m_kg, am, mu, -1.0, False, mot)
        a["etiket"] = etiket[mu]
        out["yerinde"].append(a)
        o = model_a(m_kg, am, mu, -1.0, True, mot)
        o["etiket"] = etiket[mu]
        out["yerinde_omni"].append(o)
        o = model_a(m_kg, am, mu, -1.0, True, mot, r_omni=R_W)     # cap esit omni (O125) varsayimi: cap farkinin etkisi
        o["etiket"] = etiket[mu]
        out.setdefault("yerinde_omni_cap_esit", []).append(o)
        for k in (-0.5, 0.0, 0.5):
            out["yay"].append(model_a(m_kg, am, mu, k, False, mot))
        # Model C (motor egrisi): kapali cevrimin yerlestigi PWM'de yerinde w = W_HEDEF; on omni OMNI_X ve (secenek) lastikle ayni x
        c = model_c_w(m_kg, am, mu, W_HEDEF, True, mot)
        c["etiket"] = etiket[mu]
        out.setdefault("yerinde_omni_motor", []).append(c)
        c = model_c_w(m_kg, am, mu, W_HEDEF, True, mot, x_omni=X_W)
        c["etiket"] = etiket[mu]
        out.setdefault("yerinde_omni_motor_216", []).append(c)
        d = model_a(m_kg, am, mu, 1.0, True, mot)                 # omni ile duz gidis: cap farki cekismesi
        d["etiket"] = etiket[mu]
        out.setdefault("duz_omni", []).append(d)
        for R in (0.0, 0.5, 1.0, 2.0):
            out["ust_sinir"].append(model_b(m_kg, am, mu, R, mot))
    # Model C, 9 kg cm durma torku duyarliligi (depodaki ikinci kaynak; K75)
    m9 = dict(mot, stall_kgcm=9.0, surekli_kgcm=round(9.0 * D["surekli_oran"], 2))
    out["yerinde_omni_motor_9kgcm"] = [dict(model_c_w(m_kg, am, mu, W_HEDEF, True, m9), etiket=etiket[mu]) for mu in mus]
    out["model_notu"] = ("yerinde_omni (Model A) = UST SINIR: ayni yandaki on ve arka tekere ayni cevre hizi dayatir (sonsuz sert motor); "
                         "on x %.1f / arka x %.1f farki ve cap orani on motoru arkaya karsi calistirir (arka fren). yerinde_omni_motor "
                         "(Model C) = motor hiz-tork egrisi, yan basina ayni PWM, w %.2f rad/s'yi veren PWM'de (fizik modeli ONERI-ADAY "
                         "0,89-0,93 rad/s ile ayni isletme noktasi); yari statik, gerilim olceklemesi ve dinamik yok -> alt taraf. "
                         "yerinde_omni_motor_216: ayni model, omni lastikle ayni x'te (ara parca secenegi)." % (
                             X_OMNI * 1000, X_W * 1000, W_HEDEF))
    # karar: olculen varsa ona, yoksa orta senaryoya (0,5) gore
    mu_k = D["mu_olculen"] or 0.5
    ak = next(a for a in out["yerinde"] if a["mu"] == mu_k)
    ok = next(a for a in out["yerinde_omni"] if a["mu"] == mu_k)
    oc = next(a for a in out["yerinde_omni_motor"] if a["mu"] == mu_k)
    bk = next(b for b in out["ust_sinir"] if b["mu"] == mu_k and b["R_mm"] == 0)
    kotu = ak["en_cok_oran_surekli"] > 1.0
    out["karar"] = dict(
        mu=mu_k, dayanak="olculen mu" if D["mu_olculen"] else "orta senaryo (mu 0,5; olcum yok)",
        yerinde_kgcm=ak["en_cok_kgcm"], yerinde_oran_surekli=ak["en_cok_oran_surekli"], yerinde_oran_stall=ak["en_cok_oran_stall"],
        ust_sinir_kgcm=bk["en_cok_kgcm"], ust_sinir_oran_stall=bk["oran_stall"],
        omni_kgcm=ok["en_cok_kgcm"], omni_oran_surekli=ok["en_cok_oran_surekli"], omni_kgcm_etiket="Model A, sert hiz UST SINIRI",
        omni_motor_kgcm=oc["en_cok_kgcm"], omni_motor_oran_surekli=oc["en_cok_oran_surekli"], omni_motor_teker=oc["en_cok_teker"],
        omni_motor_pwm=round(oc["d"], 3),
        sonuc=("KOTU: yerinde donus surekli degerin %.0f%%'i (ust sinir durmanin %.0f%%'i). K1 (a) on iki teker omni onerilir; "
               "omniyle %.0f%% (sert hiz ust siniri, on motor), motor egrisiyle %.0f%% (%s)." % (
                   ak["en_cok_oran_surekli"] * 100, bk["oran_stall"] * 100, ok["en_cok_oran_surekli"] * 100,
                   oc["en_cok_oran_surekli"] * 100, oc["en_cok_teker"]))
        if kotu else "IYI: yerinde donus surekli degerin altinda (%.0f%%); omni gerekmez." % (ak["en_cok_oran_surekli"] * 100))
    return out


if __name__ == "__main__":
    ta = json.load(open(os.path.join(_HERE, "taban-analiz.json"), encoding="utf-8"))
    ev = ta["robot"]["pozlar"][0]
    r = hesapla(ev["kutle_g"] / 1000.0, ev["am"])
    m = r["motor"]
    print("robot %.2f kg, AM %s; motor durma %.1f kg cm, surekli %.2f" % (r["kutle_kg"], r["am_mm"], m["stall_kgcm"], m["surekli_kgcm"]))
    for grp, ad in (("yerinde", "yerinde (standart)"), ("yerinde_omni", "yerinde (on omni)"), ("yerinde_omni_cap_esit", "yerinde (omni O125)")):
        for a in r[grp]:
            print("%-20s mu %.2f: en cok %.2f kg cm (%s) surekli x%.2f stall x%.2f akim %.2f A | R %s z0 %s | %s" % (
                ad, a["mu"], a["en_cok_kgcm"], a["en_cok_teker"], a["en_cok_oran_surekli"], a["en_cok_oran_stall"], a["en_cok_akim_A"],
                a["yaricap_mm"], a["ani_merkez_z_mm"], [(t["teker"], t["T_kgcm"], t["rol"]) for t in a["tekerler"]]))
    for grp, ad in (("yerinde_omni_motor", "C motor egrisi"), ("yerinde_omni_motor_216", "C omni x 216"), ("yerinde_omni_motor_9kgcm", "C 9 kg cm")):
        for a in r[grp]:
            print("%-16s mu %.2f: PWM %.3f w %.3f, en cok %.2f kg cm (%s) surekli x%.2f | %s" % (
                ad, a["mu"], a["d"], a["w_rad_s"], a["en_cok_kgcm"], a["en_cok_teker"], a["en_cok_oran_surekli"],
                [(t["teker"], t["T_kgcm"], t["rol"]) for t in a["tekerler"]]))
    for a in r["duz_omni"]:
        print("duz (on omni O127) mu %.2f: en cok %.2f kg cm %s" % (a["mu"], a["en_cok_kgcm"], [(t["teker"], t["T_kgcm"], t["rol"]) for t in a["tekerler"]]))
    for a in r["yay"]:
        print("yay k %+.1f mu %.2f: R %s mm, en cok %.2f kg cm x%.2f surekli" % (a["k"], a["mu"], a["yaricap_mm"], a["en_cok_kgcm"],
                                                                               a["en_cok_oran_surekli"]))
    for b in r["ust_sinir"]:
        print("ust sinir mu %.2f R %4d: mu_t %.3f, %.2f kg cm, surekli x%.2f stall x%.2f" % (b["mu"], b["R_mm"], b["mu_t"], b["en_cok_kgcm"],
                                                                                           b["oran_surekli"], b["oran_stall"]))
    print(r["karar"]["sonuc"])
