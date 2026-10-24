# Lale 1,70 m TASLAK - KOL ANALIZI: kol orani (x1,15 / x1,25 / x1,36) x omuz servosu (DS3218MG / DS3235)
# Kol analiz ajani, 24 Ekim 2026. Sistem Python'u (numpy), FreeCAD gerekmez. Ana taslak dosyalarini DEGISTIRMEZ.
# Kontrol ajani, 24 Ekim 2026 (karar Duffy: x1,25 + omuz DS3235, ek on kolda): taban geometrisi artik x1,25 taslak (parcalardan);
# varyantlar taslak_hesap.kol_orani_on_kol ile ayni (ek boy on kolda); onceki sonuc (git e8697ac, dogrusal tup:yaka) 'onceki' altinda.
#
# Girdi: ../analiz/girdi-yeni-444.json (+520) (taslak_analiz.py kutle bolumu), ../kutle.json (parca kutle/AM), ../taslak_hesap.py
#        (Robot, devrilme, rot, kol_gruplari, on_kol_ek) ve ../../arayuz.py, ../../omuz|dirsek *_parcalar.py olculeri (sayi olarak, satir notlu).
# Yontem:
#   servo     taslak_hesap.kol_servo ile AYNI izgara (S1 x S2 x dirsek x bilek, 5 derece; bilek -90/0/90), ivme alfa 26,2 rad/s2
#             (60 derece 0,4 s ucgen profil). Burada izgara kopyalandi (gruplar taslak_hesap.kol_gruplari'ndan): degerler + izgara (yuk
#             hesabi icin) doner; hesap.json ile dogrulanir. Stall torku servo gerilimine gore (datasheet noktalari arasinda dogrusal);
#             gerilim = hat 6,0 V - kablo dusumleri.
#   kutle     x1,25 = taslak geometrisi (kutle.json, parca parca; ek 32,4 mm on kolda). x1,15 = on kol uzatmasi geri alinir (x1,15 taslak
#             geometrisi), x1,36 = ek boy yine on kola: bilek servosu alt kumesi + el kayar, on kol U bolumu birim kutlesi taslaktan
#             (0,345 g/mm). x1,36 geometrisi modellenmedi (dogrusal, tahmini).
#   yapisal   1-B kol modeli (kesit momenti = kesit altindaki kutleler + uc kuvveti), kesit modulleri parca betiklerindeki olculerden
#             (sayisal integrasyon). Yuk durumlari: L1 statik (en kotu yatay poz, surekli), L2 statik + ivme (kisa), L3 servo stall
#             (el ucu engelde; S1, S2, S1+S2 vektorel), L4 darbe (jest tepe hizinda sert engel; enerji yontemi, tahmini).
#             Emniyet: sigma_izin = sigma_malzeme(katman yonune gore) x k_dolu x k_T x k_surunme; >= 2 guvenli, 1,2-2 sinirda, < 1,2 yetersiz.
# Cikti: kol-analiz.json
import os, sys, json, math, copy, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.dirname(HERE)                       # taslak-170
UST = os.path.dirname(TS)                        # tasarim/freecad
for _p in (TS, UST, os.path.join(UST, "taban")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A
import taslak_ayar as TA
import taslak_hesap as TH

G = 9.81
KG = 0.0980665                                   # kg*cm -> N*m
ALFA = TH.ALFA                                   # 26,18 rad/s2
OMEGA_TEPE = 2 * math.radians(60) / 0.4          # ucgen profil tepe hizi 5,24 rad/s
ORANLAR = (1.15, 1.25, 1.36)

# ============================================================================== 1) servo verisi (kaynakli)
SERVO = {
    "DS3218MG": dict(
        tork=[(5.0, 19.0), (6.8, 21.5)], akim=[(5.0, 1.8), (6.8, 2.6)], kutle_g=60.0, hiz_60=0.16, oran=236,
        govde="40 x 20 x 40,4 (kulakla 54,5; delik 49,5 x 10; kulak alti 27,7), 25T",
        kaynak="tork: dirsek-analiz.json stall_kaynak (datasheet 19 kg*cm @5 V, 21,5 @6,8 V; proje 20 kullanir); akim: 06-aku-secimi.md "
               "(aifitlab 1,8 A @5 V, 2,6 A @6,8 V); govde: 04-parca-olculeri.md (DS3218 datasheet)",
        tl=964.5, tl_kaynak="planlama/maliyet.json (Robocombo)"),
    "DS3235": dict(
        tork=[(5.0, 29.0), (6.0, 32.0), (7.4, 35.0)], akim=[(5.0, 1.9), (6.0, 2.1), (7.4, 2.3)], akim_tasarim_6v=3.0,
        kutle_g=60.0, hiz_60=0.12, oran=373,
        govde="40 x 20 x 40 (Robocombo) / 38,5 (datasheet) / 40,5 (probots); delik dizilimi DS3218 ile ayni varsayildi (tahmini), 25T",
        kaynak="Robocombo urun sayfasi (tork 29/32/35 kg*cm @5/6/7,4 V, hiz 0,13/0,12/0,11 s/60, 6-7,4 V, 40x20x40): "
               "https://www.robocombo.com/dsservo-ds3235-35kg-servo-motor-180-derece-su-4148 ; DS3235 datasheet (Rochester ME240 kopyasi): "
               "stall akimi 1,9/2,1/2,3 A, 60 g, oran 373, coreless https://hajim.rochester.edu/me/sites/kelley/me240/DS3235-270_datasheet.pdf ; "
               "diger satici tablolari 2,2-3,9 A -> tasarim akimi 3,0 A @6 V (tahmini)",
        tl=1171.5, tl_liste=1255.0, tl_kaynak="Robocombo 24.10.2026: liste 1.255 TL, indirimli 1.171,50 TL (KDV dahil), stok 134"),
    "MG996R": dict(
        tork=[(4.8, 9.4), (6.0, 11.0)], akim=[(4.8, 2.0), (6.0, 2.5)], kutle_g=55.0, hiz_60=0.14, oran=None,
        govde="40,7 x 19,7 x 42,9; kulakla 53,6; 25T", kaynak="Tower Pro datasheet (9,4 @4,8 V, 11 @6 V; 2,5 A @6 V); 4,8 V akimi tahmini",
        tl=199.0, tl_kaynak="planlama/maliyet.json"),
}


def interp(pts, v):
    xs, ys = zip(*pts)
    if v <= xs[0]:
        return ys[0] + (ys[1] - ys[0]) * (v - xs[0]) / (xs[1] - xs[0])
    for i in range(len(xs) - 1):
        if v <= xs[i + 1]:
            return ys[i] + (ys[i + 1] - ys[i]) * (v - xs[i]) / (xs[i + 1] - xs[i])
    return ys[-2] + (ys[-1] - ys[-2]) * (v - xs[-2]) / (xs[-1] - xs[-2])


def stall(sv, v=6.0):
    return interp(SERVO[sv]["tork"], v)


def stall_akim(sv, v=6.0, tasarim=True):
    s = SERVO[sv]
    if tasarim and "akim_tasarim_6v" in s:
        return s["akim_tasarim_6v"] * interp(s["akim"], v) / interp(s["akim"], 6.0)
    return interp(s["akim"], v)


# ============================================================================== 2) kol varyantlari (taslak_hesap.main ile ayni)
GY = TH.oku("girdi-yeni-444.json")
GE = TH.oku("girdi-eski-444.json")
PAY_Y = [(TA.KABLO_PAY_TABAN["kutle_g"], TA.KABLO_PAY_TABAN["merkez"]), (TA.KABLO_PAY_UZAMA["kutle_g"], TA.KABLO_PAY_UZAMA["merkez"])]
RB = TH.Robot(GY, "yeni-444", PAY_Y)
RB_E = TH.Robot(GE, "eski-444", [(TA.KABLO_PAY_TABAN["kutle_g"], TA.KABLO_PAY_TABAN["merkez"])])
MU_T = (RB.ozel["omuz_sag|Ust kol tupu"]["kutle"] - RB_E.ozel["omuz_sag|Ust kol tupu"]["kutle"]) / TA.UST_KOL_UZAMA   # g/mm
MU_E = (RB.ozel["dirsek_sag|El"]["kutle"] - RB_E.ozel["dirsek_sag|El"]["kutle"]) / TA.EL_UZAMA
MU_O = (RB.ozel["dirsek_sag|On kol govdesi"]["kutle"] - RB_E.ozel["dirsek_sag|On kol govdesi"]["kutle"]) / TA.ON_KOL_UZAMA
Y_BILEK = RB.ax["dirsek_sag|bilek"]["n"][1]
S_E = TA.S3_YENI - RB.ax["dirsek_sag|dirsek"]["n"][1]                            # S1 ekseni -> dirsek ekseni (203)
_S115 = TA.KOL_SECENEK["115"]
L115 = TA.KOL_BOY_ESKI + _S115["ust_kol"] + _S115["on_kol"] + _S115["el"]       # x1,15 taslak (374,5)
BILEK_ILE = RB.alt["dirsek_sag|OnKol|bilek_ile"]["adlar"]                        # bilek servosu alt kumesi (OnKol grubunda)
assert TA.ON_KOL_UZAMA > 0, "kol analizi x1,25 taslak geometrisine gore (TASLAK_KOL=125)"


def varyant(oran):
    """taslak_hesap.kol_orani_on_kol ile ayni: x1,25 taslak geometrisi, digerleri on kol uzamasi degistirilerek."""
    taslak = abs(oran - TA.KOL_ORAN_HEDEF) < 1e-9
    L = TA.KOL_BOY_YENI if taslak else (L115 if abs(oran - 1.15) < 1e-9 else TA.KOL_BOY_ESKI * oran)
    d = L - TA.KOL_BOY_YENI
    ek = None if taslak else TH.on_kol_ek(RB, RB_E, d)
    E = TA.ON_KOL_UZAMA + d
    return dict(oran=oran, L=L, d=d, E=E, dt=0.0, de=0.0, ek=ek, taslak=taslak, tup_boy=100.0 + TA.UST_KOL_UZAMA, yaka_boy=13.6 + TA.EL_UZAMA,
                on_kol_boy=(A.DIRSEK["eksen_y"] - A.DIRSEK["bilek_nokta"][1]) + E)


# ============================================================================== 3) servo izgarasi (taslak_hesap.kol_servo kopyasi + ic veriler)
def servo_izgara(rb, ek=None, taraf="sag"):
    rot, tp, et = TH.rot, TH.tp, TH.eksen_torku
    gr, ax, uc, kanca = TH.kol_gruplari(rb, taraf, ek)                            # taslak_hesap ile ayni gruplar (on kol varyanti dahil)
    a = {k: dict(n=list(v["n"]), u=list(v["u"])) for k, v in ax.items()}

    def M_al(sp):
        phi, th, al, be = sp
        M1 = rot(a["omuz_%s|one_arka" % taraf], phi)
        M2 = M1 @ rot(a["omuz_%s|yana" % taraf], th)
        M3 = M2 @ rot(a["dirsek_%s|dirsek" % taraf], al)
        M4 = M3 @ rot(a["dirsek_%s|bilek" % taraf], be)
        return M1, M2, M3, M4

    eks = [("S1", "omuz_%s|one_arka" % taraf, 0, ("Gobek", "Kol", "UstKol", "OnKol", "El")),
           ("S2", "omuz_%s|yana" % taraf, 1, ("Kol", "UstKol", "OnKol", "El")),
           ("Dirsek", "dirsek_%s|dirsek" % taraf, 2, ("OnKol", "El")),
           ("Bilek", "dirsek_%s|bilek" % taraf, 3, ("El",))]
    PH = sorted(set(list(range(-45, 136, 5)) + [135]))
    TH_ = sorted(set([5] + list(range(10, 121, 5))))
    AL = list(range(0, 106, 5))
    BE = [-90, 0, 90]
    vals = {j: [] for j in range(4)}
    en0 = [(-1, None)] * 4
    for phi in PH:
        for th in TH_:
            for al in AL:
                for be in BE:
                    Ms = M_al((phi, th, al, be))
                    T = {"Gobek": Ms[0], "Kol": Ms[1], "UstKol": Ms[1], "OnKol": Ms[2], "El": Ms[3]}
                    for j, (ad, key, lvl, gl) in enumerate(eks):
                        Mp = np.eye(4) if lvl == 0 else Ms[lvl - 1]
                        ap, up = tp(Mp, ax[key]["n"]), Mp[:3, :3] @ ax[key]["u"]
                        t0 = sum(et(tp(T[g], gr[g][1]), gr[g][0], ap, up) for g in gl)
                        t1 = et(tp(Ms[3], uc if j < 3 else kanca), 1.0, ap, up)
                        vals[j].append((t0, t1))
                        if abs(t0) > en0[j][0]:
                            en0[j] = (abs(t0), (phi, th, al, be))
    out = {}
    for j, (ad, key, lvl, gl) in enumerate(eks):
        poz = en0[j][1]
        Ms = M_al(poz)
        T = {"Gobek": Ms[0], "Kol": Ms[1], "UstKol": Ms[1], "OnKol": Ms[2], "El": Ms[3]}
        Mp = np.eye(4) if lvl == 0 else Ms[lvl - 1]
        ap, up = tp(Mp, ax[key]["n"]), Mp[:3, :3] @ ax[key]["u"]
        up = up / np.linalg.norm(up)
        I = 0.0
        for g in gl:
            m, c, cs, Ig = gr[g]
            Rg = T[g][:3, :3]
            r = tp(T[g], cs) - ap
            rp = r - up * (r @ up)
            I += up @ (Rg @ Ig @ Rg.T) @ up + m * (rp @ rp)
        ru = tp(Ms[3], uc) - ap
        r_uc = float(np.linalg.norm(ru - up * (ru @ up)))
        v = np.array(vals[j])
        out[ad] = dict(statik_kgcm=en0[j][0] / 1e4, poz=list(poz), I_kgm2=I * 1e-9, ivme_kgcm=I * 1e-9 * ALFA / G * 100,
                       r_uc_mm=r_uc, t0=v[:, 0] / 1e4, t1=v[:, 1] / 1e4)       # kg*cm ve kg*cm/g
    return out


def izinli_yuk(iz, ts, pay, ivmeli=False):
    """Elde tasinabilecek yuk (g): statik (ve istenirse ivme) torku <= ts / pay."""
    def f(m):
        t = np.max(np.abs(iz["t0"] + m * iz["t1"]))
        if ivmeli:
            t += (iz["I_kgm2"] + m / 1000.0 * (iz["r_uc_mm"] / 1000.0) ** 2) * ALFA / G * 100
        return t
    if f(0.0) > ts / pay:
        return 0.0
    lo, hi = 0.0, 5000.0
    for _ in range(30):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) <= ts / pay else (lo, mid)
    return lo


# ============================================================================== 4) servo hatti: akim ve gerilim
HAT = dict(v_set=6.0, R_ana=0.008, r_22awg=0.0529, r_20awg=0.0333, xl_tepe=8.0, xl_surekli=5.0, sigorta=7.5, verim=0.88, v_aku=12.8,
           uzatma_m={"S1": 1.45, "S2": 1.55, "Dirsek": 2.0, "Bilek": 2.0, "Pan": 1.0},
           kaynak="planlama/adim3/elektrik.md E1 (XL4016 8 A / surekli 5 A, hat sigortasi 7,5 A, 16 AWG 8 mOhm gidis-donus, 22 AWG "
                  "0,052 Ohm/m); uzatma boylari maliyet.json 'Servo uzatma kablosu' notu (S2 1,105, dirsek/bilek 1,541 m) + taslak "
                  "govde uzamasi 0,435 m (tahmini)")


def servo_akim(sv, T, Ts, Is, I0=0.15):
    """Dogrusal tork-akim modeli (tahmini): hareket halinde bostaki akim I0, stall'da Is."""
    return min(Is, I0 + (Is - I0) * max(T, 0.0) / Ts)


# ============================================================================== 5) malzeme ve emniyet
MALZ = {
    "PETG-CF": dict(xy=59.8, z=41.1, E_xy=3710.0, E_z=2652.0, dolu=0.9,
                    kaynak="Polymaker Fiberon PETG-rCF08 TDS V1.0 (cekme X-Y 59,8 / Z 41,1 MPa; E 3.710 / 2.652 MPa; HDT 65,7 C @1,8 MPa): "
                           "https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PETG-rCF08_V1.0_EN.pdf"),
    "PETG": dict(xy=47.0, z=18.0, E_xy=1500.0, E_z=1500.0, dolu=0.8,
                 kaynak="Prusament PETG TDS v1.1 (baski numunesi akma 47 MPa, E 1,5 GPa, katmanlar arasi yapisma 18 +- 4 MPa, HDT 68 C); "
                        "Microzey HS PETG verisi yok -> temsili (tahmini). https://www.3dprintergear.com.au/assets/files/technical-data-sheet%20(1).pdf"),
}
K_T = dict(normal=0.85, servo_yani=0.75)        # 40 C govde ici / 50 C servo govdesine degen (tahmini; HDT ~66-68 C)
K_SURUNME = dict(L1=0.45, L2=1.0, L3=0.7, L4=1.0)   # surekli yukte PETG surunme-kopma ~ kisa sureli dayanimin %40-50'si (tahmini)
ESIK = (2.0, 1.2)


def sinif(sf):
    if sf is None:
        return "bilinmiyor"
    return "guvenli" if sf >= ESIK[0] else ("sinirda" if sf >= ESIK[1] else "yetersiz")


def izin(malz, yon, durum, sicak="normal"):
    m = MALZ[malz]
    return m[yon] * m["dolu"] * K_T[sicak] * K_SURUNME[durum]


# ============================================================================== 6) kesit ozellikleri (sayisal)
def kesit(dolu_fn, x0, x1, z0, z1, h=0.05):
    xs = np.arange(x0 + h / 2, x1, h)
    zs = np.arange(z0 + h / 2, z1, h)
    X, Z = np.meshgrid(xs, zs)
    D = dolu_fn(X, Z)
    dA = h * h
    Aa = D.sum() * dA
    xc, zc = (X * D).sum() * dA / Aa, (Z * D).sum() * dA / Aa
    Ix = (((Z - zc) ** 2) * D).sum() * dA            # egilme ekseni X (gerilme z ile degisir) -> S1 duzlemi
    Iz = (((X - xc) ** 2) * D).sum() * dA            # egilme ekseni Z (gerilme x ile degisir) -> S2 duzlemi
    cz = max(np.abs(Z[D] - zc).max(), 1e-9)
    cx = max(np.abs(X[D] - xc).max(), 1e-9)
    return dict(A=Aa, Ix=Ix, Iz=Iz, Wx=Ix / cz, Wz=Iz / cx, xc=xc, zc=zc)


R_TUP_O, R_TUP_I = 28.0, A.TUP_PIM_R + A.GECME["tup_pim"]
TUP_TAM = kesit(lambda X, Z: (X ** 2 + Z ** 2 <= R_TUP_O ** 2) & (X ** 2 + Z ** 2 >= R_TUP_I ** 2), -28, 28, -28, 28)
TUP_PENCERE = kesit(lambda X, Z: (X ** 2 + Z ** 2 <= R_TUP_O ** 2) & (X ** 2 + Z ** 2 >= R_TUP_I ** 2) & ~((np.abs(X) < 5.0) & (Z < 0)),
                    -28, 28, -28, 28)                 # omuz_parcalar tup_pencere x 180-190 (eksen 185), arka duvar
YAKA = kesit(lambda X, Z: (X ** 2 + Z ** 2 <= 17.0 ** 2) & (X ** 2 + Z ** 2 >= 11.0 ** 2), -17, 17, -17, 17)   # taslak el boynu O34/O22
PIM = kesit(lambda X, Z: X ** 2 + Z ** 2 <= 25.4 ** 2, -25.4, 25.4, -25.4, 25.4)                               # kol catali pimi O50,8 dolu
# on kol U kesiti (dirsek_parcalar; x mutlak, z = ZE'ye gore): ust bolum (dirsek servosu yaninda) ve alt bolum (bilek servosu yaninda)
ONKOL_UST_IDEAL = kesit(lambda X, Z: ((X >= 168.0) & (X <= 176.5) & (np.abs(Z) <= 14)) | ((X >= 198.6) & (X <= 203.6) & (np.abs(Z) <= 14)) |
                        ((X >= 168.0) & (X <= 203.6) & (Z >= 11) & (Z <= 14)), 168, 204, -14, 14)
ONKOL_ALT = kesit(lambda X, Z: ((X >= 163.6) & (X <= 166.6) & (np.abs(Z) <= 14)) | ((X >= 223.7) & (X <= 226.7) & (np.abs(Z) <= 14)) |
                  ((X >= 163.6) & (X <= 226.7) & (Z >= 11) & (Z <= 14)), 163, 227, -14, 14)
# Kontrol ajani (24 Ekim 2026): taslak-170.FCStd 'On kol govdesi (sag)' y = sabit dilimleri (FreeCAD Face.MatrixOfInertia).
#   s 30 (dirsek servosu penceresi: plaka kesik, yalniz yanak + on duvar): A 324,1 mm2, Wx 1.465, Wz 1.073 mm3 -> idealize UST (plaka dahil,
#   Wz 3.959) bu kesitte 3,7 kat iyimserdi; artik CAD degeri kullanilir. s 42...(42 + 32,4 + 23): alt U, A 339,3, Wx 1.199, Wz 6.288 = ONKOL_ALT.
ONKOL_UST = dict(A=324.1, Wx=1465.1, Wz=1072.8, kaynak="CAD dilimi s 30 (taslak-170.FCStd), kontrol ajani")
assert abs(ONKOL_ALT["A"] - 339.3) < 0.5 and abs(ONKOL_ALT["Wx"] - 1199.2) < 5 and abs(ONKOL_ALT["Wz"] - 6287.6) < 15
S_ONKOL_UST, S_ONKOL_ALT = 30.0, 42.0          # dirsek ekseninden: pencere kesiti; alt U'nun basi (ara duvar alti, en buyuk moment)
PLAKA_5x32 = dict(W_duzlem=5.0 * 32.0 ** 2 / 6.0, A=5.0 * 32.0)          # kol catali on kolu / dirsek catali dis kolu
PLAKA_11x32 = dict(W_duzlem=11.0 * 32.0 ** 2 / 6.0, A=11.0 * 32.0)      # dirsek catali ic kolu


# ============================================================================== 7) 1-B kol kutle modeli (s: S1 ekseninden kol boyunca asagi, mm)
KJ = json.load(open(os.path.join(TS, "kutle.json"), encoding="utf-8"))
S1Y = TA.S3_YENI
assert abs(KJ["kol"]["sag"]["bilek_ekseni"]["nokta"][1] - Y_BILEK) < 0.05, "kutle.json ile girdi-yeni-444.json ayni geometri degil"


def kutle_noktalari(v):
    """(kutle g, s mm) listesi; S2 ekseni altindaki kol (Kol + UstKol + OnKol + El grubu), taslak kutle.json'dan (x1,25) + on kol farki."""
    pts = []
    for p in KJ["parcalar"]:
        if p["modul"] == "omuz_sag" and p["grup"] == "OmuzSag_Kol":
            pts.append((p["kutle_g"], S1Y - p["am"][1]))
        elif p["modul"] == "dirsek_sag" and p["grup"].startswith("DirsekSag_"):
            s = S1Y - p["am"][1]
            if p["grup"] == "DirsekSag_El" or (p["grup"] == "DirsekSag_OnKol" and p["ad"] in BILEK_ILE):
                s += v["d"]                                                    # bilek servosu + el on kolla kayar
            pts.append((p["kutle_g"], s))
    if abs(v["d"]) > 1e-9:
        pts.append((MU_O * v["d"], S_E + TA.ON_KOL_KES_S + TA.ON_KOL_UZAMA + v["d"] / 2))   # on kol U bolumu (eklenen / cikarilan)
        oa = RB.alt["dirsek_sag|OnKol|on_kol_alt"]                                          # govdenin uzatma alti bolumu kayar
        pts += [(-oa["m"], S1Y - oa["c"][1]), (oa["m"], S1Y - oa["c"][1] + v["d"])]
    return pts


def kesit_yuku(pts, s, F_uc=0.0, L=None, yuk_g=0.0):
    """Kesit s'de egilme momenti (N*m): yatay kolda yercekimi (L1), + ivme (L2 ek), uc kuvveti."""
    alt = [(m, si) for m, si in pts if si > s]
    Mg = sum(m / 1000.0 * G * (si - s) / 1000.0 for m, si in alt) + yuk_g / 1000.0 * G * (L - s) / 1000.0
    Ma = sum(m / 1000.0 * ALFA * si / 1000.0 * (si - s) / 1000.0 for m, si in alt) + yuk_g / 1000.0 * ALFA * L / 1000.0 * (L - s) / 1000.0
    return Mg, Ma


# ============================================================================== 8) darbe (enerji yontemi, tahmini)
K_TEMAS = 20000.0          # N/m: PETG el + sert yuzey (masa kenari / duvar) yerel ezilme (tahmini)
THETA_SERVO = math.radians(1.0)   # stall torkunda servo dislisi + horn esnemesi 1 derece (tahmini; bosluk haric)
K_S1_MIL = 2.0e6                  # N/m: S1 cikis mili + horn + gobek radyal rijitligi (tahmini)
THETA_6808 = math.radians(10.0 / 60.0)   # 6808 ic boslugundan egilme serbestligi ~10 dakika (tahmini; normal bosluk C0)


def darbe(I_kgm2, L_mm, Ts_kgcm, omega=OMEGA_TEPE):
    Lm = L_mm / 1000.0
    m_eff = I_kgm2 / Lm ** 2
    k_s = Ts_kgcm * KG / THETA_SERVO / Lm ** 2
    EI = MALZ["PETG"]["E_z"] * 1e6 * TUP_TAM["Ix"] * 1e-12        # tup katman yonunde (Z) modul
    k_k = 3 * EI / Lm ** 3
    k = 1.0 / (1.0 / k_s + 1.0 / k_k + 1.0 / K_TEMAS)
    v = omega * Lm
    F = v * math.sqrt(m_eff * k)
    return dict(m_eff_kg=m_eff, k_servo=k_s, k_kol=k_k, k_temas=K_TEMAS, k_top=k, v_uc=v, F_N=F, M_omuz_Nm=F * Lm,
                M_omuz_kgcm=F * Lm / KG, stall_kati=F * Lm / (Ts_kgcm * KG), omega_guvenli=omega * min(1.0, Ts_kgcm * KG / (F * Lm)))


# ============================================================================== 9) yapisal kontrol
def yapisal(v, iz, sv_omuz, V_eff):
    L = v["L"]
    dt, de = v["dt"], v["de"]
    pts = kutle_noktalari(v)
    W_kol = sum(m for m, _ in pts) / 1000.0 * G                       # S2 alti kol agirligi, N
    W_gobek = 175.2 / 1000.0 * G
    Ts1 = stall(sv_omuz, 6.0)                                         # yapisal stall: nominal 6 V (ihtiyatli)
    Tmg = stall("MG996R", 6.0)
    s_e = S_E + dt                                                    # dirsek ekseni (203)
    s_b = s_e + v["on_kol_boy"]                                       # bilek horn (83,1 + on kol uzamasi)
    s_yaka = s_b + 11.3                                               # flans ucu = el boynu baslangici (dirsek_parcalar S_FLANS 94,4 - S_HORN 83,1)
    I_S1, I_S2 = iz["S1"]["I_kgm2"], iz["S2"]["I_kgm2"]
    D1, D2 = darbe(I_S1, L, Ts1), darbe(I_S2, L, Ts1)
    # yuk durumlari: uc kuvveti (N) ve yercekimi/ivme carpanlari, her duzlem icin
    F_st = Ts1 * KG / (L / 1000.0)                                    # stall, el ucu engelde
    DURUM = {
        "L1": dict(ad="statik (en kotu yatay poz, surekli)", F1=0.0, F2=0.0, g=1, a=0),
        "L2": dict(ad="statik + ivme (60 derece / 0,4 s)", F1=0.0, F2=0.0, g=1, a=1),
        "L3": dict(ad="stall S1 + S2 (el ucu engelde, vektorel)", F1=F_st, F2=F_st, g=1, a=0),
        "L4": dict(ad="darbe (jest tepe hizinda sert engel)", F1=D1["F_N"], F2=D2["F_N"], g=1, a=0),
    }

    def M_kesit(s, dur, duzlem):
        d = DURUM[dur]
        Mg, Ma = kesit_yuku(pts, s, L=L)
        F = d["F1"] if duzlem == 1 else d["F2"]
        return d["g"] * Mg + d["a"] * Ma + F * (L - s) / 1000.0

    def M_birlesik(s, dur):
        if dur in ("L3",):
            return math.hypot(M_kesit(s, dur, 1), M_kesit(s, dur, 2))
        return max(M_kesit(s, dur, 1), M_kesit(s, dur, 2))

    satir = []

    def ekle(eleman, malz, yon, durum, yuk, gerilme, izinli, birim="MPa", sicak="normal", not_="", tahmini=False):
        sf = izinli / gerilme if gerilme > 1e-12 else 99.0
        satir.append(dict(eleman=eleman, malzeme=malz, yon=yon, durum=durum, yuk=yuk, gerilme=round(gerilme, 3), izin=round(izinli, 2),
                          birim=birim, sf=round(min(sf, 99.0), 2), sinif=sinif(sf), not_=not_, tahmini=tahmini))

    for dur in ("L1", "L2", "L3", "L4"):
        # --- PETG-CF kol catali: pim koku (s 40) - katman duzleminde (baski -Z)
        M = M_birlesik(40.0, dur)
        ekle("Kol çatalı pim kökü (Ø50,8 dolu, PETG-CF)", "PETG-CF", "XY", dur, "M %.2f N·m" % M, M * 1e3 / PIM["Wx"] * 1.5,
             izin("PETG-CF", "xy", dur), not_="Kt 1,5 (bilezik geçişi, tahmini); baskı −Z: gerilme katman düzleminde")
        # --- kol catali on kolu (S2 horn plakasi 32 x 5): S2 torku duzlem ici egilme + S1 duzlemi cift kuvveti eksenel
        T_s2 = {"L1": iz["S2"]["statik_kgcm"], "L2": iz["S2"]["statik_kgcm"] + iz["S2"]["ivme_kgcm"], "L3": Ts1,
                "L4": D2["M_omuz_kgcm"]}[dur] * KG
        Mx = M_kesit(0.0, dur, 1)
        sig = T_s2 * 1e3 / PLAKA_5x32["W_duzlem"] + Mx / 0.0585 / PLAKA_5x32["A"]
        ekle("Kol çatalı ön kolu (S2 horn plakası 5 × 32, PETG-CF)", "PETG-CF", "XY", dur, "T_S2 %.2f N·m + M_x %.2f N·m" % (T_s2, Mx),
             sig * 2.0, izin("PETG-CF", "xy", dur, "servo_yani"), sicak="servo_yani", not_="Kt 2,0 (horn delikleri, tahmini)")
        # --- ust kol tupu: pin ucu (s 60) tam kesit Kt 1,5; pencere (s 65) Kt 2,5. Baski +Y: egilme katmanlar arasi (Z)
        for s_, K, ad, ks in ((60.0, 1.5, "pim ucu (s 60)", TUP_TAM), (65.0, 2.5, "kablo penceresi (s 65–89)", TUP_PENCERE)):
            if dur == "L3":
                sg = math.hypot(M_kesit(s_, dur, 1) * 1e3 / ks["Wx"], M_kesit(s_, dur, 2) * 1e3 / ks["Wz"])
                M = math.hypot(M_kesit(s_, dur, 1), M_kesit(s_, dur, 2))
            else:
                M1, M2 = M_kesit(s_, dur, 1), M_kesit(s_, dur, 2)
                sg = max(M1 * 1e3 / ks["Wx"], M2 * 1e3 / ks["Wz"])
                M = max(M1, M2)
            ekle("Üst kol tüpü, %s (Ø56/Ø51,3, PETG)" % ad, "PETG", "Z", dur, "M %.2f N·m" % M, sg * K, izin("PETG", "z", dur),
                 not_="Kt %.1f (tahmini); baskı +Y: eğilme gerilmesi katmanlar arası" % K)
        # --- dirsek catali dis kolu (5 x 32, PETG, baski -Y: kol boyu katmanlar arasi). Dirsek torku + S2 duzlemi cift kuvveti
        s_kok = 178.0 + dt
        T_d = {"L1": iz["Dirsek"]["statik_kgcm"] * KG, "L2": (iz["Dirsek"]["statik_kgcm"] + iz["Dirsek"]["ivme_kgcm"]) * KG,
               "L3": max(Tmg * KG, F_st * (L - s_e) / 1000.0), "L4": D1["F_N"] * (L - s_e) / 1000.0}[dur]
        Mz_e = M_kesit(s_e, dur, 2)
        sig = T_d * 1e3 / PLAKA_5x32["W_duzlem"] + Mz_e / 0.061 / PLAKA_5x32["A"]
        ekle("Dirsek çatalı dış kolu (horn plakası 5 × 32, PETG)", "PETG", "Z", dur, "T_dirsek %.2f + M_z %.2f N·m" % (T_d, Mz_e),
             sig * 2.0, izin("PETG", "z", dur, "servo_yani"), sicak="servo_yani",
             not_="Kt 2,0 (horn delikleri); baskı −Y: kol boyu katmanlar arası. L3'te dirsek torku = max(MG996R stall, omuz stall'ının geri sürmesi)")
        # --- on kol U kesiti (PETG, baski -Z: katman duzleminde)
        for s_, ks, ad in ((s_e + S_ONKOL_UST, ONKOL_UST, "üst, dirsek servosu penceresi (s 30, CAD kesiti)"),
                           (s_e + S_ONKOL_ALT, ONKOL_ALT, "alt U başı (s 42, uzatılan kesit, 3 mm duvar)")):
            M1 = M_kesit(s_, dur, 1)
            M2 = M_kesit(s_, dur, 2)
            sg = math.hypot(M1 * 1e3 / ks["Wx"], M2 * 1e3 / ks["Wz"]) if dur == "L3" else max(M1 * 1e3 / ks["Wx"], M2 * 1e3 / ks["Wz"])
            ekle("Ön kol gövdesi, %s (U kesit, PETG)" % ad, "PETG", "XY", dur, "M %.2f / %.2f N·m" % (M1, M2), sg * 2.0,
                 izin("PETG", "xy", dur, "servo_yani"), sicak="servo_yani", not_="Kt 2,0 (kulak delikleri, köşeler; tahmini)")
        # --- el boynu (O34/O22, PETG, baski +Y: katmanlar arasi)
        M = M_birlesik(s_yaka, dur)
        ekle("El boynu / yaka (Ø34/Ø22, PETG)", "PETG", "Z", dur, "M %.2f N·m" % M, M * 1e3 / YAKA["Wx"] * 1.5, izin("PETG", "z", dur),
             not_="Kt 1,5 (flanş ucu geçişi); baskı +Y: katmanlar arası")
    # ---------------------------------------------------------------------------------- baglanti elemanlari ve satin alinan parcalar
    bag = []

    def bekle(eleman, durum, yuk, deger, kapasite, birim, not_="", tahmini=True):
        sf = kapasite / deger if deger > 1e-12 else 99.0
        bag.append(dict(eleman=eleman, durum=durum, yuk=yuk, deger=round(deger, 2), kapasite=round(kapasite, 1), birim=birim,
                        sf=round(min(sf, 99.0), 2), sinif=sinif(sf), not_=not_, tahmini=tahmini))

    # 25T spline (aluminyum horn): yanak basinci p = 2T / (d_m z h L K)
    def spline_p(T_Nm, L_mm=3.3):
        return 2 * T_Nm * 1e3 / (5.75 * 25 * 0.25 * L_mm * 0.5)
    P_SPL = 0.5 * 276.0                                              # Al 6061-T6 akma 276 MPa x 0,5 (tahmini; horn alasimi bilinmiyor)
    T_S1 = {"L1": iz["S1"]["statik_kgcm"] * KG, "L2": (iz["S1"]["statik_kgcm"] + iz["S1"]["ivme_kgcm"]) * KG, "L3": Ts1 * KG,
            "L4": D1["M_omuz_Nm"]}
    T_S2 = {"L1": iz["S2"]["statik_kgcm"] * KG, "L2": (iz["S2"]["statik_kgcm"] + iz["S2"]["ivme_kgcm"]) * KG, "L3": Ts1 * KG,
            "L4": D2["M_omuz_Nm"]}
    T_D = {"L1": iz["Dirsek"]["statik_kgcm"] * KG, "L2": (iz["Dirsek"]["statik_kgcm"] + iz["Dirsek"]["ivme_kgcm"]) * KG,
           "L3": max(Tmg * KG, F_st * (L - s_e) / 1000.0), "L4": D1["F_N"] * (L - s_e) / 1000.0}
    ell = L - s_b                                                     # bilek horn -> el ucu
    insert_M3 = math.pi * 4.6 * 5.7 * 9.0                             # pi D L tau, tau = 0,5 x 18 MPa (tahmini) ~ 740 N
    insert_M5 = math.pi * 7.0 * 7.0 * 9.0
    for dur in ("L1", "L2", "L3", "L4"):
        kc = K_SURUNME[dur]
        bekle("S1 horn 25T kanal (Al)", dur, "T %.2f N·m" % T_S1[dur], spline_p(T_S1[dur]), P_SPL, "MPa",
              "diş yanak basıncı, yük paylaşımı 0,5, diş yüksekliği 0,25 mm, boy 3,3 mm (tahmini)")
        bekle("S2 horn 25T kanal (Al)", dur, "T %.2f N·m" % T_S2[dur], spline_p(T_S2[dur]), P_SPL, "MPa", "aynı model")
        bekle("Dirsek horn 25T kanal (MG996R, Al)", dur, "T %.2f N·m" % T_D[dur], spline_p(T_D[dur]), P_SPL, "MPa",
              "L3: omuz stall'ı el ucundan dirseği geri sürer")
        # horn civatalari (4x M3, PCD r 8,5): PETG ezilme
        bekle("Göbek ← S1 horn 4× M3 (PETG-CF ezilme, t 9)", dur, "F %.0f N/cıvata" % (T_S1[dur] / (4 * 0.0085)),
              T_S1[dur] / (4 * 0.0085) / (3.0 * 9.0), izin("PETG-CF", "xy", dur, "servo_yani"), "MPa", "kayma olursa ezilme (ön yük PETG'de gevşer)")
        Mx0 = M_kesit(0.0, dur, 1)
        Fc = Mx0 / 0.0585
        Fb = math.hypot(T_S2[dur] / (4 * 0.0085), Fc / 4)
        bekle("Kol çatalı ← S2 horn 4× M3 (PETG-CF ezilme, t 5)", dur, "F %.0f N/cıvata" % Fb, Fb / (3.0 * 5.0),
              izin("PETG-CF", "xy", dur, "servo_yani"), "MPa", "S2 torku + S1 düzlemi çift kuvveti")
        Mz_e = M_kesit(s_e, dur, 2)
        Fb = math.hypot(T_D[dur] / (4 * 0.0085), Mz_e / 0.054 / 4)
        bekle("Dirsek çatalı ← dirsek horn 4× M3 (PETG ezilme, t 5)", dur, "F %.0f N/cıvata" % Fb, Fb / (3.0 * 5.0),
              izin("PETG", "xy", dur, "servo_yani"), "MPa", "delik ekseni X: ezilme katman düzleminde değil -> XY yerine Z alınmadı (yanak yükü)")
        # servo kulak M4 (servo govde reaksiyonu): F = T/84 mm + mil radyal / 4
        # S1 mili radyal (ust sinir: 6808 moment tasimazsa): M_dik = S2 torku + agirlik x (185 - 156,5) mm
        W_tot = W_kol + W_gobek
        dyn = {"L1": 1.0, "L2": 1.0 + ALFA * 0.2 / G, "L3": 1.0, "L4": 1.0}[dur]
        M_dik = T_S2[dur] + W_tot * dyn * 0.0285
        R_ust = M_dik / 0.00815                                       # 6808 hic moment tasimazsa (ust sinir)
        R_s1 = min(R_ust, K_S1_MIL * THETA_6808 * 0.00815 + W_tot * dyn * 0.5)   # 6808 boslugu kapaninca moment 6808'e gecer
        bekle("S1 servo mili radyal (6808 boşluğu sınırlı tahmin)", dur, "M_dik %.2f N·m; üst sınır %.0f N" % (M_dik, R_ust), R_s1, 40.0, "N",
              "6808 eğilme boşluğu 10′ kapanana dek mil taşır (mil rijitliği 2 N/µm, tahmini); 6808 hiç moment taşımazsa %.0f N. "
              "Kapasite: ROBOTIS XM430 radyal 40 N @10 mm (benzer sınıf, DS servoda veri yok; tahmini)" % R_ust)
        P_6808 = W_tot * dyn + max(DURUM[dur]["F1"], DURUM[dur]["F2"]) + 2 * M_dik / 0.046
        bekle("6808-2RS (omuz) eşdeğer statik yük", dur, "P %.0f N (moment 2M/d_m)" % P_6808, P_6808, 3750.0 * 0.7, "N",
              "C0 3,75 kN (SKF 61808-2RS1, RS 2076965) × 0,7 (KWC eşdeğeri, tahmini); moment eşdeğeri 2M/d_m (d_m 46 mm, tahmini)")
        # rulman kapagi 4x M3 isil gomme (6808 momenti tasirsa): cekme = M_dik / 40 mm
        bekle("Rulman kapağı 4× M3 ısıl gömme (yuva, çekme)", dur, "M_dik %.2f N·m / 40 mm" % M_dik, M_dik / 0.040,
              insert_M3 * K_T["normal"] * kc, "N", "6808 momenti taşırsa kapak kulakları sökülmeye çalışır; π·D·L·τ, τ 9 MPa (tahmini)")
        # S2 mili radyal + 625ZZ (omuz): cift kuvvet M_x / 58,5 + agirlik / 2
        R_s2 = Fc + W_kol * dyn / 2
        bekle("S2 servo mili radyal (horn tarafı)", dur, "R %.0f N" % R_s2, R_s2, 40.0, "N", "kapasite XM430 benzeri 40 N (tahmini)")
        bekle("625ZZ (omuz S2 karşı yatak), statik", dur, "R %.0f N" % R_s2, R_s2, 380.0, "N", "C0 0,38 kN (SKF 625-2Z, RS 2867827)")
        bekle("M5 mafsal ısıl gömme (göbek, yanal)", dur, "F %.0f N" % R_s2, R_s2 / (7.0 * 7.0),
              izin("PETG-CF", "xy", dur, "servo_yani"), "MPa", "yanal ezilme")
        # dirsek: 625ZZ + MG996R mili (54 mm aralik)
        sh_e = sum(m for m, si in pts if si > s_e) / 1000.0 * G * dyn
        F_uc2 = DURUM[dur]["F2"]
        R_e = Mz_e / 0.054 + (sh_e + F_uc2) / 2
        bekle("Dirsek MG996R mili radyal", dur, "R %.0f N" % R_e, R_e, 30.0, "N", "kapasite tahmini 30 N (MG996R verisi yok)")
        bekle("625ZZ (dirsek), statik", dur, "R %.0f N" % R_e, R_e, 380.0, "N", "C0 0,38 kN")
        # bilek MG996R mili: karsi yatak yok, el konsol -> esdeger radyal (horn'dan 10 mm, ic yatak 10 mm iceride, tahmini)
        F_el = (sum(m for m, si in pts if si > s_b) / 1000.0 * G * dyn) + max(DURUM[dur]["F1"], DURUM[dur]["F2"])
        lev_cg = (sum(m * (si - s_b) for m, si in pts if si > s_b) / max(sum(m for m, si in pts if si > s_b), 1e-9))
        M_b = (sum(m for m, si in pts if si > s_b) / 1000.0 * G * dyn) * lev_cg / 1000.0 + max(DURUM[dur]["F1"], DURUM[dur]["F2"]) * ell / 1000.0
        F_eq = (M_b * 1000.0 + F_el * 10.0) / 20.0
        bekle("Bilek MG996R mili (el konsol, karşı yatak yok)", dur, "M %.2f N·m, F %.0f N" % (M_b, F_el), F_eq, 30.0, "N eşd.",
              "horn'dan 10 mm eşdeğer radyal; kapasite tahmini 30 N")
        # bilek flansi <- horn 4x M3 (egilme cekmesi) ve yaka <- flans 2x M3 (kesme / ezilme)
        bekle("Bilek flanşı ← horn 4× M3 (çekme, eğilmeden)", dur, "M %.2f N·m" % M_b, M_b / 0.024, 1900.0, "N",
              "M3 8.8 çekme (A_s 5,03 mm² × 640 × 0,6); dişli Al horn (dişin sıyrılması ayrı, ~1 kN tahmini)")
        bekle("El yakası ← flanş 2× M3 ISO 7380 (yaka duvarı ezilme, t 2,85)", dur, "F %.0f N" % (M_b / 0.028), M_b / 0.028 / (3.0 * 2.85),
              izin("PETG", "z", dur), "MPa", "yaka +Y basılı: delik yükü katmanlar arası yönde alındı")
        # tup <-> catal pimi 2x M3 (burulma: bilek stall + el kuvveti x kacik) ve dirsek bilezigi
        T_bur = {"L1": 0.05, "L2": 0.1, "L3": Tmg * KG, "L4": Tmg * KG * 1.5}[dur]
        bekle("Tüp ↔ kol çatalı pimi 2× M3 (tüp duvarı ezilme, t 2,35)", dur, "T %.2f N·m" % T_bur, T_bur / (2 * 0.0254) / (3.0 * 2.35),
              izin("PETG", "xy", dur), "MPa", "burulma: bilek stall'ı (L3), darbe 1,5× (L4); tahmini")
        bilezik_T = 0.3 * math.pi * 2 * 1500.0 * 0.3 * K_T["normal"] * 0.028       # mu 0,3, 2 x M3 on yuku 1,5 kN x 0,3 (PETG gevsemesi)
        bekle("Dirsek sıkma bileziği (sürtünme, burulma)", dur, "T %.2f N·m" % T_bur, T_bur, bilezik_T, "N·m",
              "2× M3x20 ön yükü 1,5 kN, PETG sürünmesiyle %30'a düşer (tahmini), μ 0,3")
        # servo kulak M4 civatalari (S1 govdesi yuvada): F = T / 84 mm + R/4
        F_k = T_S1[dur] / 0.084 + R_s1 / 4
        bekle("S1 servo kulakları 4× M4 (yuva plakası PETG-CF ezilme, t 5)", dur, "F %.0f N" % F_k, F_k / (4.0 * 5.0),
              izin("PETG-CF", "xy", dur, "servo_yani"), "MPa", "servo tork reaksiyonu + mil radyal yükü")
    return dict(satir=satir, baglanti=bag, darbe=dict(S1=D1, S2=D2), F_stall_N=F_st, W_kol_N=W_kol, s=dict(dirsek=s_e, bilek=s_b, yaka=s_yaka),
                kutle_noktalari=[(round(m, 1), round(s, 1)) for m, s in pts])


# ============================================================================== 10) onceki sonucla karsilastirma ozeti
ONCEKI_GIT = "e8697ac"          # kol analiz ajani teslimi (24 Ekim 2026 00:36): x1,15 taslak tabanli, x1,25 / x1,36 dogrusal tup:yaka


def ozet(D, kaynak):
    o = dict(kaynak=kaynak, varyant={})
    for v in D["varyant"]:
        e = {k: v.get(k) for k in ("kol_boy_mm", "tup_boy_mm", "yaka_boy_mm", "on_kol_boy_mm", "el_ucu_y", "kol_kutle_g", "S1_ile_donen_g", "kol_am_s_mm",
                                   "I_S1_kgm2", "I_S2_kgm2")}
        dv = v.get("devrilme", {})
        e["devrilme"] = {w: dict(izgara_duz=dv[w]["izgara_duz"], izgara_rampa=dv[w]["izgara_rampa"]) for w in dv}
        e["servo"] = {}
        for sv, S in v["servo"].items():
            e["servo"][sv] = dict(
                eklem={x["eklem"]: {k: x[k] for k in ("statik_kgcm", "ivme_kgcm", "stall_eff", "pay_statik", "pay_ivmeli", "yuk_2x_g")} for x in S["eklem"]},
                hat={k: S["hat"][k] for k in ("tutma_A", "yogun_A", "tepe_A", "giris_tepe_A")}, V_servo=S["hat"]["V_servo_S1_stall"]["22AWG"],
                geri_surme=S["dirsek_geri_surme_kati"],
                darbe={k: S["yapisal"]["darbe"]["S1"][k] for k in ("F_N", "M_omuz_kgcm", "stall_kati", "omega_guvenli")},
                F_stall_N=S["yapisal"]["F_stall_N"],
                satir=[dict(eleman=r["eleman"], durum=r["durum"], sf=r["sf"]) for r in S["yapisal"]["satir"]],
                baglanti=[dict(eleman=r["eleman"], durum=r["durum"], sf=r["sf"], deger=r["deger"], birim=r["birim"]) for r in S["yapisal"]["baglanti"]])
        o["varyant"]["%.2f" % v["oran"]] = e
    return o


def onceki_ozet():
    yol = "tasarim/freecad/taslak-170/kol-analiz/kol-analiz.json"
    try:
        r = subprocess.run(["git", "-C", HERE, "show", "%s:%s" % (ONCEKI_GIT, yol)], capture_output=True, check=True)
        return ozet(json.loads(r.stdout.decode("utf-8")), "git %s: kol analizi (x1,15 taslak geometrisi; x1,25 / x1,36 dogrusal tup : yaka = 30 : 19; "
                                                         "on kol kesitleri idealize, alt kesit s 60)" % ONCEKI_GIT)
    except Exception as e:
        try:
            return json.load(open(os.path.join(HERE, "kol-analiz.json"), encoding="utf-8"))["onceki"]
        except Exception:
            print("onceki sonuc okunamadi:", e)
            return None


# ============================================================================== 11) ana
def main():
    out = dict(tarih="2026-10-24", servo=SERVO, hat=HAT, malzeme=MALZ, k_T=K_T, k_surunme=K_SURUNME, esik=ESIK,
               yontem=dict(alfa=ALFA, omega_tepe=OMEGA_TEPE, darbe=dict(k_temas=K_TEMAS, theta_servo_derece=1.0),
                           not_="x1,25 = taslak geometrisi (ek 32,4 mm on kolda, parcalardan); x1,15 = on kol uzatmasi geri alinir; x1,36 = ek "
                                "boy on kola, geometri modellenmedi (dogrusal, tahmini). Kontrol ajani 24 Ekim 2026."),
               geometri=dict(kol_secim=TA.KOL_SECIM, ust_kol_uzama=TA.UST_KOL_UZAMA, on_kol_uzama=TA.ON_KOL_UZAMA, el_uzama=TA.EL_UZAMA,
                             kol_boy=TA.KOL_BOY_YENI, omuz_servo=TA.OMUZ_SERVO["ad"], s_dirsek=S_E, onkol_kesit=dict(
                                 ust=dict(s=S_ONKOL_UST, **ONKOL_UST), ust_ideal_onceki={k: ONKOL_UST_IDEAL[k] for k in ("A", "Wx", "Wz")},
                                 alt=dict(s=S_ONKOL_ALT, **{k: ONKOL_ALT[k] for k in ("A", "Wx", "Wz")}), alt_onceki_s=60.0),
                             birim_kutle=dict(tup=MU_T, yaka=MU_E, on_kol=MU_O)),
               varyant=[])
    # dogrulama: hesap.json ile ayni mi
    hj = json.load(open(os.path.join(TS, "analiz", "hesap.json"), encoding="utf-8"))
    assert hj["kol_orani"].get("dagilim") == "on_kol", "hesap.json x1,25 (on kol) dagilimiyla yeniden uretilmeli (taslak_hesap.py)"
    IZ = {}
    for v_ in hj["kol_orani"]["varyant"]:
        if v_["oran"] in ORANLAR:
            v = varyant(v_["oran"])
            iz = IZ[v_["oran"]] = servo_izgara(RB, v["ek"])
            for j, ad in enumerate(("S1", "S2", "Dirsek")):
                a_, b_ = iz[ad]["statik_kgcm"], v_["servo"][j]["yuksuz_kgcm"]
                assert abs(a_ - b_) < 0.02, (v_["oran"], ad, a_, b_)
                assert abs(iz[ad]["ivme_kgcm"] - v_["servo"][j]["ivme_kgcm"]) < 0.02
    out["dogrulama"] = "servo izgarasi hesap.json kol_orani ile ayni (S1/S2/dirsek statik ve ivme farki < 0,02 kg*cm)"
    print(out["dogrulama"])

    for oran in ORANLAR:
        v = varyant(oran)
        iz = IZ[oran]
        pts = kutle_noktalari(v)
        kol_g = sum(m for m, _ in pts)
        V = dict(oran=oran, kol_boy_mm=round(v["L"], 1), tup_boy_mm=round(v["tup_boy"], 1), yaka_boy_mm=round(v["yaka_boy"], 1),
                 tup_ek_mm=round(v["dt"], 1), yaka_ek_mm=round(v["de"], 1), el_ucu_y=round(TA.S3_YENI - v["L"], 0),
                 on_kol_boy_mm=round(v["on_kol_boy"], 1), on_kol_uzama_mm=round(v["E"], 1), on_kol_fark_mm=round(v["d"], 1), taslak=v["taslak"],
                 kol_kutle_g=round(kol_g, 1), gobek_g=175.2, S1_ile_donen_g=round(kol_g + 175.2, 1),
                 kol_am_s_mm=round(sum(m * s for m, s in pts) / kol_g, 1),
                 I_S1_kgm2=round(iz["S1"]["I_kgm2"], 5), I_S2_kgm2=round(iz["S2"]["I_kgm2"], 5))
        # ---------------- servo + akim + gerilim
        V["servo"] = {}
        for sv in ("DS3218MG", "DS3235"):
            # hat A yogun senaryosu: S1, S2 statik+ivme, dirsek statik+ivme, bilek 0,4 A, pan 0,6 A (E1)
            I = {}
            for j in ("S1", "S2"):
                I[j] = servo_akim(sv, iz[j]["statik_kgcm"] + iz[j]["ivme_kgcm"], stall(sv), stall_akim(sv))
            I["Dirsek"] = servo_akim("MG996R", iz["Dirsek"]["statik_kgcm"] + iz["Dirsek"]["ivme_kgcm"], stall("MG996R"), stall_akim("MG996R"))
            I["Bilek"], I["Pan"] = 0.4, 0.6
            yogun = sum(I.values())
            tut = dict(S1=servo_akim(sv, iz["S1"]["statik_kgcm"], stall(sv), stall_akim(sv), I0=0.01),
                       S2=0.05, Dirsek=servo_akim("MG996R", iz["Dirsek"]["statik_kgcm"], stall("MG996R"), stall_akim("MG996R"), I0=0.01),
                       Bilek=0.02, Pan=0.1)
            tepe = stall_akim(sv) * 2 + I["Dirsek"] + I["Bilek"] + I["Pan"]
            teorik = stall_akim(sv) * 2 + stall_akim("MG996R") * 3
            # gerilim: S1 stall aninda (gercekci tepe), 22 AWG ve 20 AWG uzatma
            Vs = {}
            for awg, r in (("22AWG", HAT["r_22awg"]), ("20AWG", HAT["r_20awg"])):
                v_s1 = HAT["v_set"] - min(tepe, HAT["xl_tepe"]) * HAT["R_ana"] - stall_akim(sv) * 2 * r * HAT["uzatma_m"]["S1"]
                Vs[awg] = v_s1
            V_eff = Vs["22AWG"]
            ts_nom, ts_eff = stall(sv, 6.0), stall(sv, V_eff)
            # secenek: XL cikisi 6,4 V (MG996R <= 7,2 V, DS3235 6-7,4 V, DS3218 <= 6,8 V) + S1/S2 uzatmasi 20 AWG
            v_opt = 6.4 - min(tepe, HAT["xl_tepe"]) * HAT["R_ana"] - stall_akim(sv) * 2 * HAT["r_20awg"] * HAT["uzatma_m"]["S1"]
            secenek_64 = dict(V_servo=round(v_opt, 2), stall=round(stall(sv, v_opt), 2),
                              pay_statik=round(stall(sv, v_opt) / iz["S1"]["statik_kgcm"], 2),
                              pay_ivmeli=round(stall(sv, v_opt) / (iz["S1"]["statik_kgcm"] + iz["S1"]["ivme_kgcm"]), 2),
                              yuk_2x_g=round(izinli_yuk(iz["S1"], stall(sv, v_opt), 2.0), 0))
            # dirsek geri surme: omuz stall'i el ucundan dirsege binerse (S1 ve dirsek eksenleri paralel)
            s_e = S_E + v["dt"]
            geri_surme = stall(sv, 6.0) * (v["L"] - s_e) / v["L"] / stall("MG996R", 6.0)
            ts_mg = stall("MG996R", HAT["v_set"] - stall_akim("MG996R") * 2 * HAT["r_22awg"] * HAT["uzatma_m"]["Dirsek"])
            sv_t = []
            for j, ts in (("S1", ts_eff), ("S2", ts_eff), ("Dirsek", ts_mg), ("Bilek", ts_mg)):
                z = iz[j]
                tot = z["statik_kgcm"] + z["ivme_kgcm"]
                sv_t.append(dict(eklem=j, servo=sv if j in ("S1", "S2") else "MG996R", stall_6V=round(stall(sv if j in ("S1", "S2") else "MG996R"), 2),
                                 stall_eff=round(ts, 2), statik_kgcm=round(z["statik_kgcm"], 2), poz=z["poz"], ivme_kgcm=round(z["ivme_kgcm"], 2),
                                 toplam_kgcm=round(tot, 2), pay_statik=round(ts / max(z["statik_kgcm"], 1e-9), 2),
                                 pay_ivmeli=round(ts / max(tot, 1e-9), 2), pay_statik_6V=round(stall(sv if j in ("S1", "S2") else "MG996R") / max(z["statik_kgcm"], 1e-9), 2),
                                 yuk_2x_g=round(izinli_yuk(z, ts, 2.0), 0), yuk_ivmeli_15x_g=round(izinli_yuk(z, ts, 1.5, True), 0),
                                 I_kgm2=round(z["I_kgm2"], 5)))
            hat = dict(I_servo_yogun={k: round(x, 2) for k, x in I.items()}, tutma={k: round(x, 2) for k, x in tut.items()},
                       tutma_A=round(sum(tut.values()), 2), yogun_A=round(yogun, 2), tepe_A=round(tepe, 2), teorik_A=round(teorik, 2),
                       giris_yogun_A=round(HAT["v_set"] * yogun / HAT["verim"] / HAT["v_aku"], 2),
                       giris_tepe_A=round(HAT["v_set"] * min(tepe, HAT["xl_tepe"]) / HAT["verim"] / HAT["v_aku"], 2),
                       V_servo_S1_stall={k: round(x, 2) for k, x in Vs.items()}, stall_akim_A=round(stall_akim(sv), 2),
                       xl_yogun=("yeter" if yogun <= HAT["xl_surekli"] else ("sinirda" if yogun <= HAT["xl_tepe"] else "yetmez")),
                       xl_tepe=("yeter" if tepe <= HAT["xl_tepe"] else "akim sinirina carpar"))
            ys = yapisal(v, iz, sv, V_eff)
            V["servo"][sv] = dict(eklem=sv_t, hat=hat, yapisal=ys, secenek_64V_20AWG=secenek_64, dirsek_geri_surme_kati=round(geri_surme, 2))
            print("x%.2f %-9s S1 st %.2f/%.2f=%.2f iv %.2f | S2 %.2f | yuk2x %s g | hat yogun %.2f tepe %.2f V %.2f | darbe S1 %.0f kgcm (x%.1f)" % (
                oran, sv, sv_t[0]["statik_kgcm"], sv_t[0]["stall_eff"], sv_t[0]["pay_statik"], sv_t[0]["pay_ivmeli"], sv_t[1]["pay_statik"],
                sv_t[0]["yuk_2x_g"], yogun, tepe, V_eff, ys["darbe"]["S1"]["M_omuz_kgcm"], ys["darbe"]["S1"]["stall_kati"]))
        # ---------------- devrilme (taslak_hesap yontemi; servo degisimi kutleyi degistirmez: ikisi de 60 g)
        hv = [x for x in hj["kol_orani"]["varyant"] if abs(x["oran"] - oran) < 1e-9][0]
        V["devrilme"] = hv["devrilme"]
        V["kol_kutle_ek_g_hesap"] = hv["kol_kutle_ek_g"]
        if v["taslak"]:
            # capraz kontrol: omuz stall'i (servo geriliminde) taslak_hesap ile ayni modelden
            for j in (0, 1):
                h_ = hj["servo"]["yeni-444"]["kol"][j]
                k_ = V["servo"][h_["servo"]]["eklem"][j]
                assert abs(h_["stall_kgcm"] - k_["stall_eff"]) < 0.02, (h_["stall_kgcm"], k_["stall_eff"])
            out["dogrulama"] += "; omuz stall (servo geriliminde) taslak_hesap ile ayni (%s %.2f kg*cm @ %.2f V)" % (
                h_["servo"], h_["stall_kgcm"], h_.get("servo_gerilimi_V", 6.0))
        out["varyant"].append(V)
    out["ozet"] = ozet(out, "bu kosu: x1,25 taslak geometrisi, ek on kolda (kontrol ajani 24 Ekim 2026)")
    out["onceki"] = onceki_ozet()
    # ---------------- maliyet
    n = 5
    d_ind = n * (SERVO["DS3235"]["tl"] - SERVO["DS3218MG"]["tl"])
    d_lis = n * (SERVO["DS3235"]["tl_liste"] - SERVO["DS3218MG"]["tl"])
    out["maliyet"] = dict(adet=n, ds3218_birim=SERVO["DS3218MG"]["tl"], ds3235_birim_indirimli=SERVO["DS3235"]["tl"],
                          ds3235_birim_liste=SERVO["DS3235"]["tl_liste"], fark_indirimli=round(d_ind, 2), fark_liste=round(d_lis, 2),
                          filament_tl_kg=389.0)
    json.dump(out, open(os.path.join(HERE, "kol-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1,
              default=lambda o: o.tolist() if isinstance(o, np.ndarray) else float(o))
    print("kol-analiz.json yazildi")


if __name__ == "__main__":
    main()
