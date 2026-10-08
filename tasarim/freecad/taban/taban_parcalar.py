# Taban modulu (V3) - PARCALAR: alt plaka, elektronik kati (on) + guc paneli (arka), burclar, 4 motorlu tahrik (JGB37 + L braket
# + kaplin + teker), aku + kayis + takoz, guc elektronigi (BTS7960 x2, XL4016 x3, sigorta kutusu, role, ana sigorta, ana anahtar),
# kartlar (Pi 5, ESP32 + tasiyici, PCA9685, BNO055, MAX98357A), HC-SR04 x3 + tutucular, acil stop, tum baglanti elemanlari ve
# kablo yolu semasi (Referans). Import edilebilir: taban_montaj.py (kontroller + kayit), 2. asamada ../carpisma.py ve montaj/.
# Koordinat = global (arayuz.py): orijin zemin + robot merkezi, +X sag, +Y yukari, +Z ileri, mm. Olculer arayuz.TABAN'dan.
import os, sys, math, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from taban_lib import *   # noqa
import taban_lib as L
import arayuz as A

t0 = time.time()
T = A.TABAN
P = []          # parcalar
BAG = []        # baglantilar (rapor tablosu + kontroller)
BASKI = {}      # baski parcasi -> dict(yukari, yon)
LAZER = {}      # lazer kesim parcasi -> dict(y0, malzeme, kalinlik)
YOL = []        # kablo yolu semasi: (devre, renk, nokta listesi)
DOLULUK = 0.8   # kucuk baski parcalari etkin doluluk (tahmini; dirsek/kafa ile ayni)
UP, DOWN = V(0, 1, 0), V(0, -1, 0)
X_BR = (A.W0 / 2 - 2) + (A.V3_W - A.W0) / 2          # 133 (rc:95 + xm='s')
X_WH = X_BR + 2 + 14 + A.TEKER_W / 2                  # 178
Z_WH = A.L0 / 2 - 65                                  # 185
RX = A.UZUN_RAY_X                                     # 115
RHO = {"Al 5754": 2.66, "Kontrplak": 0.68, "Celik": 7.85, "Celik 8.8": 7.85, "Naylon": 1.14, "Pirinc": 8.5,
       "Polyester": 1.38, "Kopuk": 0.10, "PETG": A.PETG_RHO}


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))


def add(ad, grup, shape, tur, malzeme, kod=None, renk="gri", patlat=(0, 0, 0), not_="", kutle=None):
    P.append(dict(ad=ad, grup=grup, shape=shape, tur=tur, malzeme=malzeme, kod=kod or ad, renk=renk, patlat=list(patlat),
                  not_=not_, kutle_sabit=kutle))
    return len(P) - 1


def ayna(sh, sx, sz=1):
    s = sh.copy()
    if sx < 0:
        s = s.mirror(V(0, 0, 0), V(1, 0, 0))
    if sz < 0:
        s = s.mirror(V(0, 0, 0), V(0, 0, 1))
    return s


def tasi(sh, x, y, z):
    """Geometriyi kopyalayarak tasir (Placement birim kalir; Part::Feature'a atanip kaydedilince konum kaybolmaz)."""
    return yerlestir(sh, App.Placement(V(x, y, z), App.Rotation()))


def pisir(s):
    """Sekil kendi Placement'ini tasiyorsa geometriye uygular (dosyada Placement birim, patlatma/AM hesabi dogru)."""
    if s.Placement.isIdentity():
        return s
    m = s.Placement.toMatrix()
    c = s.copy()
    c.Placement = App.Placement()
    c.transformShape(m, True)
    return c


def SX(sx):
    return "sag" if sx > 0 else "sol"


def SZ(sz):
    return "on" if sz > 0 else "arka"


def bag(ad, tip, rol, olcu, temas=(), eksen=None, aciklama=""):
    """rol: {'vida': i, 'pul': i, 'somun': i, 'govde': [i...], ...}; olcu: analitik uc/kavrama degerleri (mm);
    temas: dayanmasi gereken (i, j) ciftleri; eksen: (nokta, yon, [(parca i, yaricap)...]) eksen hizasi kontrolu."""
    BAG.append(dict(ad=ad, tip=tip, rol=rol, olcu=olcu, temas=list(temas), eksen=eksen, aciklama=aciklama))


# ====================================================================== 1) ALT PLAKA (rc:715, 3 mm Al, lazer kesim)
PX, PZ, PR = T["plaka"]["x"], T["plaka"]["z"], T["plaka"]["r"]
y0p, tp = A.Y_PL, A.PL_T
pl = plaka_xz(-PX, PX, -PZ, PZ, y0p, tp, {(sx, sz): PR for sx in (-1, 1) for sz in (-1, 1)})
del_ray = [(sx * RX, z) for sx in (-1, 1) for z in T["plaka_ray_z"]]
del_ara = [(x, z) for x in T["plaka_ara_x"] for z in A.ARA_RAY_Z]
del_brk = [(sx * T["braket_civata"]["x"], sz * Z_WH + s * T["braket_civata"]["dz"]) for sx in (-1, 1) for sz in (-1, 1) for s in (-1, 1)]
del_kablo = [(sx * x, z) for sx in (-1, 1) for (x, z) in T["motor_kablo_delik"]]
del_bts = [(bx + dx * L.BTS["dk"], bz + dz * L.BTS["dk"]) for (bx, bz) in T["bts"] for dx in (-1, 1) for dz in (-1, 1)]
del_xl = [(x + dx * L.XL["dx"] / 2, z + dz * L.XL["dz"] / 2) for (x, z, _) in T["xl"] for dx in (-1, 1) for dz in (-1, 1)]
del_tak = [(x, 0.5 * (T["takoz"]["z"][0] + T["takoz"]["z"][1])) for x in (-60.0, 60.0)]
kes = []
kes += [delik_y(x, z, A.CLEAR[6], y0p, tp) for (x, z) in del_ray + del_ara]
kes += [delik_y(x, z, A.CLEAR[4], y0p, tp) for (x, z) in del_brk]
kes += [delik_y(x, z, T["kablo_delik_d"], y0p, tp) for (x, z) in del_kablo]
kes += [delik_y(x, z, A.CLEAR[3], y0p, tp) for (x, z) in del_bts + del_xl + del_tak]
KAYIS_X = (90.75, 94.25)
for sx in (-1, 1):
    for z in T["kayis_z"]:
        x0, x1 = sorted((sx * KAYIS_X[0], sx * KAYIS_X[1]))
        kes.append(yarik_y(x0, x1, z - T["kayis_en"] / 2 - 2.5, z + T["kayis_en"] / 2 + 2.5, y0p, tp))
pl = pl.cut(Part.makeCompound(kes)).removeSplitter()
PLAKA = add("Alt plaka", "Plaka", pl, "Lazer", "Al 5754", kod="Alt plaka 270 x 500 x 3 Al 5754 (lazer kesim)", renk="alu2",
            patlat=(0, -150, 0), not_="sigma raylarina 14x M6 + cekic somun; motor braketleri 8x M4 + cekic somun")
LAZER["Alt plaka"] = dict(y0=y0p, malzeme="Al 5754 3 mm", kalinlik=tp)
log("alt plaka", len(kes), "kesim")

# --- plaka -> sigma raylari: M6x14 DIN 912 + pul (alttan) + M6 cekic somun (rayin alt kanalinda)
CD, CL = T["plaka_civata"]
for (x, z), ad_ray, uzun in [((x, z), "uzun ray %s" % SX(x), "X") for (x, z) in del_ray] + \
                            [((x, z), "ara ray z %+.0f" % z, "Z") for (x, z) in del_ara]:
    yb = y0p - A.WASH125[CD][2]
    iw = add("Pul M6 (plaka, %s, z %+.0f)" % (ad_ray, z), "Plaka", pul(CD, (x, yb, z), UP), "Baglanti", "Celik", kod="M6 DIN 125 pul",
             renk="celik", patlat=(x * 0.2, -210, z * 0.1))
    iv = add("Civata M6x%d (plaka, %s, z %+.0f)" % (CL, ad_ray, z), "Plaka", vida912(CD, CL, (x, yb, z), UP), "Baglanti", "Celik 8.8",
             kod="M6x%d DIN 912" % CL, renk="celik", patlat=(x * 0.2, -250, z * 0.1))
    ld = V(1, 0, 0) if uzun == "X" else V(0, 0, 1)
    isn = add("Cekic somun M6 (plaka, %s, z %+.0f)" % (ad_ray, z), "Plaka", hammer_nut((x, A.Y_RAIL0 + A.LIP, z), DOWN, ld, d=6),
              "Baglanti", "Celik", kod="M6 cekic somun, kanal 10", renk="celik", patlat=(x * 0.2, 60, z * 0.1))
    uc = yb + CL
    bag("Plaka - %s (z %+.0f, x %+.0f)" % (ad_ray, z, x), "kanal", dict(vida=iv, pul=iw, somun=isn, govde=[PLAKA]),
        dict(d=CD, uc=uc - A.Y_RAIL0, somun_ust=A.LIP + 5.0, taban=A.KANAL_TABAN, kavrama=min(uc, A.Y_RAIL0 + A.LIP + 5) - (A.Y_RAIL0 + A.LIP)),
        temas=[(iw, PLAKA), (iv, iw)], eksen=(V(x, 0, z), UP, [(iv, CD / 2), (isn, CD / 2)]),
        aciklama="alttan pul + M6x14, rayin alt kanalinda cekic somun (uzun yonu kanala dik)")

# ====================================================================== 2) BURCLAR + KAT (on) + GUC PANELI (arka)
y0d, td = A.Y_DECK0, A.DECK_T
BURC = {}
for sx in (-1, 1):
    for z in T["burc_z"]:
        x = sx * RX
        ih = add("Cekic somun M5 (burc %s z %+.0f)" % (SX(sx), z), "Plaka", hammer_nut((x, A.Y_RAIL1 - A.LIP, z), UP, V(1, 0, 0), d=5),
                 "Baglanti", "Celik", kod="M5 cekic somun, kanal 10 (tahmini olcu)", renk="celik", patlat=(sx * 40, 0, z * 0.1))
        ys = A.Y_RAIL1 - A.LIP - 5.0 + 16.0
        isv = add("Saplama M5x16 DIN 913 (burc %s z %+.0f)" % (SX(sx), z), "Plaka", setvida(5, 16, (x, ys, z), DOWN), "Baglanti", "Celik 8.8",
                  kod="M5x16 DIN 913 set vida (saplama)", renk="siyah", patlat=(sx * 40, 40, z * 0.1))
        ib = add("Burc M5x40 (%s z %+.0f)" % (SX(sx), z), "Plaka", burc(8.0, 40.0, (x, A.Y_RAIL1, z), UP, 5.0), "Satin", "Pirinc",
                 kod="M5 x 40 burc, disi-disi, AA 8", renk="pirinc", patlat=(sx * 40, 90, z * 0.1), kutle=12.0)
        BURC[(sx, z)] = ib
        bag("Burc - uzun ray %s ust kanali (z %+.0f)" % (SX(sx), z), "saplama", dict(vida=isv, somun=ih, govde=[ib]),
            dict(d=5, uc=-(ys - 16.0 - A.Y_RAIL1), somun_ust=A.LIP + 5.0, taban=A.KANAL_TABAN, kavrama_somun=5.0, kavrama_burc=ys - A.Y_RAIL1),
            temas=[], eksen=(V(x, 0, z), UP, [(isv, 2.5), (ih, 2.5), (ib, 2.5)]),
            aciklama="M5 cekic somun + M5x16 saplama (somunu tam gecer, kanal tabanina 2,5), burc saplamaya ~6,7 mm vidalanir")
YK = T["kat_ayrim_z"]
KAT_ON_Z0, KAT_ARKA_Z1 = YK + 0.25, YK - 0.25
kat_on = plaka_xz(-PX, PX, KAT_ON_Z0, PZ, y0d, td, {(-1, 1): PR, (1, 1): PR, (-1, -1): 2.0, (1, -1): 2.0})
kat_ar = plaka_xz(-PX, PX, -PZ, KAT_ARKA_Z1, y0d, td, {(-1, -1): PR, (1, -1): PR, (-1, 1): 2.0, (1, 1): 2.0})
kes_on, kes_ar = [], []
for sx in (-1, 1):
    for z in T["burc_z"]:
        (kes_on if z > 0 else kes_ar).append(delik_y(sx * RX, z, 5.5, y0d, td))
x0, x1, z0, z1 = T["kat_kesik_on"]
kes_on.append(kesik_r(x0, x1, z0, z1, 5.0, y0d, td))
kes_ar.append(box(-22, 22, y0d - 1, y0d + td + 1, -22, KAT_ARKA_Z1 + 1))          # direk cebi (onden acik)
for sx in (-1, 1):
    a0, a1 = sorted((sx * 40.0, sx * 80.0))
    kes_ar.append(yarik_y(a0, a1, -37.0, -23.0, y0d, td))                            # aku kablolari
SK = T["sigorta_kutusu"]
for sx in (-1, 1):
    kes_ar.append(delik_y(SK["merkez"][0] + sx * SK["delik_x"], SK["delik_z"], A.CLEAR[4], y0d, td))
RL = T["role"]
RL_DEL = (RL["merkez"][0], RL["merkez"][1] - RL["olcu"][1] / 2 - 5.0)
kes_ar.append(delik_y(RL_DEL[0], RL_DEL[1], A.CLEAR[4], y0d, td))

# --- kart konumlari (kat ustu y = Y_DECK1)
YD1 = A.Y_DECK1
PI_C, PCA_C, BNO_C, ESP_C, AMP_C = T["pi"]["merkez"], T["pca"]["merkez"], T["bno"]["merkez"], T["esp"]["merkez"], T["amp"]["merkez"]
pi_del = [(PI_C[0] + x, PI_C[1] + z) for (x, z) in L.PI_DELIK]
pca_del = [(PCA_C[0] + sx * L.PCA["dx"] / 2, PCA_C[1] + sz * L.PCA["dz"] / 2) for sx in (-1, 1) for sz in (-1, 1)]
bno_del = [(BNO_C[0] + sx * L.BNO["dx"] / 2, BNO_C[1] + sz * L.BNO["dz"] / 2) for sx in (-1, 1) for sz in (-1, 1)]
perf_del = [(ESP_C[0] + sx * (L.PERF["l"] / 2 - L.PERF["kenar"]), ESP_C[1] + sz * (L.PERF["w"] / 2 - L.PERF["kenar"]))
            for sx in (-1, 1) for sz in (-1, 1)]
kes_on += [delik_y(x, z, CLEAR_T[2.5], y0d, td) for (x, z) in pi_del + pca_del + bno_del]
kes_on += [delik_y(x, z, A.CLEAR[3], y0d, td) for (x, z) in perf_del]
kat_on = kat_on.cut(Part.makeCompound(kes_on)).removeSplitter()
kat_ar = kat_ar.cut(Part.makeCompound(kes_ar)).removeSplitter()
KAT_ON = add("Elektronik kati (on)", "Plaka", kat_on, "Lazer", "Kontrplak", kod="Elektronik kati on 270 x 226 x 5 huş kontrplak (lazer)",
             renk="ahsap", patlat=(0, 260, 60), not_="Pi 5, ESP32 tasiyici, PCA9685, BNO055, MAX98357A; 4x M5 burca")
KAT_AR = add("Guc paneli (arka kat)", "Plaka", kat_ar, "Lazer", "Kontrplak", kod="Guc paneli arka 270 x 274 x 5 huş kontrplak (lazer)",
             renk="ahsap", patlat=(0, 260, -60), not_="sigorta kutusu, role, ana sigorta; akunun ustunde, aku icin sokulur")
LAZER["Elektronik kati (on)"] = dict(y0=y0d, malzeme="Huş kontrplak 5 mm", kalinlik=td)
LAZER["Guc paneli (arka kat)"] = dict(y0=y0d, malzeme="Huş kontrplak 5 mm", kalinlik=td)
for (sx, z), ib in BURC.items():
    x = sx * RX
    kat = KAT_ON if z > 0 else KAT_AR
    iw = add("Pul M5 (kat %s z %+.0f)" % (SX(sx), z), "Plaka", pul(5, (x, YD1, z), UP), "Baglanti", "Celik", kod="M5 DIN 125 pul",
             renk="celik", patlat=(sx * 40, 300, z * 0.3))
    yb = YD1 + A.WASH125[5][2]
    iv = add("Civata M5x12 (kat %s z %+.0f)" % (SX(sx), z), "Plaka", vida912(5, 12, (x, yb, z), DOWN), "Baglanti", "Celik 8.8",
             kod="M5x12 DIN 912", renk="celik", patlat=(sx * 40, 330, z * 0.3))
    bag("Kat - burc (%s z %+.0f)" % (SX(sx), z), "burc", dict(vida=iv, pul=iw, govde=[kat], burc=ib),
        dict(d=5, kavrama=12 - A.WASH125[5][2] - td, uc_burc=12 - A.WASH125[5][2] - td),
        temas=[(iw, kat), (iv, iw), (ib, kat)], eksen=(V(x, 0, z), UP, [(iv, 2.5), (ib, 2.5)]),
        aciklama="ustten pul + M5x12, burca 6 mm")
log("plakalar + burclar")

# ====================================================================== 3) TAHRIK: JGB37 + L braket + kaplin + teker (4 kose)
motor0 = tasi(jgb37_local(), X_BR, A.AX, Z_WH)
braket0 = tasi(braket_local(T["braket_civata"]["x"] - X_BR, T["braket_civata"]["dz"]), X_BR, A.AX, Z_WH)
kaplin0 = tasi(kaplin_local(), X_BR + L.BRK["t"] + 2.0, A.AX, Z_WH)
teker0 = tasi(teker_local(), X_WH, A.AX, Z_WH)
TEKER = {}
for sx in (-1, 1):
    for sz in (-1, 1):
        k = "%s %s" % (SZ(sz), SX(sx))
        pk = (sx * 80, 0, sz * 40)
        im = add("Motor JGB37-520 (%s)" % k, "Tahrik", ayna(motor0, sx, sz), "Satin", "Celik", kod="JGB37-520 12 V 60 dev/dk enkoderli",
                 renk="motor", patlat=(sx * 60, -40, sz * 40), kutle=L.JGB["kutle_g"])
        ibr = add("Motor braketi L 37 mm (%s)" % k, "Tahrik", ayna(braket0, sx, sz), "Satin", "Celik", kod="37 mm L motor braketi 1,5 mm",
                  renk="celik", patlat=(sx * 90, -20, sz * 40), kutle=L.BRK["kutle_g"])
        ik = add("Kaplin 12 mm altigen (%s)" % k, "Tahrik", ayna(kaplin0, sx, sz), "Satin", "Pirinc", kod="12 mm altigen kaplin x 30, O6",
                 renk="pirinc", patlat=(sx * 120, -40, sz * 40), kutle=L.KAP["kutle_g"])
        it = add("Teker 125 x 58 (%s)" % k, "Tahrik", ayna(teker0, sx, sz), "Satin", "Kaucuk + plastik", kod="Arazi tekerlegi 125 x 58",
                 renk="lastik", patlat=(sx * 170, -40, sz * 40), kutle=L.TEK["kutle_g"])
        TEKER[(sx, sz)] = it
        # braket -> plaka -> uzun ray: 2x M4x16 + pul (flans altindan) + M4 cekic somun
        yf = A.Y_PL - L.BRK["t"]
        for s in (-1, 1):
            x, z = sx * T["braket_civata"]["x"], sz * Z_WH + s * T["braket_civata"]["dz"]
            yb = yf - A.WASH125[4][2]
            iw = add("Pul M4 (braket %s %+d)" % (k, s), "Tahrik", pul(4, (x, yb, z), UP), "Baglanti", "Celik", kod="M4 DIN 125 pul",
                     renk="celik", patlat=(sx * 90, -80, sz * 40))
            iv = add("Civata M4x16 (braket %s %+d)" % (k, s), "Tahrik", vida912(4, 16, (x, yb, z), UP), "Baglanti", "Celik 8.8",
                     kod="M4x16 DIN 912", renk="celik", patlat=(sx * 90, -110, sz * 40))
            isn = add("Cekic somun M4 (braket %s %+d)" % (k, s), "Tahrik", hammer_nut((x, A.Y_RAIL0 + A.LIP, z), DOWN, V(1, 0, 0), d=4),
                      "Baglanti", "Celik", kod="M4 cekic somun, kanal 10 (tahmini olcu)", renk="celik", patlat=(sx * 40, 60, sz * 40))
            uc = yb + 16
            bag("Motor braketi - plaka - uzun ray (%s %+d)" % (k, s), "kanal", dict(vida=iv, pul=iw, somun=isn, govde=[ibr, PLAKA]),
                dict(d=4, uc=uc - A.Y_RAIL0, somun_ust=A.LIP + 5.0, taban=A.KANAL_TABAN, kavrama=min(uc, A.Y_RAIL0 + A.LIP + 5) - (A.Y_RAIL0 + A.LIP)),
                temas=[(iw, ibr), (iv, iw), (ibr, PLAKA)], eksen=(V(x, 0, z), UP, [(iv, 2.0), (isn, 2.0)]),
                aciklama="flans + plaka sikistirilir; braket motor takilmadan once baglanir (anahtar reduktorden gecmez)")
        # motor -> braket: 4x M3x6 DIN 912 reduktor on yuzu deliklerine (O31 daire)
        for i, (yy, zz) in enumerate(jgb_delikler()):
            if (30, 90, 150, 210, 270, 330)[i] not in L.JGB_DELIK_ACI:
                continue
            p = V(sx * (X_BR + L.BRK["t"]), A.AX + yy, sz * (Z_WH + zz))
            iv = add("Civata M3x6 (motor %s %d)" % (k, i), "Tahrik", vida912(3, 6, p, V(-sx, 0, 0)), "Baglanti", "Celik 8.8",
                     kod="M3x6 DIN 912", renk="celik", patlat=(sx * 100, -40, sz * 40))
            bag("Motor - braket (%s, delik %d)" % (k, i), "dis", dict(vida=iv, govde=[ibr], dis=im),
                dict(d=3, kavrama=6 - L.BRK["t"], delik=L.JGB["delik_derin"]), temas=[(iv, ibr), (ibr, im)],
                eksen=(p, V(-sx, 0, 0), [(iv, 1.5), (im, 1.5)]), aciklama="reduktor on yuzu M3 dis (O31 daire), 4,5 mm kavrama")
        # teker -> kaplin: M4x16 + pul, teker gobek gogsunden kaplinin M4 disine
        xg = X_WH - A.TEKER_W / 2 + L.TEK["yuva_derin"] + L.TEK["gogus"]
        p = V(sx * xg, A.AX, sz * Z_WH)
        iw = add("Pul M4 (teker %s)" % k, "Tahrik", pul(4, p, V(sx, 0, 0)), "Baglanti", "Celik", kod="M4 DIN 125 pul", renk="celik",
                 patlat=(sx * 200, -40, sz * 40))
        pb = p + V(sx * A.WASH125[4][2], 0, 0)
        iv = add("Civata M4x16 (teker %s)" % k, "Tahrik", vida912(4, 16, pb, V(-sx, 0, 0)), "Baglanti", "Celik 8.8", kod="M4x16 DIN 912",
                 renk="celik", patlat=(sx * 220, -40, sz * 40))
        kav = 16 - A.WASH125[4][2] - L.TEK["gogus"] - 0.0
        bag("Teker - kaplin (%s)" % k, "dis", dict(vida=iv, pul=iw, govde=[it], dis=ik),
            dict(d=4, kavrama=kav, delik=L.KAP["m4_derin"]), temas=[(iw, it), (iv, iw), (ik, it)],
            eksen=(p, V(-sx, 0, 0), [(iv, 2.0), (ik, 2.0)]), aciklama="altigen kaplin teker yuvasina 17,5 mm girer, M4 eksenel vida")
        bag("Kaplin - motor mili (%s)" % k, "mil", dict(govde=[ik], mil=im), dict(d=6, kavrama=L.JGB["sh_l"] - 2.0 - 1.5 + 2.0 - 2.0),
            temas=[], eksen=(V(sx * X_BR, A.AX, sz * Z_WH), V(sx, 0, 0), [(ik, 3.05), (it, 2.25)]),
            aciklama="O6 D mil kaplina 11,5 mm; kaplinin set vidalari mil duzlugune (cizilmedi)")
log("tahrik")

# ====================================================================== 4) AKU + KAYIS + TAKOZ
AK = T["aku"]
AKU = add("Aku LiFePO4 12,8 V (yatik)", "Guc", tasi(aku_local(), *AK["merkez"]), "Satin", "LiFePO4",
          kod="LiFePO4 12,8 V 24 Ah (yuva 181 x 77 x 167)", renk="aku", patlat=(0, 0, -330), kutle=AK["kutle_g"], not_=AK["not_"])
ya1 = AK["merkez"][1] + AK["olcu"][1]
for z in T["kayis_z"]:
    z0, z1 = z - T["kayis_en"] / 2, z + T["kayis_en"] / 2
    dis = box(-(KAYIS_X[0] + 0.25 + T["kayis_t"]), KAYIS_X[0] + 0.25 + T["kayis_t"], y0p - T["kayis_t"], ya1 + 0.2 + T["kayis_t"], z0, z1)
    ic = box(-(KAYIS_X[0] + 0.25), KAYIS_X[0] + 0.25, y0p, ya1 + 0.2, z0 - 1, z1 + 1)
    add("Aku kayisi 25 mm (z %+.0f)" % z, "Guc", dis.cut(ic), "Satin", "Polyester", kod="25 mm cirt bant kayis (tahmini)", renk="siyah",
        patlat=(0, 30, -330), not_="plakadaki yariklardan gecip plaka altindan doner")
tk = T["takoz"]
takoz = kutu_r(tk["x"][0], tk["x"][1], tk["y"][0], tk["y"][1], tk["z"][0], tk["z"][1], 3.0, "Z")
for (x, z) in del_tak:
    takoz = takoz.cut(insert_hole(3, (x, tk["y"][0], z), UP, extra=2.5))
TAKOZ = add("Aku on takozu", "Guc", takoz.removeSplitter(), "Baski", "PETG", kod="Aku on takozu (PETG baski)", renk="petg",
            patlat=(0, 0, -200), not_="aku ile orta ara ray arasindaki 18 mm bosluk; kutuplar takozun ustunde serbest")
BASKI["Aku on takozu"] = dict(yukari=UP, yon="alt yuzu tablada")
for (x, z) in del_tak:
    ii = add("Isil gomme somun M3 (takoz x %+.0f)" % x, "Guc", insert(3, (x, tk["y"][0], z), UP), "Baglanti", "Pirinc", kod="M3 isil gomme somun",
             renk="pirinc", patlat=(0, -20, -200))
    iv = add("Civata M3x8 (takoz x %+.0f)" % x, "Guc", vida912(3, 8, (x, y0p, z), UP), "Baglanti", "Celik 8.8", kod="M3x8 DIN 912",
             renk="celik", patlat=(0, -60, -200))
    bag("Takoz - plaka (x %+.0f)" % x, "insert", dict(vida=iv, govde=[PLAKA], insert=ii, parca=TAKOZ),
        dict(d=3, kavrama=8 - tp, insert_boy=A.INSERT[3][1]), temas=[(iv, PLAKA), (TAKOZ, PLAKA)],
        eksen=(V(x, 0, z), UP, [(iv, 1.5), (ii, 1.5)]), aciklama="alttan M3x8, takoz icinde isil gomme somun")
log("aku")


# ====================================================================== 5) GUC ELEKTRONIGI (plaka ustu, burclu)
def kart_burclu(ad, grup, sh_local, cx, cz, y_alt, burc_L, delikler, d, af, malzeme_burc, kod_burc, govde_idx, kod, kutle, renk, pk,
                vida_ust=6, vida_alt=6, kalin=1.6, alt_kalin=None, not_=""):
    """Karti burc ustune koyar: burclar, ustten vida (PCB'den), alttan vida (govde plakasindan). Doner kart indeksi."""
    alt_kalin = alt_kalin if alt_kalin is not None else (A.PL_T if govde_idx == PLAKA else A.DECK_T)
    yk = y_alt + burc_L
    ik = add(ad, grup, tasi(sh_local, cx, yk, cz), "Satin", "PCB", kod=kod, renk=renk, patlat=pk, kutle=kutle, not_=not_)
    for j, (x, z) in enumerate(delikler):
        ib = add("Burc %s (%s %d)" % (kod_burc, ad, j), grup, burc(af, burc_L, (x, y_alt, z), UP, d), "Satin", malzeme_burc,
                 kod=kod_burc, renk="naylon" if malzeme_burc == "Naylon" else "pirinc", patlat=(pk[0], pk[1] - 15, pk[2]))
        iu = add("Vida M%sx%d (%s %d ust)" % (("%g" % d).replace(".", ","), vida_ust, ad, j), grup,
                 vida912(d, vida_ust, (x, yk + kalin, z), DOWN), "Baglanti", "Celik 8.8",
                 kod="M%sx%d DIN 912" % (("%g" % d).replace(".", ","), vida_ust), renk="celik", patlat=(pk[0], pk[1] + 25, pk[2]))
        ia = add("Vida M%sx%d (%s %d alt)" % (("%g" % d).replace(".", ","), vida_alt, ad, j), grup,
                 vida912(d, vida_alt, (x, y_alt - alt_kalin, z), UP), "Baglanti", "Celik 8.8",
                 kod="M%sx%d DIN 912" % (("%g" % d).replace(".", ","), vida_alt), renk="celik", patlat=(pk[0], pk[1] - 60, pk[2]))
        bag("%s - burc %d" % (ad, j), "burc_kart", dict(vida=iu, vida_alt=ia, burc=ib, govde=[govde_idx], kart=ik),
            dict(d=d, kavrama=vida_ust - kalin, kavrama_alt=vida_alt - alt_kalin, burc_L=burc_L,
                 vida_arasi=burc_L - (vida_ust - kalin) - (vida_alt - alt_kalin)),
            temas=[(ib, govde_idx), (ib, ik), (iu, ik), (ia, govde_idx)], eksen=(V(x, 0, z), UP, [(iu, d / 2), (ia, d / 2), (ib, d / 2)]),
            aciklama="kart %s burc ustunde; ustten ve alttan vida" % kod_burc)
    return ik


BTS_I = []
for (bx, bz), ad in zip(T["bts"], ("sol", "sag")):
    d = [(bx + dx * L.BTS["dk"], bz + dz * L.BTS["dk"]) for dx in (-1, 1) for dz in (-1, 1)]
    BTS_I.append(kart_burclu("BTS7960 motor surucu %s" % ad, "Guc", bts_local(), bx, bz, A.Y_RAIL0, T["bts_burc"], d, 3, 5.5, "Naylon",
                             "M3x8 naylon burc", PLAKA, "BTS7960B 43 A (IBT-2)", L.BTS["kutle_g"], "pcb_k", (bx * 0.6, 120, 120),
                             not_="%s motor cifti (on + arka paralel)" % ad))
XL_I = []
for (x, z, gorev) in T["xl"]:
    d = [(x + dx * L.XL["dx"] / 2, z + dz * L.XL["dz"] / 2) for dx in (-1, 1) for dz in (-1, 1)]
    XL_I.append(kart_burclu("XL4016 %s" % gorev, "Guc", xl_local(), x, z, A.Y_RAIL0, T["xl_burc"], d, 3, 5.5, "Naylon", "M3x8 naylon burc",
                            PLAKA, "XL4016 8 A DC-DC dusurucu", L.XL["kutle_g"], "pcb_m", (x * 0.6, 120, z * 0.3), not_=gorev))

# --- guc paneli (arka kat ustu): sigorta kutusu, role, ana sigorta yuvasi (tahmini zarflar), ana anahtar (etek plakasi alti)
cx, cz = SK["merkez"]
lx, lz, ly = SK["olcu"]
sk = zarf(cx - lx / 2 + 10, cx + lx / 2 - 10, YD1, YD1 + ly, cz - lz / 2, cz + lz / 2, 3.0)
for sx in (-1, 1):
    k0, k1 = sorted((cx + sx * (lx / 2 - 10), cx + sx * lx / 2))
    kul = box(k0, k1, YD1, YD1 + 3.0, SK["delik_z"] - 8, SK["delik_z"] + 8).cut(delik_y(cx + sx * SK["delik_x"], SK["delik_z"], A.CLEAR[4], YD1, 3.0))
    sk = sk.fuse(kul)
SKI = add("Sigorta kutusu 6 yollu (tahmini zarf)", "Guc", sk.removeSplitter(), "Satin", "Plastik", kod="6 yollu bicak sigorta kutusu",
          renk="koyu", patlat=(0, 330, -200), kutle=120.0, not_="olcu bilinmiyor: zarf 105 x 60 x 35 tahmini, kumpasla olculecek")
for sx in (-1, 1):
    x = cx + sx * SK["delik_x"]
    yb = YD1 + 3.0 + A.WASH125[4][2]
    iw = add("Pul M4 (sigorta kutusu %s)" % SX(sx), "Guc", pul(4, (x, YD1 + 3.0, SK["delik_z"]), UP), "Baglanti", "Celik", kod="M4 DIN 125 pul",
             renk="celik", patlat=(0, 360, -200))
    iv = add("Civata M4x16 (sigorta kutusu %s)" % SX(sx), "Guc", vida912(4, 16, (x, yb, SK["delik_z"]), DOWN), "Baglanti", "Celik 8.8",
             kod="M4x16 DIN 912", renk="celik", patlat=(0, 380, -200))
    isn = add("Somun M4 (sigorta kutusu %s)" % SX(sx), "Guc", nut(4, (x, y0d, SK["delik_z"]), DOWN, kind="985"), "Baglanti", "Celik",
              kod="M4 DIN 985 naylon somun", renk="celik", patlat=(0, 200, -200))
    uc = yb - 16
    bag("Sigorta kutusu - guc paneli (%s)" % SX(sx), "somun", dict(vida=iv, pul=iw, somun=isn, govde=[SKI, KAT_AR]),
        dict(d=4, uc_disari=(y0d - A.NUT985[4][1]) - uc, kavrama=y0d - max(uc, y0d - A.NUT985[4][1])),
        temas=[(iw, SKI), (iv, iw), (SKI, KAT_AR), (isn, KAT_AR)], eksen=(V(x, 0, SK["delik_z"]), UP, [(iv, 2.0), (isn, 2.0)]),
        aciklama="kulaktan M4x16 + kontra somun; somun akunun disinda (z -215)")
rx, rz = RL["merkez"]
rl = zarf(rx - 15, rx + 15, YD1, YD1 + RL["olcu"][2], rz - 15, rz + 15, 2.0)
kul = box(rx - 6, rx + 6, YD1, YD1 + 3.0, rz - 15 - 10, rz - 15 + 0.5).cut(delik_y(RL_DEL[0], RL_DEL[1], A.CLEAR[4], YD1, 3.0))
RLI = add("Role 12 V 40 A + soket (tahmini zarf)", "Guc", rl.fuse(kul).removeSplitter(), "Satin", "Plastik",
          kod="ISO mini role 12 V 40 A + soket (BOM'da yok)", renk="koyu", patlat=(-60, 330, -100), kutle=35.0,
          not_="acil stop NC kontagi bobini keser -> motor + servo gucu duser (Pi acik kalir)")
iw = add("Pul M4 (role)", "Guc", pul(4, (RL_DEL[0], YD1 + 3.0, RL_DEL[1]), UP), "Baglanti", "Celik", kod="M4 DIN 125 pul", renk="celik",
         patlat=(-60, 360, -100))
iv = add("Civata M4x16 (role)", "Guc", vida912(4, 16, (RL_DEL[0], YD1 + 3.0 + A.WASH125[4][2], RL_DEL[1]), DOWN), "Baglanti", "Celik 8.8",
         kod="M4x16 DIN 912", renk="celik", patlat=(-60, 380, -100))
isn = add("Somun M4 (role)", "Guc", nut(4, (RL_DEL[0], y0d, RL_DEL[1]), DOWN, kind="985"), "Baglanti", "Celik", kod="M4 DIN 985 naylon somun",
          renk="celik", patlat=(-60, 200, -100))
uc = YD1 + 3.0 + A.WASH125[4][2] - 16
bag("Role soketi - guc paneli", "somun", dict(vida=iv, pul=iw, somun=isn, govde=[RLI, KAT_AR]),
    dict(d=4, uc_disari=(y0d - A.NUT985[4][1]) - uc, kavrama=y0d - max(uc, y0d - A.NUT985[4][1])),
    temas=[(iw, RLI), (iv, iw), (RLI, KAT_AR), (isn, KAT_AR)], eksen=(V(RL_DEL[0], 0, RL_DEL[1]), UP, [(iv, 2.0), (isn, 2.0)]),
    aciklama="soket kulagindan M4 + kontra somun; somun uzun rayin ustunde (akunun disinda)")
AS = T["ana_sigorta"]
ax_, az_ = AS["merkez"]
ASI = add("Ana sigorta yuvasi 30 A (tahmini zarf)", "Guc", zarf(ax_ - AS["olcu"][0] / 2, ax_ + AS["olcu"][0] / 2, YD1, YD1 + AS["olcu"][2],
                                                            az_ - AS["olcu"][1] / 2, az_ + AS["olcu"][1] / 2, 4.0),
          "Satin", "Plastik", kod="Kablolu kapakli bicak sigorta yuvasi 12 AWG + 30 A", renk="kirmizi", patlat=(60, 330, -100), kutle=40.0,
          not_="kablo uzerinde; panele 2 kablo bagi ile (cizilmedi)")
AA = T["ana_anahtar"]
aax, aaz = AA["merkez"]
ya_ust = A.Y_COV1 - A.KABUK_T - 3.0
AAI = add("Ana anahtar ASW-A01 govdesi (tahmini zarf)", "Guc", zarf(aax - 25, aax + 25, ya_ust - AA["olcu"][2], ya_ust, aaz - 25, aaz + 25, 4.0),
          "Satin", "Plastik", kod="ASW-A01 100 A aku ayirici", renk="kirmizi", patlat=(-60, 420, -200), kutle=150.0,
          not_="oneri: etek ust plakasinin altinda, acil stobun aynasi; kabukta delik yok (2. asama). Olcu bilinmiyor (zarf)")
add("Ana anahtar dugmesi (gosterim, kabuk deligi gerekir)", "Referans",
    Part.makeCylinder(20.0, 22.0, V(aax, A.Y_COV1, aaz), UP), "Referans", "-", kod="(gosterim)", renk="kirmizi", patlat=(-60, 470, -200),
    kutle=0.0)
log("guc")

# ====================================================================== 6) ELEKTRONIK KATI (on)
PI_I = kart_burclu("Raspberry Pi 5 8GB + Active Cooler", "Elektronik", pi5_local(), PI_C[0], PI_C[1], YD1, T["pi"]["burc"], pi_del, 2.5, 5.0,
                   "Pirinc", "M2,5x8 pirinc burc", KAT_ON, "Raspberry Pi 5 8GB + resmi Active Cooler", L.PI["kutle_g"], "pcb_y",
                   (-80, 120, 40), vida_ust=5, vida_alt=8,
                   not_="SD yuvasi -X kenarinda (x -135,5, z 80); USB/Ethernet +X'e, micro HDMI + USB-C -Z kenarinda; fan ustu ~55 mm acik")
PCA_I = kart_burclu("PCA9685 servo surucu", "Elektronik", pca_local(), PCA_C[0], PCA_C[1], YD1, T["pca"]["burc"], pca_del, 2.5, 5.0, "Pirinc",
                    "M2,5x8 pirinc burc", KAT_ON, "PCA9685 16 kanal (Adafruit 815 delik duzeni)", L.PCA["kutle_g"], "pcb_m",
                    (80, 120, 60), vida_ust=5, vida_alt=8)
BNO_I = kart_burclu("BNO055 IMU", "Elektronik", bno_local(), BNO_C[0], BNO_C[1], YD1, T["bno"]["burc"], bno_del, 2.5, 5.0, "Pirinc",
                    "M2,5x8 pirinc burc", KAT_ON, "BNO055 9 eksen (Adafruit 2472 delik duzeni; eldeki muadil olculecek)", L.BNO["kutle_g"],
                    "pcb_m", (0, 120, 60), vida_ust=5, vida_alt=8)
PERF_I = kart_burclu("ESP32 tasiyici kart (pertinaks)", "Elektronik", perf_local(), ESP_C[0], ESP_C[1], YD1, T["esp"]["burc"], perf_del, 3,
                     5.5, "Naylon", "M3x8 naylon burc", KAT_ON, "Delikli pertinaks 70 x 50 + 2x 15'li disi header (tahmini; BOM'da yok)",
                     L.PERF["kutle_g"], "pcb_y", (80, 120, 20), vida_ust=6, vida_alt=8)
y_esp = YD1 + T["esp"]["burc"] + L.PERF["t"] + 8.5
ESP_I = add("ESP32 DevKit 30 pin", "Elektronik", tasi(esp_local(), ESP_C[0], y_esp, ESP_C[1]), "Satin", "PCB", kod="ESP32-WROOM-32 DevKit 30 pin",
            renk="pcb_k", patlat=(80, 170, 20), kutle=L.ESP["kutle_g"], not_="disi header'a takili (pin 6 mm)")
bag("ESP32 - tasiyici header", "gecme", dict(govde=[PERF_I], kart=ESP_I), dict(d=0.64, kavrama=6.0), temas=[(ESP_I, PERF_I)],
    aciklama="ESP32 pinleri 15'li disi header'lara 6 mm gecer")
yam = YD1 + 1.0
add("Kopuk bant (amfi)", "Elektronik", box(AMP_C[0] - L.AMP["l"] / 2, AMP_C[0] + L.AMP["l"] / 2, YD1, yam, AMP_C[1] - L.AMP["w"] / 2,
                                          AMP_C[1] + L.AMP["w"] / 2), "Satin", "Kopuk", kod="Cift tarafli kopuk bant 1 mm", renk="siyah",
    patlat=(-50, 100, 40))
AMP_I = add("MAX98357A I2S amfi", "Elektronik", tasi(amp_local(), AMP_C[0], yam, AMP_C[1]), "Satin", "PCB", kod="Adafruit MAX98357A",
            renk="pcb_m", patlat=(-50, 140, 40), kutle=L.AMP["kutle_g"], not_="montaj deligi yok: kopuk bant")
log("elektronik kati")

# ====================================================================== 7) SONARLAR + TUTUCULAR, ACIL STOP
SN = A.SONAR
ZF = T["sonar_on_z"]
ZB = A.L0 / 2                     # on ara rayin on yuzu (250)
YS = SN["y"]


def sonar_tutucu(s, kulak):
    sh = box(s - 26, s + 26, 96, 124, ZB, ZB + 3)
    sh = sh.cut(box(s - 19, s + 19, 103, 117, ZB - 1, ZB + 4))
    ust = box(s - 22, s + 22, 118.5, 124, ZB + 3, 257.6).cut(box(s - 23, s + 23, 118.4, 120.3, 254.3, 256.1))
    sh = sh.fuse(ust)
    for (a, b) in ((s - 22, s - 6.5), (s + 6.5, s + 22)):
        alt = box(a, b, 96, 101.5, ZB + 3, 257.6).cut(box(a - 1, b + 1, 99.7, 101.6, 254.3, 256.1))
        sh = sh.fuse(alt)
    for xe in kulak:
        x0 = min(xe - 5, s + (26 if xe > s else -26))
        x1 = max(xe + 5, s + (26 if xe > s else -26))
        sh = sh.fuse(box(x0, x1, 104, 125, ZB, ZB + 3))
    for xe in kulak:
        sh = sh.cut(Part.makeCylinder(A.CLEAR[6] / 2, 6, V(xe, A.RAY_YC, ZB - 1), V(0, 0, 1)))
    return sh.removeSplitter()


for s in SN["x"]:
    nm = "orta" if abs(s) < 1 else SX(s)
    kulak = (s - 31, s + 31) if abs(s) < 1 else ((s - 31,) if s > 0 else (s + 31,))
    isn_ = add("Sonar HC-SR04 (%s)" % nm, "Sensor", tasi(sonar_local(), s, YS, ZF - L.SONAR["t"]), "Satin", "PCB", kod="HC-SR04",
               renk="pcb_m", patlat=(s * 0.3, 0, 140), kutle=L.SONAR["kutle_g"], not_="transduserler etek deliklerinden (O17)")
    ad_t = "Sonar tutucu %s" % nm
    itu = add(ad_t, "Sensor", sonar_tutucu(s, kulak), "Baski", "PETG", kod="Sonar tutucu (PETG baski)", renk="petg",
              patlat=(s * 0.3, 0, 90), not_="PCB yandan raylara surulur; on ara rayin on kanalina M6")
    BASKI[ad_t] = dict(yukari=V(0, 0, 1), yon="arka yuzu (ray tarafi) tablada")
    for xe in kulak:
        pb = V(xe, A.RAY_YC, ZB + 3)
        iv = add("Civata M6x14 ISO 7380 (sonar %s x %+.0f)" % (nm, xe), "Sensor", vida7380(6, 14, pb, V(0, 0, -1)), "Baglanti", "Celik",
                 kod="M6x14 ISO 7380", renk="celik", patlat=(s * 0.3, 0, 130))
        ih = add("Cekic somun M6 (sonar %s x %+.0f)" % (nm, xe), "Sensor", hammer_nut((xe, A.RAY_YC, ZB - A.LIP), V(0, 0, 1), V(0, 1, 0), d=6),
                 "Baglanti", "Celik", kod="M6 cekic somun, kanal 10", renk="celik", patlat=(s * 0.3, 0, 40))
        uc = 14 - 3
        bag("Sonar tutucu %s - on ara ray (x %+.0f)" % (nm, xe), "kanal", dict(vida=iv, somun=ih, govde=[itu]),
            dict(d=6, uc=uc, somun_ust=A.LIP + 5.0, taban=A.KANAL_TABAN, kavrama=min(uc, A.LIP + 5.0) - A.LIP),
            temas=[(iv, itu)], eksen=(pb, V(0, 0, -1), [(iv, 3.0), (ih, 3.0)]),
            aciklama="bombe basli M6 (etek duvarina 3,2 mm), on ara rayin on kanalinda cekic somun")
    bag("Sonar - tutucu (%s)" % nm, "ray", dict(govde=[itu], kart=isn_), dict(d=1.6, kavrama=1.5), temas=[],
        aciklama="PCB ust ve alt kenari tutucunun raylarinda (arka dayama 0,1, on dudak 1,5 mm); transduserler etek deliginde")
ES = A.ACIL_STOP
ust, alt = acil_stop_local()
ESU = add("Acil stop mantari + bilezik", "Sensor", tasi(ust, ES["x"], A.Y_COV1, ES["z"]), "Satin", "Plastik", kod="Emas B200E60 acil stop",
          renk="kirmizi", patlat=(0, 120, -60), kutle=35.0, not_=T["acil_stop"])
ESA = add("Acil stop kontak govdesi (1NC)", "Sensor", tasi(alt, ES["x"], A.Y_COV1, ES["z"]), "Satin", "Plastik", kod="Emas B200E60 kontak blogu",
          renk="koyu", patlat=(0, 60, -60), kutle=50.0, not_="etek ust plakasinin O22,4 deliginde; bilezik plaka ustune oturur")
log("sensor")

# ====================================================================== 8) KABLO YOLU SEMASI (Referans: taramaya ve kutleye girmez)
ex, ez = ES["x"], ES["z"]
SKC = V(cx, YD1 + 36, cz)
YOL += [
    ("12 V ana hat: aku + -> XT60 -> ana sigorta 30 A -> ana anahtar -> sigorta kutusu", "kirmizi",
     [(-65.5, 133, -29), (-62, 160, -29), (-60, 190, -30), (40, 190, -70), (ax_, 192, az_ + 30), (ax_, 192, az_ - 30), (60, 195, -175),
      (aax, 220, aaz + 25), (aax, 214, aaz - 10), (-20, 196, -215), (cx - 30, YD1 + 36, cz)]),
    ("Toprak: aku - -> WAGO yildiz noktasi (guc paneli) -> tum donusturuculer", "siyah",
     [(65.5, 133, -29), (62, 160, -29), (60, 190, -30), (30, 186, -60), (-20, 186, -90)]),
    ("Motor 12 V: F1 20 A -> role -> WAGO -> BTS7960 sol/sag -> motor kablo delikleri -> 4 motor", "turuncu",
     [(cx - 40, YD1 + 36, cz), (rx, YD1 + 46, rz), (-60, 182, -30), (-60, 150, 0), (-50, 145, 60), (-67.5, 145, 140), (-80, 120, 196),
      (-80, 90, 200), (-100, 85, 185)]),
    ("Motor 12 V sag kol + arka motorlar (plaka altindan z 36 deliginden)", "turuncu",
     [(-50, 145, 60), (50, 145, 60), (67.5, 145, 140), (80, 120, 196), (80, 88, 200), (100, 85, 185), (80, 120, 140), (80, 112, 40),
      (80, 88, 36), (80, 87, -150), (100, 85, -185)]),
    ("Servo 6 V: F1 -> role -> WAGO -> XL4016 servo -> PCA9685 V+ -> direk arka yuzu -> omuz / kafa", "sari",
     [(rx, YD1 + 46, rz), (-60, 182, -30), (-30, 150, 40), (0, 130, 150), (0, 140, 170), (30, 182, 150), (PCA_C[0], 200, PCA_C[1]),
      (40, 205, 30), (25, 230, -26), (0, 262, -26), (0, 400, -26), (0, 900, -26), (60, 955, -26), (100, 955, -26)]),
    ("Servo kablolari sola ve kafaya (direk ustu dagitim)", "sari", [(0, 900, -26), (-60, 955, -26), (-100, 955, -26), (0, 900, -26),
                                                                      (0, 975, -30), (0, 1010, -10)]),
    ("Pi 5,1 V: F3 10 A -> XL4016 Pi -> Pi USB-C", "mavi",
     [(cx - 20, YD1 + 36, cz), (-62, 182, -30), (-55, 150, 20), (T["xl"][0][0], 125, T["xl"][0][1]), (-40, 150, 150), (-40, 185, 160),
      (-100, 190, 58)]),
    ("Cevre 5 V: F4 5 A -> XL4016 cevre -> ESP32 / Nextion / 7in LCD / sensorler", "mavi",
     [(cx, YD1 + 36, cz), (62, 182, -30), (55, 150, 20), (T["xl"][1][0], 125, T["xl"][1][1]), (40, 150, 150), (40, 185, 160),
      (ESP_C[0], 200, ESP_C[1]), (30, 205, 40), (24, 230, 26), (24, 262, 26), (24, 700, 26), (24, 800, 60)]),
    ("Acil stop: F5 -> mantar (NC) -> role bobini", "yesil",
     [(cx + 30, YD1 + 36, cz), (ex, 205, ez), (ex, 214, ez), (ex - 10, 205, ez + 20), (rx, YD1 + 46, rz)]),
    ("Sinyal: sonar x3 -> ESP32 (on ara ray ustunden)", "mor",
     [(-79.4, 95, 254), (-79.4, 90, 240), (-60, 140, 240), (0, 150, 240), (60, 150, 235), (ESP_C[0], 190, 100)]),
    ("Sinyal: enkoder + BTS PWM/EN -> ESP32; Pi <-> ESP32 USB", "mor",
     [(-67.5, 140, 140), (-30, 160, 160), (ESP_C[0], 190, ESP_C[1]), (PI_C[0] + 42, 195, PI_C[1] + 15)]),
    ("Pi -> kafa: 2x HDMI (7in LCD), kamera FPC, USB mikrofon, hoparlor (direk on yuzu)", "beyaz",
     [(PI_C[0] + 10, 190, PI_C[1] - 30), (-30, 205, 30), (-24, 230, 26), (-24, 262, 26), (-24, 900, 26), (-24, 975, 30), (0, 1010, 20)]),
]


def tup(pts, r=2.5):
    pts = [V(*p) for p in pts]
    parca = [Part.makeSphere(r, p) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        if (b - a).Length > 1e-6:
            parca.append(Part.makeCylinder(r, (b - a).Length, a, (b - a).normalize()))
    s = parca[0].fuse(parca[1:])
    return s.removeSplitter()


for i, (devre, renk, pts) in enumerate(YOL):
    add("Kablo yolu %d: %s" % (i + 1, devre), "Referans", tup(pts), "Referans", "-", kod="(gosterim)", renk="k_" + renk,
        patlat=(0, 0, 0), kutle=0.0)
log("kablo yolu")

# ====================================================================== 9) kutle ve merkez
for p in P:
    p["shape"] = pisir(p["shape"])
    sh = p["shape"]
    p["hacim"] = sh.Volume
    p["kati"] = len(sh.Solids)
    p["merkez"] = sh.Solids[0].CenterOfMass if p["kati"] == 1 else sh.BoundBox.Center
    p["bb"] = sh.BoundBox
    if p["kutle_sabit"] is not None:
        p["kutle"] = p["kutle_sabit"]
    elif p["tur"] == "Baski":
        p["kutle"] = p["hacim"] / 1000.0 * RHO["PETG"] * DOLULUK
    else:
        p["kutle"] = p["hacim"] / 1000.0 * RHO[p["malzeme"]]
KABLO_PAY = dict(kutle_g=400.0, merkez=(0.0, 150.0, -60.0),
                 not_="kablo payi (tahmini): 12 AWG ~4 m, 18 AWG ~10 m, servo uzatma ~8 m, Dupont, XT60, WAGO; parca listesine girmez")
log("parca", len(P), "toplam %.0f g" % sum(p["kutle"] for p in P))
