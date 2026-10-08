# Kafa modulu (boyun + pan + tilt + kafa) - PARCALAR, kutle ve kinematik (FreeCAD 1.1, Part)
# Import edilebilir: kafa_montaj.py (kontroller + kayit); 2. asamada carpisma / ana montaj bunu kullanir.
# Koordinat (kafa yereli, arayuz.MODULLER["kafa"]): orijin = traversin ust yuzu ortasi (global 0, 975, 0), X sag, Y yukari,
# Z ileri. Pan ekseni yerel Y ekseni (x = z = 0), tilt ekseni X'e paralel (y = 130, z = 25). Ev pozu: duz bakis.
# Arayuz olculeri: ../arayuz.py KAFA. V3 kaynak: rc:782-800 (kafa grubu), rc:471-484 (head_shell 210x180x150),
# rc:636-642 (visor), rc:374-396 (7" LCD, kamera). Iskelet ve kabuk geometrisi degismez (kabuk ust kapakta R62 aciklik).
#
# Yapi
#   Govde (traverse sabit): boyun plakasi (3 mm Al; 2x M6 + cekic somun traversin ust kanalina) -> servo yuvasi (PETG;
#       pan MG996R'yi kulaklarindan tasir, M3 + isil gomme somun) -> rulman yuvasi (PETG; iki 6808-2RS, 4x M3 ile servo
#       yuvasina). Kafa kutlesi ve devrilme momenti 6808 ciftinde (ust rulman eksenel yuku tasir) -> pan servosu yalniz
#       dondurur. Servo yuvasinda arka kablo kanali + alt pencere (kablolar R62 halkasindan govdeye iner).
#   Pan (pan ekseninde doner): pan horn -> boyun mili (PETG; ici bos O32, alt diski horn'a 4x M3; 6808 ic bileziklerine
#       oturur, omuzu ust rulmanin ic bileziginde) -> egme catali (PETG; mil flansina 4x M3 + isil gomme somun) -> tilt
#       MG996R (govdesi catalda, mil +X) + karsi yatak pimi (625ZZ ic bilezigi M5 civatayla catalin sol duvarina sikilir).
#   Kafa (Pan * tilt): tilt horn -> kafa iskeleti (PETG; sag yanak horn'a 4x M3, sol yanakta 625ZZ dis bilezigi; ustte
#       kafa tablasi) -> on (yuz) ve arka kafa kabugu (tablaya 4x M3 ISO 7380 + isil gomme somun) -> 7" LCD (on kabukta
#       ekran yuvasi, 4x M3), siyah akrilik vizor (VHB bant), Camera Module 3 (on kabukta, 4x M2).
import os, sys, math, time

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from kafa_lib import *   # noqa
import arayuz as A

t0 = time.time()
K = A.KAFA
YT, ZT = K["tilt_nokta"][1], K["tilt_nokta"][2]      # tilt ekseni (130, 25)

# ---------------------------------------------------------------- olcu zinciri (Y: asagidan yukari, yerel)
Y_PL = K["boyun_plaka"]["t"]               # 3: plaka ust yuzu
Y_KULAK_T = 8.0                            # servo yuvasi kulak (flans) ust yuzu
Y_PK = 41.6                                # pan servosu kasa ustu (taban 5,0 -> plakaya 2 mm)
Y_PT = Y_PK - MG["H"]                      # 5.0
Y_EAR = (Y_PK - MG["TAB_TOP"] - MG["TAB_T"], Y_PK - MG["TAB_TOP"])   # 31.6 / 34.1 kulak yuzleri
Y_LEDGE0 = Y_EAR[0] - 7.0                  # 24.6 kulak tablasi alti (7 mm: M3 isil gomme somun 5,7)
Y_BLK = 46.0                               # servo yuvasi ust yuzu = rulman yuvasi alt yuzu
Y_HORN = (Y_PK + HORN_MG["Z0"], Y_PK + HORN_MG["Z1"])   # 44.6 / 47.9
Y_DISK = (Y_HORN[1], Y_HORN[1] + 5.0)      # 47.9...52.9 boyun mili alt diski
Y_PEN = (53.0, 63.0)                       # boyun mili kablo penceresi
Y_R1 = (64.0, 71.0)                        # alt 6808
Y_R2 = (75.0, 82.0)                        # ust 6808 (eksenel yuk)
Y_UST = Y_R2[1]                            # 82 rulman yuvasi ust yuzu
Y_OMUZ = (82.0, 84.0)                      # mil omuzu (ust rulman ic bileziginde)
Y_KONI = (84.0, 92.0)                      # 45 derece gecis
Y_FL = (92.0, 96.0)                        # mil flansi (catal civatalari)
Y_CB = (96.0, 99.0)                        # catal tabani
R_CAP = 30.0                               # rulman yuvasi dis yaricapi
R_ODA = 27.5                               # kablo odasi (halka) ic yaricapi
X_TB = -12.7                               # tilt servosu taban yuzu (mil +X)
X_TK = X_TB + MG["H"]                      # 23.9 kasa ustu
X_TH = (X_TK + HORN_MG["Z0"], X_TK + HORN_MG["Z1"])   # 26.9 / 30.2 tilt horn
X_TKUL = (X_TB + 26.6, X_TB + 26.6 + MG["TAB_T"])     # 13.9 / 16.4 kulak yuzleri
X_EP = (X_TKUL[0] - 5.0, X_TKUL[0])        # 8.9...13.9 catal kulak plakasi
X_SAG = (X_TH[1], X_TH[1] + 5.0)           # 30.2...35.2 sag yanak (horn'a bagli)
X_SOL = (-35.2, -24.2)                     # sol yanak (625ZZ yuvasi)
X_RUL = (-29.2, -24.2)                     # 625ZZ
X_DUVAR = (-23.2, -13.2)                   # catal sol duvari (M5 isil gomme somun)
Y_TABLA = (178.0, 183.0)                   # kafa tablasi
KB = K["kafa_kutu"]                        # 210 x 180 x 150
KX, KY0, KY1 = KB[0] / 2, K["kafa_alt_y"], K["kafa_alt_y"] + KB[1]          # 105, 95, 275
KZ0, KZ1 = 10.0 - KB[2] / 2, 10.0 + KB[2] / 2                               # -65, 85 (rc: merkez z 10)
KT = 2.5                                   # kabuk duvari (rc:472 V3 2,5)
Z_DIKIS = 30.0                             # on / arka kabuk ayrimi (LCD arkasi 64,5)
Z_LCD = KZ1 - KT - 3.0                     # 79.5 LCD panel on yuzu (3 mm ekran yuvasi kenari onunde)
Y_LCD = KY0 + 84.0                         # 179 LCD merkezi (rc:790)
Y_CAM = 258.0                              # kamera lens ekseni (LCD kulaklarinin 17 mm ustu; rc 247 LCD kulagiyla cakisirdi)
Z_CAM = Z_LCD - LCD["panel_t"] - LCD["arka_t"] + 1.6   # 76.0 kamera PCB on yuzu (LCD kulak on yuzu ile ayni)
ACIKLIK = dict(x=42.0, z=(-56.0, 64.0), r=15.0)          # kafa alt duvarinda boyun acikligi (kafa_montaj taramasi)

assert abs(K["pan_nokta"][1] - Y_HORN[0]) < 1e-9 and abs(K["tilt_nokta"][0] - X_TH[0]) < 1e-9
assert abs(KY1 - A.HEAD_UP) < 1e-9


def gp(local, m):
    return m.multVec(V(*local))


M_P = matris((1, 0, 0), (0, 0, -1), (0, 1, 0), (0, Y_PK, 0))        # pan servosu: mil +Y, govde one (+Z)
M_T = matris((0, 1, 0), (0, 0, 1), (1, 0, 0), (X_TK, YT, ZT))       # tilt servosu: mil +X, govde arkaya (-Z)

P = []


def add(ad, grup, shape, tur, malzeme, kod=None, renk="gri", patlat=(0, 0, 0), not_="", doluluk=None):
    P.append(dict(ad=ad, grup=grup, shape=shape, tur=tur, malzeme=malzeme, kod=kod or ad, renk=renk,
                  patlat=list(patlat), not_=not_, doluluk=doluluk))
    return len(P) - 1


BAG = []     # baglanti tanimlari (kafa_montaj kontrol eder)
EP_G = (0, -40, 0)       # patlatma: govde asagi
EP_P = (0, 40, 0)
EP_K = (0, 140, 0)

# ====================================================================== GOVDE (traverse sabit)
# --- boyun plakasi (3 mm Al): V3 70x70 + iki yan kulak, 2x M6 traversin ust kanalina (kanal z = 0)
BP = K["boyun_plaka"]
pl = yuv_dikdortgen_y(BP["x"][0], BP["x"][1], BP["z"][0], BP["z"][1], 6.0, 0.0, Y_PL)
pl = pl.fuse(yuv_dikdortgen_y(-BP["kulak_x"], BP["kulak_x"], -BP["kulak_z"], BP["kulak_z"], 5.0, 0.0, Y_PL))
for sx in (1, -1):
    pl = pl.cut(cyl(CLEAR[6] / 2, (sx * BP["civata_x"], -1, 0), (sx * BP["civata_x"], Y_PL + 1, 0)))
I_PLAKA = add("Boyun plakasi", "Govde", pl.removeSplitter(), "Imalat", "Aluminyum", kod="Boyun plakasi 3 mm Al (lazer/su jeti)",
              renk="alu", patlat=(0, -60, 0), not_="V3 70x70 (rc:647) + yan kulaklar; traversin ust kanalina 2x M6")

# --- servo yuvasi (PETG): blok + kulak flansi; icinde pan servosu, kulak tablasi (M3 isil gomme), kablo kanali
sy = yuv_dikdortgen_y(-30.0, 30.0, -30.0, 44.0, 8.0, Y_PL, Y_BLK)
sy = sy.fuse(yuv_dikdortgen_y(-48.0, 48.0, -10.0, 10.0, 5.0, Y_PL, Y_KULAK_T))
sy = sy.cut(box(-10.05, 10.05, Y_PL - 1, Y_EAR[0] + 0.1, -10.4, 30.7))            # govde cebi (alttan acik)
sy = sy.cut(box(-10.5, 10.5, Y_EAR[0], Y_BLK + 0.1, -18.6, 38.9))                 # kulak + pul + bas boslugu (ustten takilir)
sy = sy.cut(cyl(14.0, (0, 41.0, 0), (0, Y_BLK + 0.1, 0)))                         # pan horn boslugu
sy = sy.cut(box(-14.0, 6.0, 6.0, 40.0, -27.0, -19.2))                             # arka kablo kanali
sy = sy.cut(box(-14.0, 6.0, 40.0, Y_BLK + 0.1, -23.0, -10.4))                     # kanal ustu -> kablo odasi (r < 27,5)
sy = sy.cut(prizma([(40.0 - 0.01, -27.0), (40.0 - 0.01, -23.0), (44.0, -23.0)], "x", -14.0, 6.0))   # kanal tavani 45 derece
sy = sy.cut(box(-6.0, 4.0, 5.0, 14.0, -19.5, -10.3))                              # pan servosu kablosu -> kanal
sy = sy.cut(box(-6.0, 6.0, 6.0, 18.0, -31.0, -26.5))                              # alt kablo cikisi (arka, 12 genis)
PED, _ = mg_delikler()
DELIK_P = [gp((xx, yy, 0), M_P) for (xx, yy) in PED]
for q in DELIK_P:
    sy = sy.cut(insert_hole(3, (q.x, Y_EAR[0], q.z), (0, -1, 0)))
for sx in (1, -1):
    sy = sy.cut(cyl(CLEAR[6] / 2, (sx * BP["civata_x"], Y_PL - 1, 0), (sx * BP["civata_x"], Y_KULAK_T + 1, 0)))
LUG = [(24.0, 32.0), (-24.0, 32.0), (24.0, -24.0), (-24.0, -24.0)]               # rulman yuvasi baglanti kulaklari
for (x, z) in LUG:
    sy = sy.cut(insert_hole(3, (x, Y_BLK, z), (0, -1, 0)))
I_SY = add("Servo yuvasi", "Govde", sy.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(0, -45, 0),
           not_="pan servosu ustten girer, kulaklari 7 mm tablaya (M3 isil gomme); arkada kablo kanali ve alt cikis penceresi")

# --- rulman yuvasi (PETG): iki 6808-2RS; ust rulman ortadaki tablaya oturur (eksenel yuk), alt rulman pres gecme
ry = cyl(R_CAP, (0, Y_BLK, 0), (0, Y_UST, 0))
for (x, z) in LUG:
    rr = math.hypot(x, z)
    ux, uz = x / rr, z / rr
    nx, nz = -uz, ux
    pts = [((R_CAP - 3) * ux + 5.5 * nx, (R_CAP - 3) * uz + 5.5 * nz), (x + 5.5 * nx, z + 5.5 * nz),
           (x - 5.5 * nx, z - 5.5 * nz), ((R_CAP - 3) * ux - 5.5 * nx, (R_CAP - 3) * uz - 5.5 * nz)]
    ry = ry.fuse(prizma(pts, "y", Y_BLK, Y_BLK + 6.0)).fuse(cyl(5.5, (x, Y_BLK, z), (x, Y_BLK + 6.0, z)))
ry = ry.cut(cyl(R_ODA, (0, Y_BLK - 1, 0), (0, 62.0, 0)))                          # kablo odasi (halka)
ry = ry.cut(cyl(26.0, (0, 61.9, 0), (0, Y_R1[1], 0)))                             # alt 6808 yuvasi O52
ry = ry.cut(koni(26.0, 23.5, (0, Y_R1[1] - 0.001, 0), (0, Y_R1[1] + 2.5, 0)))      # tabla alti 45 derece (desteksiz)
ry = ry.cut(cyl(23.5, (0, Y_R1[1] + 2.4, 0), (0, Y_R2[0] + 0.01, 0)))
ry = ry.cut(cyl(26.0, (0, Y_R2[0], 0), (0, Y_UST + 1, 0)))                        # ust 6808 yuvasi
for (x, z) in LUG:
    ry = ry.cut(cyl(CLEAR[3] / 2, (x, Y_BLK - 1, z), (x, Y_BLK + 7, z)))
I_RY = add("Rulman yuvasi", "Govde", ry.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(0, -20, 0),
           not_="iki 6808-2RS: ust rulman tablaya oturur (kafa agirligi), alt rulman devrilme momentini ikiye boler")

# --- 6808 dis bilezikleri (govdede)
r1_i, r1_d = rulman_6808((0, Y_R1[0], 0), (0, 1, 0))
r2_i, r2_d = rulman_6808((0, Y_R2[0], 0), (0, 1, 0))
I_R1D = add("6808-2RS alt rulman (dis bilezik)", "Govde", r1_d, "Satin", "Celik", kod="6808-2RS rulman 40x52x7", renk="celik",
            patlat=(0, -10, 0))
I_R2D = add("6808-2RS ust rulman (dis bilezik)", "Govde", r2_d, "Satin", "Celik", kod="6808-2RS rulman 40x52x7", renk="celik",
            patlat=(0, 5, 0))

# --- pan servosu (govdesi sabit) + kulak civatalari M3x8 + pul + isil gomme somun (tablada)
body_p, dome_p, _ = mg996r_local()
I_SERVO_P = add("Pan servosu MG996R", "Govde", yerlestir_m(body_p, M_P), "Satin", "-", kod="MG996R servo", renk="siyah",
                patlat=(0, -45, 60))
I_DOME_P = add("Pan servosu cikis mili", "Govde", yerlestir_m(dome_p, M_P), "Satin", "-", kod="(servo ile)", renk="siyah",
               patlat=(0, -45, 60))
for q in DELIK_P:
    t_ = WASH125[3][2]
    i_p = add("Pan servosu kulak pulu M3", "Govde", washer(3, (q.x, Y_EAR[1], q.z), (0, 1, 0)), "Baglanti", "Celik",
              kod="M3 DIN 125 pul", renk="celik", patlat=(0, -15, 60))
    i_c = add("Pan servosu kulak civatasi M3x8", "Govde", screw912(3, 8, (q.x, Y_EAR[1] + t_, q.z), (0, -1, 0)), "Baglanti",
              "Celik 8.8", kod="M3x8 DIN 912", renk="celik", patlat=(0, -5, 60))
    i_i = add("Isil gomme somun M3 (servo yuvasi)", "Govde", insert(3, (q.x, Y_EAR[0], q.z), (0, -1, 0)), "Baglanti", "Pirinc",
              kod="M3 isil gomme somun", renk="pirinc", patlat=(0, -45, 0))
    BAG.append(dict(ad="Pan servosu kulagi", tip="insert", civata=i_c, pul=i_p, insert=i_i, bas_parca=I_SERVO_P, govde=I_SY,
                    nokta=(q.x, Y_EAR[1] + t_, q.z), yon=(0, -1, 0), d=3, L=8.0,
                    agiz_t=Y_EAR[1] + t_ - Y_EAR[0]))

# --- plaka + servo yuvasi -> traverse: 2x M6x20 + pul + cekic somun (kanal z = 0)
for sx in (1, -1):
    x = sx * BP["civata_x"]
    t6 = WASH125[6][2]
    i_p = add("Boyun civata pulu M6", "Govde", washer(6, (x, Y_KULAK_T, 0), (0, 1, 0)), "Baglanti", "Celik", kod="M6 DIN 125 pul",
              renk="celik", patlat=(0, -10, 0))
    i_c = add("Boyun civatasi M6x20", "Govde", screw912(6, 20, (x, Y_KULAK_T + t6, 0), (0, -1, 0)), "Baglanti", "Celik 8.8",
              kod="M6x20 DIN 912", renk="celik", patlat=(0, 10, 0))
    i_s = add("Cekic somun M6 (travers ust kanali)", "Govde", hammer_nut((x, -A.LIP, 0), (0, 1, 0), (0, 0, 1)), "Baglanti", "Celik",
              kod="M6 cekic somun (kanal 10)", renk="celik", patlat=(0, -80, 0))
    BAG.append(dict(ad="Boyun plakasi -> traverse", tip="cekic", civata=i_c, pul=i_p, somun=i_s, govde=I_SY, plaka=I_PLAKA,
                    nokta=(x, Y_KULAK_T + t6, 0), yon=(0, -1, 0), d=6, L=20.0))

# --- rulman yuvasi -> servo yuvasi: 4x M3x10 + isil gomme somun
for (x, z) in LUG:
    i_c = add("Rulman yuvasi civatasi M3x10", "Govde", screw912(3, 10, (x, Y_BLK + 6.0, z), (0, -1, 0)), "Baglanti", "Celik 8.8",
              kod="M3x10 DIN 912", renk="celik", patlat=(0, -10, 0))
    i_i = add("Isil gomme somun M3 (servo yuvasi ustu)", "Govde", insert(3, (x, Y_BLK, z), (0, -1, 0)), "Baglanti", "Pirinc",
              kod="M3 isil gomme somun", renk="pirinc", patlat=(0, -45, 0))
    BAG.append(dict(ad="Rulman yuvasi -> servo yuvasi", tip="insert", civata=i_c, pul=None, insert=i_i, bas_parca=I_RY, govde=I_SY,
                    nokta=(x, Y_BLK + 6.0, z), yon=(0, -1, 0), d=3, L=10.0, agiz_t=6.0))

# ====================================================================== PAN (pan ekseninde doner)
horn_l, hholes = horn_mg_local()
HORN_P = [gp((x, y, 0), M_P) for (x, y) in hholes]
I_HORN_P = add("Pan horn 25T aluminyum disk", "Pan", yerlestir_m(horn_l, M_P), "Satin", "Aluminyum", kod="25T aluminyum disk horn",
               renk="alu", patlat=(0, 10, 0))
add("Pan horn merkez vidasi M3", "Pan", yerlestir_m(horn_vidasi_local(), M_P), "Baglanti", "Celik", kod="M3x5 horn vidasi (servo ile)",
    renk="celik", patlat=(0, 20, 0))

# --- boyun mili (PETG): alt disk horn'a, ici bos (kablolar), arka pencere, omuz + 45 derece koni + flans
bm = cyl(20.0, (0, Y_DISK[0], 0), (0, Y_OMUZ[0], 0)).fuse(cyl(22.0, (0, Y_OMUZ[0], 0), (0, Y_OMUZ[1], 0)))
bm = bm.fuse(koni(22.0, R_CAP, (0, Y_KONI[0], 0), (0, Y_KONI[1], 0))).fuse(cyl(R_CAP, (0, Y_FL[0], 0), (0, Y_FL[1], 0)))
bm = bm.cut(cyl(16.0, (0, Y_DISK[1], 0), (0, Y_FL[1] + 1, 0)))                       # O32 kablo deligi
bm = bm.cut(cyl(4.5, (0, Y_DISK[0] - 1, 0), (0, Y_DISK[1] + 1, 0)))                  # horn merkez vidasi
for h in HORN_P:
    bm = bm.cut(cyl(CLEAR[3] / 2, (h.x, Y_DISK[0] - 1, h.z), (h.x, Y_DISK[1] + 1, h.z)))
bm = bm.cut(box(-6.85, 6.85, Y_PEN[0], Y_PEN[1], -25.0, 0.0))                        # arka kablo penceresi (13,7 genis)
FL_DEL = [(25.0, 0.0), (0.0, 25.0), (-25.0, 0.0), (0.0, -25.0)]
for (x, z) in FL_DEL:
    bm = bm.cut(insert_hole(3, (x, Y_FL[1], z), (0, -1, 0)))
I_MIL = add("Boyun mili", "Pan", bm.removeSplitter(), "Baski", "PETG", renk="petg2", patlat=(0, 70, 0),
            not_="ici bos O32 (kablolar eksenden iner), alt diski horn'a 4x M3x8; omzu ust 6808 ic bileziginde")
for h in HORN_P:
    i = add("Mil-horn civatasi M3x8", "Pan", screw912(3, 8, (h.x, Y_DISK[1], h.z), (0, -1, 0)), "Baglanti", "Celik 8.8",
            kod="M3x8 DIN 912", renk="celik", patlat=(0, 75, 0))
    BAG.append(dict(ad="Boyun mili -> pan horn", tip="civata_horn", civata=i, govde=I_MIL, horn=I_HORN_P, nokta=(h.x, Y_DISK[1], h.z),
                    yon=(0, -1, 0), yuz_bas=Y_DISK[1], horn_yuz=(Y_HORN[1], Y_HORN[0]), kasa=Y_PK, d=3, L=8.0))
I_R1I = add("6808-2RS alt rulman (ic bilezik)", "Pan", r1_i, "Satin", "Celik", kod="(6808 ile)", renk="celik", patlat=(0, -10, 0))
I_R2I = add("6808-2RS ust rulman (ic bilezik)", "Pan", r2_i, "Satin", "Celik", kod="(6808 ile)", renk="celik", patlat=(0, 5, 0))

# --- egme catali (PETG): taban + sol duvar (M5 pim) + U kulak plakasi (tilt servosu) + on ag
cb = cyl(R_CAP, (0, Y_CB[0], 0), (0, Y_CB[1], 0)).fuse(box(X_DUVAR[0], X_EP[1], Y_CB[0], Y_CB[1], -14.5, 44.5))
cb = cb.fuse(box(X_DUVAR[0], X_DUVAR[1], Y_CB[1] - 0.01, YT, ZT - 15.0, ZT + 15.0))
cb = cb.fuse(cyl(15.0, (X_DUVAR[0], YT, ZT), (X_DUVAR[1], YT, ZT)))
cb = cb.fuse(cyl(4.0, (X_SOL[1], YT, ZT), (X_DUVAR[0] + 0.01, YT, ZT)))               # 625ZZ ic bilezik dayamasi
cb = cb.fuse(box(X_EP[0], X_EP[1], Y_CB[1] - 0.01, YT + 14.0, -14.5, 44.5))          # kulak plakasi
cb = cb.cut(box(X_EP[0] - 0.1, X_EP[1] + 0.1, YT - MG["W"] / 2 - 0.2, YT + 20.0, ZT - (MG["L"] - MG["SH"]) - 0.2,
                ZT + MG["SH"] + 0.2))                                                 # servo penceresi (ustten acik U)
cb = cb.fuse(box(X_DUVAR[0], X_EP[1], Y_CB[1] - 0.01, 118.0, 37.0, 44.5))            # on ag
cb = cb.cut(cyl(14.0, (0, Y_CB[0] - 1, 0), (0, Y_CB[1] + 1, 0)).cut(box(X_EP[0], 50, Y_CB[0] - 2, Y_CB[1] + 2, -50, 50)))   # kablo deligi O28, kulak plakasi altinda duz (desteksiz)
for (x, z) in FL_DEL:
    cb = cb.cut(cyl(CLEAR[3] / 2, (x, Y_CB[0] - 1, z), (x, Y_CB[1] + 1, z)))
TED, (tz0, tz1) = mg_delikler()
DELIK_T = [gp((xx, yy, tz0), M_T) for (xx, yy) in TED]
for q in DELIK_T:
    cb = cb.cut(cyl(CLEAR[4] / 2, (X_EP[0] - 1, q.y, q.z), (X_EP[1] + 1, q.y, q.z)))
cb = cb.cut(cyl(2.75, (X_SOL[1] - 0.1, YT, ZT), (X_DUVAR[0] + 0.1, YT, ZT)))
cb = cb.cut(insert_hole(5, (X_DUVAR[0], YT, ZT), (1, 0, 0)))
I_CATAL = add("Egme catali", "Pan", cb.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(0, 95, 0),
              not_="mil flansina 4x M3; tilt servosu +X'ten kulak plakasina, sol duvarda 625ZZ pimi (M5 isil gomme)")
for (x, z) in FL_DEL:
    i_c = add("Catal-mil civatasi M3x8", "Pan", screw912(3, 8, (x, Y_CB[1], z), (0, -1, 0)), "Baglanti", "Celik 8.8",
              kod="M3x8 DIN 912", renk="celik", patlat=(0, 100, 0))
    i_i = add("Isil gomme somun M3 (mil flansi)", "Pan", insert(3, (x, Y_FL[1], z), (0, -1, 0)), "Baglanti", "Pirinc",
              kod="M3 isil gomme somun", renk="pirinc", patlat=(0, 70, 0))
    BAG.append(dict(ad="Egme catali -> boyun mili", tip="insert", civata=i_c, pul=None, insert=i_i, bas_parca=I_CATAL, govde=I_MIL,
                    nokta=(x, Y_CB[1], z), yon=(0, -1, 0), d=3, L=8.0, agiz_t=Y_CB[1] - Y_FL[1]))

# --- tilt servosu (govdesi catalda) + 4x M4x16 + kontra somun
body_t, dome_t, _ = mg996r_local()
I_SERVO_T = add("Tilt servosu MG996R", "Pan", yerlestir_m(body_t, M_T), "Satin", "-", kod="MG996R servo", renk="siyah",
                patlat=(60, 95, 0))
I_DOME_T = add("Tilt servosu cikis mili", "Pan", yerlestir_m(dome_t, M_T), "Satin", "-", kod="(servo ile)", renk="siyah",
               patlat=(60, 95, 0))
for q in DELIK_T:
    i_cv = add("Tilt servosu kulak civatasi M4x16", "Pan", screw912(4, 16, (X_TKUL[1], q.y, q.z), (-1, 0, 0)), "Baglanti",
               "Celik 8.8", kod="M4x16 DIN 912", renk="celik", patlat=(90, 95, 0))
    i_sm = add("Tilt servosu kontra somunu M4", "Pan", nut(4, (X_EP[0], q.y, q.z), (-1, 0, 0), "985", (0, 0, 1)), "Baglanti", "Celik",
               kod="M4 DIN 985 kontra somun", renk="celik", patlat=(-20, 95, 0))
    BAG.append(dict(ad="Tilt servosu kulagi", tip="servo_kulak", civata=i_cv, somun=i_sm, servo=I_SERVO_T, govde=I_CATAL,
                    nokta=(X_TKUL[1], q.y, q.z), yon=(-1, 0, 0), d=4, L=16.0))

# --- 625ZZ ic bilezik + M5 pim civatasi + pul + isil gomme somun (catal sol duvarinda)
b5_i, b5_d = bearing(5, 16, 5, (X_RUL[0], YT, ZT), (1, 0, 0), 4.1, 6.4)
I_625I = add("625ZZ rulman (ic bilezik)", "Pan", b5_i, "Satin", "Celik", kod="(625ZZ ile)", renk="celik", patlat=(-40, 140, 0))
I_PUL5 = add("Pim pulu M5", "Pan", washer(5, (X_RUL[0], YT, ZT), (-1, 0, 0)), "Baglanti", "Celik", kod="M5 DIN 125 pul",
             renk="celik", patlat=(-55, 140, 0))
I_CIV5 = add("Pim civatasi M5x12", "Pan", screw912(5, 12, (X_RUL[0] - 1.0, YT, ZT), (1, 0, 0)), "Baglanti", "Celik 8.8",
             kod="M5x12 DIN 912", renk="celik", patlat=(-70, 140, 0))
I_INS5 = add("Isil gomme somun M5 (catal)", "Pan", insert(5, (X_DUVAR[0], YT, ZT), (1, 0, 0)), "Baglanti", "Pirinc",
             kod="M5 isil gomme somun", renk="pirinc", patlat=(0, 95, 0))

# ====================================================================== KAFA (Pan * tilt)
horn_t, hholes_t = horn_mg_local()
HORN_T = [gp((x, y, 0), M_T) for (x, y) in hholes_t]
I_HORN_T = add("Tilt horn 25T aluminyum disk", "Kafa", yerlestir_m(horn_t, M_T), "Satin", "Aluminyum", kod="25T aluminyum disk horn",
               renk="alu", patlat=(25, 140, 0))
add("Tilt horn merkez vidasi M3", "Kafa", yerlestir_m(horn_vidasi_local(), M_T), "Baglanti", "Celik", kod="M3x5 horn vidasi (servo ile)",
    renk="celik", patlat=(35, 140, 0))
I_625D = add("625ZZ rulman (dis bilezik)", "Kafa", b5_d, "Satin", "Celik", kod="625ZZ rulman 5x16x5", renk="celik",
             patlat=(-40, 140, 0))

# --- kafa iskeleti (PETG): kafa tablasi + 4 kenar boss'u (kabuk civatalari) + iki yanak (tilt ekseni)
BOSS_Z = (-30.0, 45.0)                    # arka kabuk / on kabuk civatasi z
Y_BOSS = (170.0, Y_TABLA[1])
Y_KCIV = 176.5                            # kabuk civatasi ekseni y
ki = yuv_dikdortgen_y(-(KX - KT - 2.0), KX - KT - 2.0, -58.0, 58.0, 10.0, Y_TABLA[0], Y_TABLA[1])
for sx in (1, -1):
    for zc in BOSS_Z:
        x0, x1 = sorted((sx * 92.0, sx * (KX - KT)))
        ki = ki.fuse(box(x0, x1, Y_BOSS[0], Y_BOSS[1], zc - 6.0, zc + 6.0))
for (x0, x1) in (X_SAG, X_SOL):
    ki = ki.fuse(box(x0, x1, YT, Y_TABLA[0] + 0.01, ZT - 16.0, ZT + 16.0)).fuse(cyl(16.0, (x0, YT, ZT), (x1, YT, ZT)))
ki = ki.cut(cyl(4.5, (X_SAG[0] - 0.1, YT, ZT), (X_SAG[1] + 0.1, YT, ZT)))           # horn merkez vidasi erisimi
for h in HORN_T:
    ki = ki.cut(cyl(CLEAR[3] / 2, (X_SAG[0] - 0.1, h.y, h.z), (X_SAG[1] + 0.1, h.y, h.z)))
ki = ki.cut(cyl(8.0, (X_RUL[0], YT, ZT), (X_SOL[1] + 0.01, YT, ZT)))                 # 625ZZ yuvasi O16
ki = ki.cut(cyl(6.5, (X_SOL[0] - 0.01, YT, ZT), (X_RUL[0], YT, ZT)))                 # civata basi cebi
for sx in (1, -1):
    for zc in BOSS_Z:
        ki = ki.cut(insert_hole(3, (sx * (KX - KT), Y_KCIV, zc), (-sx, 0, 0)))
ki = ki.cut(yuv_dikdortgen_y(-50.0, -37.0, 0.0, 24.0, 4.0, Y_TABLA[0] - 1, Y_TABLA[1] + 1))   # kablo gecisi (sol yanak disi)
for (x0, x1, z0, z1) in ((44.0, 86.0, -46.0, 30.0), (-86.0, -56.0, -46.0, 30.0), (-30.0, 22.0, -50.0, -10.0),
                         (-22.0, 18.0, 46.0, 54.0)):
    ki = ki.cut(yuv_dikdortgen_y(x0, x1, z0, z1, min(6.0, (z1 - z0) / 2 - 1.0), Y_TABLA[0] - 1, Y_TABLA[1] + 1))   # hafifletme
I_ISK = add("Kafa iskeleti", "Kafa", ki.removeSplitter(), "Baski", "PETG", renk="petg2", patlat=(0, 170, 0),
            not_="kafa tablasi + iki yanak: sag yanak tilt horn'una 4x M3, sol yanakta 625ZZ; kabuklar tablaya 4x M3")
for h in HORN_T:
    i = add("Yanak-horn civatasi M3x8", "Kafa", screw912(3, 8, (X_SAG[1], h.y, h.z), (-1, 0, 0)), "Baglanti", "Celik 8.8",
            kod="M3x8 DIN 912", renk="celik", patlat=(45, 170, 0))
    BAG.append(dict(ad="Kafa iskeleti sag yanak -> tilt horn", tip="civata_horn", civata=i, govde=I_ISK, horn=I_HORN_T,
                    nokta=(X_SAG[1], h.y, h.z), yon=(-1, 0, 0), yuz_bas=X_SAG[1], horn_yuz=(X_TH[1], X_TH[0]), kasa=X_TK, d=3, L=8.0))
BAG.append(dict(ad="Tilt pimi (servo karsi yatagi)", tip="pim", civata=I_CIV5, pul=I_PUL5, rul_i=I_625I, rul_d=I_625D, insert=I_INS5,
                govde=I_CATAL, catal=I_ISK, nokta=(X_DUVAR[0], YT, ZT), yon=(1, 0, 0), agiz=X_DUVAR[0], d=5))

# --- kafa kabugu: V3 210 x 180 x 150 (rc:472), duvar 2,5; z = 30'da on (yuz) / arka ayrimi
dis = kafa_kutu(-KX, KX, KY0, KY1, KZ0, KZ1, 28.0, 12.0)
ic = kafa_kutu(-KX + KT, KX - KT, KY0 + KT, KY1 - KT, KZ0 + KT, KZ1 - KT, 28.0 - KT, 12.0 - KT)
kab = dis.cut(ic)
ACIK = yuv_dikdortgen_y(-ACIKLIK["x"], ACIKLIK["x"], ACIKLIK["z"][0], ACIKLIK["z"][1], ACIKLIK["r"], KY0 - 5, KY0 + KT + 5)
kab = kab.cut(ACIK)
BIG = 1000.0
# on kabuk: LCD penceresi + ekran yuvasi kenari + 4 LCD boss'u + kamera deligi ve 4 boss
ok = kab.common(box(-BIG, BIG, -BIG, BIG, Z_DIKIS, BIG))
aw, ah = LCD["al"] / 2 + 1.0, LCD["ah"] / 2 + 1.0
Y_AA = Y_LCD + LCD["aa_dy"]                                                          # 181 aktif alan merkezi
PEN = box(-aw, aw, Y_AA - ah, Y_AA + ah, Z_LCD - 1.0, KZ1 + 1.0)
kenar = box(-LCD["l"] / 2 - 1.0, LCD["l"] / 2 + 1.0, Y_LCD - LCD["h"] / 2 - 1.0, Y_LCD + LCD["h"] / 2 + 1.0, Z_LCD, KZ1 - KT + 0.1)
ok = ok.fuse(kenar.cut(PEN))
Z_KULAK0 = Z_LCD - LCD["panel_t"]                                                    # 76: LCD kulak on yuzu
LCD_DEL = [(x, Y_LCD + y) for (x, y) in lcd_delikler()]
for (x, y) in LCD_DEL:
    ok = ok.fuse(cyl(3.5, (x, y, Z_KULAK0), (x, y, KZ1 - KT + 0.1)))
CAM_DEL = [(x, Y_CAM + y) for (x, y) in kamera_delikler()]
for (x, y) in CAM_DEL:
    ok = ok.fuse(cyl(2.5, (x, y, Z_CAM), (x, y, KZ1 - KT + 0.1)))
ok = ok.cut(PEN)
ok = ok.cut(cyl(4.5, (0, Y_CAM, Z_CAM), (0, Y_CAM, KZ1 + 1)))
for (x, y) in LCD_DEL:
    ok = ok.cut(insert_hole(3, (x, y, Z_KULAK0), (0, 0, 1)))
for (x, y) in CAM_DEL:
    ok = ok.cut(cyl(1.0, (x, y, Z_CAM - 0.1), (x, y, Z_CAM + 7.5)))                  # M2 PT vida: modelde O2 (gercek pilot O1,6)
for sx in (1, -1):
    ok = ok.cut(cyl(CLEAR[3] / 2, (sx * (KX + 1), Y_KCIV, BOSS_Z[1]), (sx * (KX - KT - 1), Y_KCIV, BOSS_Z[1])))
I_ON = add("Yuz kabugu (on)", "Kafa", ok.removeSplitter(), "Baski", "PETG", renk="kabuk", patlat=(0, 140, 120),
           not_="LCD penceresi + 3 mm ekran yuvasi kenari + 4 LCD boss'u (M3 isil gomme), kamera deligi O9 + 4 boss (M2)",
           doluluk=A.KABUK_DOLULUK)
# arka kabuk: dikis dili (on kabugun icine 6 mm), yan havalandirma yariklari
ak = kab.common(box(-BIG, BIG, -BIG, BIG, -BIG, Z_DIKIS))
dil_ic = kafa_kutu(-KX + KT + 1.5, KX - KT - 1.5, KY0 + KT + 1.5, KY1 - KT - 1.5, KZ0 + KT + 1.5, KZ1 - KT - 1.5,
                   28.0 - KT - 1.5, 12.0 - KT - 1.5)
dil = ic.cut(dil_ic).common(box(-BIG, BIG, -BIG, BIG, Z_DIKIS - 0.01, Z_DIKIS + 6.0)).cut(ACIK)
ak = ak.fuse(dil)
for sx in (1, -1):
    for k in range(4):
        ak = ak.cut(box(min(sx * (KX + 1), sx * (KX - KT - 1)), max(sx * (KX + 1), sx * (KX - KT - 1)), 140.0 + 9 * k, 144.0 + 9 * k,
                        -15.0, 20.0))
    ak = ak.cut(cyl(CLEAR[3] / 2, (sx * (KX + 1), Y_KCIV, BOSS_Z[0]), (sx * (KX - KT - 1), Y_KCIV, BOSS_Z[0])))
I_ARKA = add("Arka kafa kabugu", "Kafa", ak.removeSplitter(), "Baski", "PETG", renk="kabuk", patlat=(0, 140, -120),
             not_="dikis dili on kabuga 6 mm girer; yanlarda 4'er havalandirma yarigi", doluluk=A.KABUK_DOLULUK)
for sx in (1, -1):
    for zc, kab_i in ((BOSS_Z[0], I_ARKA), (BOSS_Z[1], I_ON)):
        i_c = add("Kabuk civatasi M3x8 ISO 7380", "Kafa", screw7380(3, 8, (sx * KX, Y_KCIV, zc), (-sx, 0, 0)), "Baglanti", "Celik",
                  kod="M3x8 ISO 7380", renk="celik", patlat=(sx * 40, 170, 0))
        i_i = add("Isil gomme somun M3 (kafa tablasi)", "Kafa", insert(3, (sx * (KX - KT), Y_KCIV, zc), (-sx, 0, 0)), "Baglanti",
                  "Pirinc", kod="M3 isil gomme somun", renk="pirinc", patlat=(0, 170, 0))
        BAG.append(dict(ad="Kafa kabugu -> kafa tablasi", tip="insert", civata=i_c, pul=None, insert=i_i, bas_parca=kab_i, govde=I_ISK,
                        nokta=(sx * KX, Y_KCIV, zc), yon=(-sx, 0, 0), d=3, L=8.0, agiz_t=KT))

# --- 7" LCD (Waveshare (C)) + 4x M3x6 ISO 7380 + isil gomme somun (on kabuk boss'larinda)
lcd = lcd_local()
lcd.translate(V(0, Y_LCD, Z_LCD))
I_LCD = add("Yuz ekrani Waveshare 7in HDMI LCD (C)", "Kafa", lcd, "Satin", "-", kod="Waveshare 7in HDMI LCD (C) 1024x600",
            renk="siyah", patlat=(0, 140, 60), not_="panel on yuzu ekran yuvasi kenarina dayali; kulaklar 4x M3 ile boss'lara")
Z_KULAK1 = Z_KULAK0 - LCD["arka_t"]                                                  # 74.4 kulak arka yuzu
for (x, y) in LCD_DEL:
    i_c = add("LCD civatasi M3x6 ISO 7380", "Kafa", screw7380(3, 6, (x, y, Z_KULAK1), (0, 0, 1)), "Baglanti", "Celik",
              kod="M3x6 ISO 7380", renk="celik", patlat=(0, 140, 40))
    i_i = add("Isil gomme somun M3 (LCD boss)", "Kafa", insert(3, (x, y, Z_KULAK0), (0, 0, 1)), "Baglanti", "Pirinc",
              kod="M3 isil gomme somun", renk="pirinc", patlat=(0, 140, 120))
    BAG.append(dict(ad="LCD kulagi -> on kabuk boss'u", tip="insert", civata=i_c, pul=None, insert=i_i, bas_parca=I_LCD, govde=I_ON,
                    nokta=(x, y, Z_KULAK1), yon=(0, 0, 1), d=3, L=6.0, agiz_t=LCD["arka_t"]))

# --- vizor: 3 mm parlak siyah akrilik 190 x 115 R18 (rc:636-642), ekran penceresi; on yuze VHB bantla (tahmini)
vz = yuv_dikdortgen_z(-95.0, 95.0, Y_LCD - 1.5 - 57.5, Y_LCD - 1.5 + 57.5, 18.0, KZ1, KZ1 + 3.0)
vz = vz.cut(box(-aw, aw, Y_AA - ah, Y_AA + ah, KZ1 - 1, KZ1 + 4))
I_VIZOR = add("Vizor (siyah akrilik)", "Kafa", vz.removeSplitter(), "Imalat", "Akrilik", kod="Vizor 3 mm siyah akrilik 190x115 (lazer)",
              renk="vizor", patlat=(0, 140, 170), not_="on yuze 3M VHB bantla (tahmini); ekranin kenarlarini gizler")

# --- Camera Module 3 + 4x M2x8 PT vida (on kabuk boss'lari)
cam = kamera_local()
cam.translate(V(0, Y_CAM, Z_CAM))
I_CAM = add("Kamera Raspberry Pi Camera Module 3", "Kafa", cam, "Satin", "-", kod="Raspberry Pi Camera Module 3", renk="pcb",
            patlat=(0, 160, 60))
Z_CAM_ARKA = Z_CAM - CAM["t"]
for (x, y) in CAM_DEL:
    i_c = add("Kamera vidasi M2x8 PT", "Kafa", screw_m2(8.0, (x, y, Z_CAM_ARKA), (0, 0, 1)), "Baglanti", "Celik",
              kod="M2x8 PT vida (plastik icin)", renk="celik", patlat=(0, 160, 40))
    BAG.append(dict(ad="Kamera -> on kabuk boss'u", tip="pt", civata=i_c, bas_parca=I_CAM, govde=I_ON, nokta=(x, y, Z_CAM_ARKA),
                    yon=(0, 0, 1), d=2, L=8.0, agiz_t=CAM["t"]))

# --- kablo demeti gosterimi (Referans: carpisma ve kutleye girmez). LCD/kamera -> tabla ustu -> sol yanak disi ->
#     tilt ekseni altindan (eksenin 18 mm alti) catal sol duvarina -> taban deligi -> mil ici -> pencere -> kablo odasi ->
#     servo yuvasi arka kanali -> alt pencere -> gövdeye (R62 halkasi)
YOL = [(55.0, 190.0, 62.0), (0.0, 190.0, 30.0), (-43.0, 190.0, 12.0), (-43.0, 150.0, 12.0), (-40.0, 112.0, 18.0),
       (-18.0, 108.0, 2.0), (-8.0, 100.0, -6.0), (0.0, 90.0, 0.0), (0.0, 60.0, 0.0), (0.0, 58.0, -18.0), (-12.0, 55.0, -23.0),
       (-4.0, 45.0, -21.0), (-4.0, 15.0, -23.0), (0.0, 10.0, -33.0), (0.0, -40.0, -36.0)]
kd = None
for a, b in zip(YOL[:-1], YOL[1:]):
    s = cyl(3.0, a, b).fuse(Part.makeSphere(3.0, V(*b)))
    kd = s if kd is None else kd.fuse(s)
add("Kablo demeti (gosterim)", "Referans", kd.removeSplitter(), "Referans", "-", kod="(gosterim)", renk="kablo",
    not_="HDMI ince kablo + USB (dokunmatik/guc) + kamera FPC + tilt servosu; sema, gercek kablo degil")

# ====================================================================== kutle ve agirlik merkezi
DOLULUK = 0.80          # kucuk, kalin cidarli PETG parcalar (dirsek ile ayni, tahmini); kabuklar arayuz.KABUK_DOLULUK
RHO = {"PETG": A.PETG_RHO, "Aluminyum": 2.70, "Celik": 7.85, "Celik 8.8": 7.85, "Pirinc": 8.50, "Akrilik": 1.19}
for p in P:
    p["hacim"] = p["shape"].Volume
    sol = p["shape"].Solids
    p["kati"] = len(sol)
    if sol:
        vt = sum(s.Volume for s in sol)
        cc = V(0, 0, 0)
        for s in sol:
            cc = cc + s.CenterOfMass * (s.Volume / vt)
        p["merkez"] = cc
    else:
        p["merkez"] = p["shape"].BoundBox.Center
    if p["tur"] == "Referans" or p["kod"] == "(servo ile)":
        p["kutle"] = 0.0
    elif p["kod"] == "MG996R servo":
        p["kutle"] = MG["kutle_g"]                    # datasheet 55 g (cikis mili dahil)
    elif p["ad"].startswith("Yuz ekrani"):
        p["kutle"] = LCD["kutle_g"]                   # rc:39 m_lcd 0,23 kg (kaynakta dogrulanmadi: tahmini)
    elif p["ad"].startswith("Kamera Raspberry"):
        p["kutle"] = CAM["kutle_g"]                   # rc:37 m_cam 0,004 kg
    else:
        d = p["doluluk"] if p["doluluk"] else (DOLULUK if p["malzeme"] == "PETG" else 1.0)
        p["kutle"] = p["hacim"] / 1000.0 * RHO.get(p["malzeme"], 1.0) * d
    p["bb"] = p["shape"].BoundBox

# baski parcalari: baski yonu (robot koordinatinda tablaya gore yukari) ve aciklama
BASKI = {
    "Servo yuvasi": dict(yukari=(0, 1, 0), yon="dik: kulak flansi tablada"),
    "Rulman yuvasi": dict(yukari=(0, 1, 0), yon="dik: kulaklar tablada, rulman yuvasi yukari"),
    "Boyun mili": dict(yukari=(0, 1, 0), yon="dik: horn diski tablada, flans yukari (45 derece koni)"),
    "Egme catali": dict(yukari=(0, 1, 0), yon="dik: taban tablada, duvarlar yukari"),
    "Kafa iskeleti": dict(yukari=(0, -1, 0), yon="ters: kafa tablasi tablada, yanaklar yukari"),
    "Yuz kabugu (on)": dict(yukari=(0, 0, -1), yon="yuz asagi: on yuz tablada, dikis yukari"),
    "Arka kafa kabugu": dict(yukari=(0, 0, 1), yon="arka yuz tablada, dikis dili yukari"),
}
for p in P:
    if p["tur"] == "Baski":
        p["doluluk_baski"] = p["doluluk"] or DOLULUK


# ====================================================================== kinematik
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
