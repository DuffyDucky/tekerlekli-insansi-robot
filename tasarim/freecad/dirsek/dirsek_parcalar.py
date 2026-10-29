# Sag dirsek modulu (dirsek + on kol + bilek + el) - PARCALAR, kutle ve kinematik (FreeCAD 1.1, Part)
# 1,65 m (Y2a, 26 Ekim 2026; taslak-170 kol x1,25 kararlari): tup ucu -170 (catal y olculeri TUC'a bagli), on kol U bolumu +32,4,
# el yakasi +19 (ici bos), catal dis kolu 8 mm + 45 derece destek dis yuze, horn civatasi M3x12 + 2x DIN 125-A pul. Olculer arayuz.DIRSEK.
# Import edilebilir: dirsek_montaj.py (kontroller + kayit) ve 2. asamada carpisma / ana montaj bunu kullanir.
# Koordinat = omuz yereli: orijin travers merkezi (omuz S1 ekseni), X disari, Y yukari, Z ileri. Ev pozu: kol asagida duz.
# Arayuz olculeri (tup ucu, dirsek/bilek ekseni, sinirlar): ../arayuz.py DIRSEK. Omuz geometrisi degismez.
#
# Yapi (V3 robot_cad sag kol duzeni, rc:669-810: dirsek MG996R mili +X, bilek MG996R mili asagi, sabit el):
#   UstKol (omuz Kol grubuna sabit): dirsek catali = tup ucuna giren pim + yarikli sikma bilezigi (2x M3) + kopru + iki kol.
#       Dis kol dirsek servosunun horn'una 4x M3 ile bagli; ic kolda 625ZZ (servo milinin karsisinda yatak).
#   OnKol (dirsek ekseninde doner): on kol govdesi (arkasi acik U), dirsek servosu (govdesi on kolda), bilek servosu.
#       M5 pim civatasi 625ZZ ic bilezigini on koldaki dayamaya sikar -> servo mili yanal yuk tasimaz.
#   El (bilek ekseninde doner): bilek flansi (horn'a 4x M3) + el (yaka 2x M3 ile flansa; sabit kanca parmak + basparmak).
import os, sys, math, time

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from dirsek_lib import *   # noqa
import arayuz as A

t0 = time.time()
D = A.DIRSEK
TX, TZ = D["tup_x"], D["tup_z"]          # ust kol tupu ekseni (omuz XR, ZC)
TUC = D["tup_uc_y"]                      # tup ucu y (-170; 125 cm'de -140). Catal olculeri TUC'a gore (asagida TUC + ofset)
YE, ZE = D["eksen_y"], D["eksen_z"]      # dirsek ekseni
XW = D["bilek_x"]                        # bilek ekseni x


def Y(s):
    """s = dirsek ekseninden on kol boyunca asagi uzaklik (ev pozunda) -> y."""
    return YE - s


# ---------------------------------------------------------------- olcu zinciri (X: icten disa)
XB = 177.0                                   # dirsek servosu taban yuzu
X_KASA = XB + MG["H"]                        # 213.6 kasa ustu (mil tarafi)
X_HORN0 = X_KASA + HORN_MG["Z0"]             # 216.6 horn alt yuzu
X_HORN1 = X_KASA + HORN_MG["Z1"]             # 219.9 horn ust yuzu = mil ucu
X_KULAK = (XB + 26.6, XB + 26.6 + MG["TAB_T"])   # 203.6 / 206.1 kulak yuzleri
DIS_KOL = (X_HORN1, X_HORN1 + D["catal_dis_kol"])   # catal dis kolu (horn'a bagli): 8 mm (1,65 m; 125 cm'de 5), disa (+X) kalinlasir
CATAL_EK = D["catal_dis_kol"] - 5.0              # 125 cm 5 mm dis kola gore ek (3)
IC_KOL = (156.0, 167.0)                      # catal ic kolu (625ZZ yuvasi)
RUL_X = 162.0                                # 625ZZ: x 162...167
YANAK = (168.0, XB - 0.5)                    # on kol yanagi (M5 isil gomme somun)
PLAKA_E = (X_KULAK[0] - 5.0, X_KULAK[0])     # dirsek servosu kulak plakasi 198.6...203.6
R_KAFA = 21.0                                # on kol basinin dirsek ekseni etrafindaki yaricapi
KOPRU_Y = (TUC - 8.0, TUC)                   # catal koprusu
ON_DUVAR = (ZE + 11.0, ZE + 14.0)            # on kol on duvari (z)
ZK = 14.0                                    # on kol yari derinligi (z)
# --- bilek servosu (s ekseni): taban s 43.5 + on_kol_uzama (1,65 m kol x1,25: 75,9), kasa ustu s 112,5 (125 cm 80,1)
#     Ara duvar (S_WEB) ve dirsek servosu yerinde; ara duvarin altindaki U bolum (yan duvarlar + on duvar, S_ALT) on_kol_uzama kadar uzar.
ON_KOL_UZAMA = D["on_kol_uzama"]
EL_UZAMA = D["el_uzama"]
S_BT = 43.5 + ON_KOL_UZAMA
S_KASA = S_BT + MG["H"]                      # 80.1
S_KULAK = (S_BT + 26.6, S_BT + 26.6 + MG["TAB_T"])   # 70.1 / 72.6
S_PLAKA_B = (S_KULAK[0] - 5.0, S_KULAK[0])   # 65.1...70.1
S_HORN = (S_KASA + HORN_MG["Z0"], S_KASA + HORN_MG["Z1"])   # 83.1 / 86.4
S_FLANS = (S_HORN[1], S_HORN[1] + 8.0)       # 86.4...94.4
S_VIDA_B = S_FLANS[0] + 4.0                  # 90.4 flans civata basi oturma yuzu ve radyal isil gomme somun ekseni
S_YAKA = (S_FLANS[0] + 0.5, S_FLANS[1] + 6.1 + EL_UZAMA)   # el yakasi (boyun): 125 cm 86,9...100,5; 1,65 m'de EL_UZAMA (19) uzun
S_YAKA_BOS = (S_FLANS[1] + 6.1 + 1.5, S_YAKA[1] - 1.5)        # uzayan yakanin ici O22 bos, uclari 1,5 mm kapali (taslak-170 ile ayni)
S_AVUC = (S_YAKA[1], S_YAKA[1] + 52.0)       # 100.5...152.5
S_UC = S_AVUC[1]
S_WEB = (39.5, 42.0)                         # dirsek ve bilek servosu arasindaki yatay ara duvar
S_ALT = (32.0, S_KASA)                       # on kolun genis alt bolumu
X_ALT = (163.6, 226.7)                       # alt bolum dis olculeri (bilek servosu kulaklari + somunlar)
BILEK_GOVDE_X = XW + (MG["L"] / 2 - MG["SH"])   # 195.15 bilek servosu govde merkezi

assert abs(D["eksen_nokta"][0] - X_HORN0) < 1e-9 and abs(D["eksen_x"][1] - DIS_KOL[1]) < 1e-9
assert abs(D["bilek_nokta"][1] - Y(S_HORN[0])) < 1e-9, (D["bilek_nokta"], Y(S_HORN[0]))
assert abs(D["el_ucu"][1] - Y(S_UC)) < 1e-9

ROT_E = App.Rotation(V(0, 1, 0), 90)                         # servo yerel +Z -> +X, govde asagi (-Y)
BASE_E = (X_KASA, YE, ZE)
M_E = App.Placement(V(*BASE_E), ROT_E).toMatrix()
M_B = matris((0, 0, 1), (-1, 0, 0), (0, -1, 0), (XW, Y(S_KASA), ZE))   # bilek servosu: mil -Y, govde +X yonunde


def gp(local, m):
    return m.multVec(V(*local))


P = []


def add(ad, grup, shape, tur, malzeme, kod=None, renk="gri", patlat=(0, 0, 0), not_=""):
    P.append(dict(ad=ad, grup=grup, shape=shape, tur=tur, malzeme=malzeme, kod=kod or ad, renk=renk,
                  patlat=list(patlat), not_=not_))
    return len(P) - 1


BAG = []     # baglanti tanimlari (dirsek_montaj kontrol eder)

# ====================================================================== UST KOL (omuz Kol grubuna sabit)
# --- dirsek catali (PETG): tupe giren pim + sikma bilezigi + kulaklar + kopru + iki kol
R_PIM = A.TUP_PIM_R                                                                  # pim yaricapi (O50,8)
R_TUP_IC = R_PIM + A.GECME["tup_pim"]                                               # tup ic yaricapi (omuz_parcalar ile ayni)
R_TUP_DIS = D["tup_ro"]                                                             # tup dis yaricapi (omuzda 28)
R_BIL_IC = R_TUP_DIS + A.GECME["tup_bilezik"]                                       # bilezik ic yaricapi (tup dis + A.GECME)
c = cyl(R_PIM, (TX, TUC, TZ), (TX, TUC + 25.0, TZ))                                 # pim O50,8 (tup ic bosluk A.GECME)
c = c.fuse(cyl(31.0, (TX, TUC, TZ), (TX, TUC + 25.0, TZ)))                          # bilezik dis O62
c = c.fuse(box(178.0, 192.0, TUC + 2.0, TUC + 25.0, TZ - 41.0, TZ - 30.0))          # sikma kulaklari (arkada)
c = c.fuse(cyl(31.0, (TX, KOPRU_Y[0], TZ), (TX, TUC, TZ)))                          # tup alin kapagi
c = c.fuse(box(IC_KOL[0], DIS_KOL[1], KOPRU_Y[0], TUC, TZ - 16.0, TZ + 16.0))        # kopru
# 45 der. destek: dis kol kalinlasinca ayni egimle dis yuze kadar (1,65 m dis kol 8: ust ucu x 213'te TUC + 12 + 3); ters baskida kopru alti
# cikinti seridi kalmaz. Tup yuvasi (asagida) destekten SONRA oyulur -> destek tup gecmesine girmez (taslakta sonradan yeniden oyuluyordu).
c = c.fuse(prizma([(213.0, TUC + 12.0 + CATAL_EK), (DIS_KOL[1], TUC + 0.1), (DIS_KOL[1], TUC), (213.0, TUC)], "z", TZ - 16.0, TZ + 16.0))
for (x0, x1) in (IC_KOL, DIS_KOL):
    c = c.fuse(box(x0, x1, YE, KOPRU_Y[0], ZE - 16.0, ZE + 16.0)).fuse(cyl(16.0, (x0, YE, ZE), (x1, YE, ZE)))
c = c.cut(cyl(R_BIL_IC, (TX, TUC, TZ), (TX, TUC + 26.0, TZ)).cut(cyl(R_PIM, (TX, TUC - 1, TZ), (TX, TUC + 27.0, TZ))))  # tup yuvasi (halka)
# tup alin yuvasinda 45 der. V oluk: tup ucu oluk kenarlarina (r R_TUP_IC ve R_TUP_DIS) dayanir, ters baskida tavan kendini tasir
_om, _od = 0.5 * (R_TUP_IC + R_TUP_DIS), 0.5 * (R_TUP_DIS - R_TUP_IC)
oluk = Part.Face(Part.makePolygon([V(TX + R_TUP_IC, TUC, TZ), V(TX + R_TUP_DIS, TUC, TZ), V(TX + _om, TUC - _od, TZ), V(TX + R_TUP_IC, TUC, TZ)]))
c = c.cut(oluk.revolve(V(TX, 0, TZ), V(0, 1, 0), 360))
# alin kapaginin on bolumu 45 der. pahli (bukulen on kol kapaga erken degmesin); kopru bandi (z +-16) korunur
pah = box(140.0, 240.0, KOPRU_Y[0] - 0.1, TUC + 0.01, TZ + 16.0, TZ + 40.0).cut(koni(31.0, 23.0, (TX, TUC + 0.01, TZ), (TX, KOPRU_Y[0] - 0.01, TZ)))
c = c.cut(pah)
c = c.cut(cyl(21.9, (TX, TUC + 26.0, TZ), (TX, TUC + 18.0, TZ)))                    # pim ici bos
c = c.cut(koni(21.9, 5.0, (TX, TUC + 18.0, TZ), (TX, TUC + 1.1, TZ)))               # 45 der. tavan (ters baskida desteksiz)
c = c.cut(cyl(5.0, (TX, TUC + 2.0, TZ), (TX, KOPRU_Y[0] - 1.0, TZ)))                # kablo deligi (servo kablolari tupe)
KO = A.KOL_KABLO["catal_oluk"]                                                       # M1: kopru + alin kapagi alti oluk, delikten arkaya:
c = c.cut(box(KO["x"][0], KO["x"][1], KO["y"][0] - 0.01, KO["y"][1], KO["z"][0], KO["z"][1]))   # kablo 4 mm araliga inmez, dirsek arkasindan girer
YARIK_W = D["bilezik_yarik"]                                                         # yarik genisligi (arayuz; kapaninca ic yaricap ~ W/2pi iner)
c = c.cut(box(TX - YARIK_W / 2, TX + YARIK_W / 2, TUC, TUC + 26.0, TZ - 45.0, TZ - 27.5))   # yarik (arka; pim yariksiz)
KELEPCE_Y = (TUC + 19.0, TUC + 8.0)
KELEPCE_Z = TZ - 36.0
for yb in KELEPCE_Y:
    c = c.cut(cyl(CLEAR[3] / 2, (177.0, yb, KELEPCE_Z), (193.0, yb, KELEPCE_Z)))
c = c.cut(cyl(8.0, (RUL_X, YE, ZE), (IC_KOL[1] + 0.01, YE, ZE)))                     # 625ZZ yuvasi O16
c = c.cut(cyl(6.5, (IC_KOL[0] - 0.01, YE, ZE), (RUL_X, YE, ZE)))                     # civata basi cebi (dudak dis bilezige)
c = c.cut(cyl(4.5, (DIS_KOL[0] - 0.01, YE, ZE), (DIS_KOL[1] + 0.01, YE, ZE)))        # horn merkez vidasi erisimi
horn_e, hholes_e = horn_mg_local()
HORN_E = [gp((x, y, 0), M_E) for (x, y) in hholes_e]
for g in HORN_E:
    c = c.cut(cyl(CLEAR[3] / 2, (DIS_KOL[0] - 0.01, g.y, g.z), (DIS_KOL[1] + 0.01, g.y, g.z)))
I_CATAL = add("Dirsek catali", "UstKol", c.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(0, 30, 0),
              not_="tup ucuna pim + yarikli bilezik; kopruden iki kol; ters basilir (pim tablada). Dis kol %.0f mm (1,65 m; kontrol ajani "
                   "x1,25 + DS3235'te L3 SF 2,99 / L4 1,22), kopru ve 45 derece destek dis yuze kadar" % D["catal_dis_kol"])

# --- sikma bilezigi civatalari: M3x20 + 2 pul + M3 kontra somun (arka kulaklar, X yonunde)
for yb in KELEPCE_Y:
    i_p1 = add("Bilezik pulu M3 (bas)", "UstKol", washer(3, (192.0, yb, KELEPCE_Z), (1, 0, 0)), "Baglanti", "Celik",
               kod="M3 DIN 125 pul", renk="celik", patlat=(35, 30, 0))
    i_cv = add("Bilezik civatasi M3x20", "UstKol", screw912(3, 20, (192.5, yb, KELEPCE_Z), (-1, 0, 0)), "Baglanti",
               "Celik 8.8", kod="M3x20 DIN 912", renk="celik", patlat=(50, 30, 0))
    i_p2 = add("Bilezik pulu M3 (somun)", "UstKol", washer(3, (178.0, yb, KELEPCE_Z), (-1, 0, 0)), "Baglanti", "Celik",
               kod="M3 DIN 125 pul", renk="celik", patlat=(-35, 30, 0))
    i_sm = add("Bilezik kontra somunu M3", "UstKol", nut(3, (177.5, yb, KELEPCE_Z), (-1, 0, 0), "985", (0, 0, 1)),
               "Baglanti", "Celik", kod="M3 DIN 985 kontra somun", renk="celik", patlat=(-50, 30, 0))
    BAG.append(dict(ad="Sikma bilezigi y %.0f" % yb, tip="civata_somun", civata=i_cv, pul_bas=i_p1, pul_somun=i_p2,
                    somun=i_sm, govde=I_CATAL, govde_somun=I_CATAL, nokta=(192.0, yb, KELEPCE_Z), yon=(-1, 0, 0),
                    yuz_bas=192.0, yuz_somun=178.0, d=3, L=20.0))

# --- 625ZZ dis bilezigi (catal ic kolunda)
b_in, b_out = bearing(5, 16, 5, (RUL_X, YE, ZE), (1, 0, 0), 4.1, 6.4)
I_RUL_D = add("625ZZ rulman (dis bilezik)", "UstKol", b_out, "Satin", "Celik", kod="625ZZ rulman 5x16x5", renk="celik",
              patlat=(-25, 0, 0))

# --- dirsek servosu horn'u ve civatalari (catal dis koluna sabit)
I_HORN_E = add("Dirsek horn 25T aluminyum disk", "UstKol", yerlestir_m(horn_e, M_E), "Satin", "Aluminyum",
               kod="25T aluminyum disk horn", renk="alu", patlat=(25, 0, 0))
add("Dirsek horn merkez vidasi M3", "UstKol", yerlestir_m(horn_vidasi_local(), M_E), "Baglanti", "Celik",
    kod="M3x5 horn vidasi (servo ile)", renk="celik", patlat=(40, 0, 0))
# Horn civatasi: dis kol 8 mm -> M3x12 DIN 912 + 2x DIN 125-A M3 pul (arayuz DIRSEK horn_civata / horn_pul): gereken boy 8 + 3 = 11
# (standart degil); uc 125 cm'deki yerde (x 216,9: horn'da 3,0 mm dis, kasaya 3,3). Pulsuz M3x12 cikis kubbesine 0,58 mm kalirdi (ret).
HC_D, HC_L = D["horn_civata"]
HP_N, HP_T = D["horn_pul"]
assert abs((DIS_KOL[1] + HP_N * HP_T - HC_L) - (X_HORN1 - 3.0)) < 1e-9, "horn civatasi ucu horn'da 3 mm olmali"
for g in HORN_E:
    yb = DIS_KOL[1] + HP_N * HP_T                          # civata basinin oturma yuzu (pul yigini ustu)
    i = add("Catal-horn civatasi M3x%d" % HC_L, "UstKol", screw912(HC_D, HC_L, (yb, g.y, g.z), (-1, 0, 0)), "Baglanti",
            "Celik 8.8", kod="M3x%d DIN 912" % HC_L, renk="celik", patlat=(45, 0, 0),
            not_="dis kol %.0f mm: bas %d x DIN 125-A pul ustunde, uc 125 cm'deki yerde (horn'da 3 mm)" % (D["catal_dis_kol"], HP_N))
    ip_ = None
    if HP_N:
        pul_ = washer(3, (DIS_KOL[1], g.y, g.z), (1, 0, 0))
        for k_ in range(1, HP_N):
            pul_ = pul_.fuse(washer(3, (DIS_KOL[1] + k_ * HP_T, g.y, g.z), (1, 0, 0)))
        ip_ = add("Catal-horn pulu M3 (%dx DIN 125-A)" % HP_N, "UstKol", pul_.removeSplitter(), "Baglanti", "Celik",
                  kod="%d x DIN 125-A M3 (3,2 x 7 x 0,5)" % HP_N, renk="celik", patlat=(40, 0, 0),
                  not_="M3x%d bas alti pul yigini %.1f mm (M3x11 standart degil)" % (HC_L, HP_N * HP_T))
    BAG.append(dict(ad="Catal dis kolu -> dirsek horn", tip="civata_horn", civata=i, pul=ip_, govde=I_CATAL, horn=I_HORN_E,
                    nokta=(yb, g.y, g.z), yon=(-1, 0, 0), yuz_bas=yb, horn_yuz=(X_HORN1, X_HORN0),
                    kasa=X_KASA, d=3, L=float(HC_L)))

# ====================================================================== ON KOL (dirsek ekseninde doner)
kafa = cyl(R_KAFA, (150.0, YE, ZE), (240.0, YE, ZE)).fuse(box(150.0, 240.0, Y(S_KASA + 1), YE, ZE - 30, ZE + 30))
g = box(YANAK[0], YANAK[1], Y(S_WEB[1]), Y(-R_KAFA), ZE - ZK, ZE + ZK)                          # yanak
g = g.fuse(cyl(4.0, (IC_KOL[1], YE, ZE), (YANAK[0], YE, ZE)))                                    # 625ZZ ic bilezik dayamasi
g = g.fuse(box(YANAK[0], PLAKA_E[1], Y(S_WEB[1]), Y(-R_KAFA), ON_DUVAR[0], ON_DUVAR[1]))          # on duvar (boyun)
g = g.fuse(box(PLAKA_E[0], PLAKA_E[1], Y(S_WEB[1]), Y(-R_KAFA), ZE - ZK, ZE + ZK))               # dirsek servosu plakasi
g = g.fuse(box(X_ALT[0], X_ALT[1], Y(S_WEB[1]), Y(S_WEB[0]), ZE - ZK, ZE + ZK))                  # ara duvar
for (x0, x1) in ((X_ALT[0], X_ALT[0] + 3.0), (X_ALT[1] - 3.0, X_ALT[1])):
    g = g.fuse(box(x0, x1, Y(S_ALT[1]), Y(S_ALT[0]), ZE - ZK, ZE + ZK))                          # alt yan duvarlar
g = g.fuse(box(X_ALT[0], X_ALT[1], Y(S_ALT[1]), Y(S_ALT[0]), ON_DUVAR[0], ON_DUVAR[1]))           # alt on duvar
g = g.fuse(box(X_ALT[0], X_ALT[1], Y(S_PLAKA_B[1]), Y(S_PLAKA_B[0]), ZE - ZK, ZE + ZK))          # bilek servosu plakasi
g = g.common(kafa)
# dirsek servosu yuvasi (arkadan takilir: pencere arkaya acik) + kulak delikleri
g = g.cut(box(PLAKA_E[0] - 0.1, PLAKA_E[1] + 0.1, Y(30.7), Y(-10.4), ZE - 20, ZE + 10.05))
ED, (tz0, tz1) = mg_delikler()
DELIK_E = [gp((xx, yy, tz0), M_E) for (xx, yy) in ED]           # kulak taban yuzu = plaka ust yuzu (x 203.6)
for q in DELIK_E:
    g = g.cut(cyl(CLEAR[4] / 2, (PLAKA_E[0] - 1, q.y, q.z), (PLAKA_E[1] + 1, q.y, q.z)))
# bilek servosu yuvasi + kulak delikleri
g = g.cut(box(XW + (MG["L"] / 2 - MG["SH"]) - MG["L"] / 2 - 0.2, BILEK_GOVDE_X + MG["L"] / 2 + 0.2,
              Y(S_PLAKA_B[1] + 0.1), Y(S_PLAKA_B[0] - 0.1), ZE - 20, ZE + 10.05))
DELIK_B = [gp((xx, yy, tz0), M_B) for (xx, yy) in ED]
for q in DELIK_B:
    g = g.cut(cyl(CLEAR[4] / 2, (q.x, Y(S_PLAKA_B[0] - 1), q.z), (q.x, Y(S_PLAKA_B[1] + 1), q.z)))
# M5 pim: dayamadan gecis + isil gomme somun deligi
g = g.cut(cyl(2.75, (IC_KOL[1] - 0.1, YE, ZE), (YANAK[0] + 0.1, YE, ZE)))
g = g.cut(insert_hole(5, (YANAK[0], YE, ZE), (1, 0, 0)))
# M1: yanagin ust-arka kosesinde kablo tirnagi (dirsek + bilek kablosu burada birlesir, kablo bagi tirnak + demeti sarar)
KT = A.KOL_KABLO["onkol_tirnak"]
g = g.fuse(box(KT["x"][0], KT["x"][1], YE + KT["dy"][0], YE + KT["dy"][1], ZE + KT["dz"][0], ZE + KT["dz"][1]))
# M1: ara duvarin arka kenarinda bilek servosu kablosu centigi (kablo dirsek servosunun arkasindan yukari cikar)
KC = A.KOL_KABLO["onkol_centik"]
g = g.cut(box(KC["x"][0], KC["x"][1], Y(S_WEB[1]) - 0.01, Y(S_WEB[0]) + 0.01, ZE + KC["dz"][0], ZE + KC["dz"][1]))
I_ONKOL = add("On kol govdesi", "OnKol", g.removeSplitter(), "Baski", "PETG", renk="petg2", patlat=(0, -70, 0),
              not_="arkasi acik U: iki servo arkadan takilir; on yuzu tablada basilir. 1,65 m: ara duvarin altindaki U bolum %.1f mm uzun "
                   "(dirsek -> bilek ekseni %.1f mm)" % (ON_KOL_UZAMA, S_HORN[0]))

# --- 625ZZ ic bilezik + M5 pim civatasi + pul + isil gomme somun
I_RUL_I = add("625ZZ rulman (ic bilezik)", "OnKol", b_in, "Satin", "Celik", kod="(625ZZ ile)", renk="celik",
              patlat=(-25, 0, 0))
I_PUL5 = add("Pim pulu M5", "OnKol", washer(5, (RUL_X, YE, ZE), (-1, 0, 0)), "Baglanti", "Celik", kod="M5 DIN 125 pul",
             renk="celik", patlat=(-45, 0, 0))
I_CIV5 = add("Pim civatasi M5x12", "OnKol", screw912(5, 12, (RUL_X - 1.0, YE, ZE), (1, 0, 0)), "Baglanti", "Celik 8.8",
             kod="M5x12 DIN 912", renk="celik", patlat=(-60, 0, 0))
I_INS5 = add("Isil gomme somun M5 (on kolda)", "OnKol", insert(5, (YANAK[0], YE, ZE), (1, 0, 0)), "Baglanti", "Pirinc",
             kod="M5 isil gomme somun", renk="pirinc", patlat=(0, -70, 0))
BAG.append(dict(ad="Dirsek pimi (servo karsi yatagi)", tip="pim", civata=I_CIV5, pul=I_PUL5, rul_i=I_RUL_I, rul_d=I_RUL_D,
                insert=I_INS5, govde=I_ONKOL, catal=I_CATAL, nokta=(YANAK[0], YE, ZE), yon=(1, 0, 0), agiz=YANAK[0], d=5))

# --- dirsek servosu (govdesi on kolda) + 4x M4x16 + kontra somun
body_e, dome_e, _ = mg996r_local()
I_SERVO_E = add("Dirsek servosu MG996R", "OnKol", yerlestir_m(body_e, M_E), "Satin", "-", kod="MG996R servo", renk="siyah",
                patlat=(0, -70, -60))
add("Dirsek servosu cikis mili", "OnKol", yerlestir_m(dome_e, M_E), "Satin", "-", kod="(servo ile)", renk="siyah",
    patlat=(0, -70, -60))
for q in DELIK_E:
    flat = (0, 0, 1)
    i_cv = add("Dirsek servosu kulak civatasi M4x16", "OnKol", screw912(4, 16, (X_KULAK[1], q.y, q.z), (-1, 0, 0)),
               "Baglanti", "Celik 8.8", kod="M4x16 DIN 912", renk="celik", patlat=(30, -70, -60))
    i_sm = add("Dirsek servosu kontra somunu M4", "OnKol", nut(4, (PLAKA_E[0], q.y, q.z), (-1, 0, 0), "985", flat),
               "Baglanti", "Celik", kod="M4 DIN 985 kontra somun", renk="celik", patlat=(-20, -70, -60))
    BAG.append(dict(ad="Dirsek servosu kulagi", tip="servo_kulak", civata=i_cv, somun=i_sm, servo=I_SERVO_E, govde=I_ONKOL,
                    nokta=(X_KULAK[1], q.y, q.z), yon=(-1, 0, 0), yuz_bas=X_KULAK[1], yuz_somun=PLAKA_E[0], d=4, L=16.0))

# --- bilek servosu (mil asagi) + 4x M4x16 + kontra somun
body_b, dome_b, _ = mg996r_local()
I_SERVO_B = add("Bilek servosu MG996R", "OnKol", yerlestir_m(body_b, M_B), "Satin", "-", kod="MG996R servo", renk="siyah",
                patlat=(0, -70, -60))
add("Bilek servosu cikis mili", "OnKol", yerlestir_m(dome_b, M_B), "Satin", "-", kod="(servo ile)", renk="siyah",
    patlat=(0, -70, -60))
for q in DELIK_B:
    i_cv = add("Bilek servosu kulak civatasi M4x16", "OnKol", screw912(4, 16, (q.x, Y(S_KULAK[1]), q.z), (0, 1, 0)),
               "Baglanti", "Celik 8.8", kod="M4x16 DIN 912", renk="celik", patlat=(0, -95, -60))
    i_sm = add("Bilek servosu kontra somunu M4", "OnKol", nut(4, (q.x, Y(S_PLAKA_B[0]), q.z), (0, 1, 0), "985", (1, 0, 0)),
               "Baglanti", "Celik", kod="M4 DIN 985 kontra somun", renk="celik", patlat=(0, -45, -60))
    BAG.append(dict(ad="Bilek servosu kulagi", tip="servo_kulak", civata=i_cv, somun=i_sm, servo=I_SERVO_B, govde=I_ONKOL,
                    nokta=(q.x, Y(S_KULAK[1]), q.z), yon=(0, 1, 0), yuz_bas=Y(S_KULAK[1]), yuz_somun=Y(S_PLAKA_B[0]),
                    d=4, L=16.0))

# ====================================================================== EL (bilek ekseninde doner)
horn_b, hholes_b = horn_mg_local()
HORN_B = [gp((x, y, 0), M_B) for (x, y) in hholes_b]
I_HORN_B = add("Bilek horn 25T aluminyum disk", "El", yerlestir_m(horn_b, M_B), "Satin", "Aluminyum",
               kod="25T aluminyum disk horn", renk="alu", patlat=(0, -110, 0))
add("Bilek horn merkez vidasi M3", "El", yerlestir_m(horn_vidasi_local(), M_B), "Baglanti", "Celik",
    kod="M3x5 horn vidasi (servo ile)", renk="celik", patlat=(0, -120, 0))
fl = cyl(14.0, (XW, Y(S_FLANS[0]), ZE), (XW, Y(S_FLANS[1]), ZE))
fl = fl.cut(cyl(4.5, (XW, Y(S_FLANS[0] - 0.1), ZE), (XW, Y(S_FLANS[0] + 3.3), ZE)))   # horn merkez vidasi basi (3)
for h in HORN_B:
    fl = fl.cut(cyl(CLEAR[3] / 2, (h.x, Y(S_FLANS[0] - 0.1), h.z), (h.x, Y(S_FLANS[1] + 0.1), h.z)))
    fl = fl.cut(cyl(3.0, (h.x, Y(S_VIDA_B), h.z), (h.x, Y(S_FLANS[1] + 0.1), h.z)))
for sx in (1, -1):
    fl = fl.cut(insert_hole(3, (XW + sx * 14.0, Y(S_VIDA_B), ZE), (-sx, 0, 0)))
I_FLANS = add("Bilek flansi", "El", fl.removeSplitter(), "Baski", "PETG", renk="petg", patlat=(0, -130, 0),
              not_="horn'a 4x M3x8 (havsadan), ele 2x radyal M3")
for h in HORN_B:
    i = add("Flans-horn civatasi M3x8", "El", screw912(3, 8, (h.x, Y(S_VIDA_B), h.z), (0, 1, 0)), "Baglanti", "Celik 8.8",
            kod="M3x8 DIN 912", renk="celik", patlat=(0, -150, 0))
    BAG.append(dict(ad="Bilek flansi -> bilek horn", tip="civata_horn", civata=i, govde=I_FLANS, horn=I_HORN_B,
                    nokta=(h.x, Y(S_VIDA_B), h.z), yon=(0, 1, 0), yuz_bas=Y(S_VIDA_B), horn_yuz=(Y(S_HORN[1]), Y(S_HORN[0])),
                    kasa=Y(S_KASA), d=3, L=8.0))

# --- el: yaka (flansa gecer) + 45 der. gecis + avuc + kanca parmaklar + basparmak (ters basilir: parmaklar tablada)
el = cyl(17.0, (XW, Y(S_YAKA[0]), ZE), (XW, Y(S_YAKA[1]), ZE))
if EL_UZAMA > 0:
    # uzayan yaka ici O22 bos. Y2a (29 Ekim 2026): bosluun ust (baskida yukari, flans tarafi) ucu 45 derece koni: duz tavan O22 kopru
    # olarak destek kontrolune takiliyordu (dirsek_montaj baski: El z 70,5, 24 mm > 15). Koni r 11 -> 0,5, 10,5 mm; kalan 5,5 mm silindir.
    _kb = min(10.5, S_YAKA_BOS[1] - S_YAKA_BOS[0] - 1.0)
    el = el.cut(cyl(11.0, (XW, Y(S_YAKA_BOS[0] + _kb), ZE), (XW, Y(S_YAKA_BOS[1]), ZE)))
    el = el.cut(koni(11.0, 11.0 - _kb, (XW, Y(S_YAKA_BOS[0] + _kb + 0.01), ZE), (XW, Y(S_YAKA_BOS[0]), ZE)))
el = el.fuse(koni(17.0, 7.0, (XW, Y(S_YAKA[1]), ZE), (XW, Y(S_YAKA[1] + 11.0), ZE)))
el = el.fuse(box(XW - 7.0, XW + 7.0, Y(S_UC), Y(S_AVUC[0]), ZE - 25.0, ZE + 25.0))                       # avuc 14 x 50 x 52
el = el.fuse(box(XW - 23.0, XW - 7.0, Y(S_UC), Y(S_UC - 16.0), ZE - 23.0, ZE + 23.0))                     # parmaklar (iceri bukuk)
el = el.fuse(box(XW - 23.0, XW - 19.0, Y(S_UC - 16.0), Y(S_UC - 21.0), ZE - 23.0, ZE + 23.0))             # parmak ucu dudagi
_SY = S_YAKA[1]                                                                                              # (125 cm'de 100,5)
el = el.fuse(prizma([(Y(_SY + 3.7), ZE + 24.0), (Y(_SY + 3.7), ZE + 33.0), (Y(_SY + 20.7), ZE + 33.0), (Y(_SY + 30.7), ZE + 24.0)],
                    "x", XW - 4.0, XW + 4.0))                                                                 # basparmak
el = el.cut(cyl(14.15, (XW, Y(S_YAKA[0] - 0.1), ZE), (XW, Y(S_FLANS[1]), ZE)))                            # flans yuvasi
for sx in (1, -1):
    el = el.cut(cyl(CLEAR[3] / 2, (XW + sx * 13.0, Y(S_VIDA_B), ZE), (XW + sx * 18.0, Y(S_VIDA_B), ZE)))
I_EL = add("El", "El", el.removeSplitter(), "Baski", "PETG", renk="petg2", patlat=(0, -175, 0),
           not_="sabit el: parmaklar 16 mm iceri bukuk + 5 mm dudak (kanca), basparmak onde; yaka %.0f mm uzun (ici O22 bos)" % EL_UZAMA)
for sx in (1, -1):
    i_ins = add("Isil gomme somun M3 (flansta)", "El", insert(3, (XW + sx * 14.0, Y(S_VIDA_B), ZE), (-sx, 0, 0)),
                "Baglanti", "Pirinc", kod="M3 isil gomme somun", renk="pirinc", patlat=(0, -130, 0))
    i_cv = add("Yaka civatasi M3x6 ISO 7380", "El", screw7380(3, 6, (XW + sx * 17.0, Y(S_VIDA_B), ZE), (-sx, 0, 0)),
               "Baglanti", "Celik", kod="M3x6 ISO 7380", renk="celik", patlat=(sx * 30, -175, 0))
    BAG.append(dict(ad="El yakasi -> bilek flansi", tip="radyal", civata=i_cv, insert=i_ins, govde=I_EL, flans=I_FLANS,
                    nokta=(XW + sx * 14.0, Y(S_VIDA_B), ZE), yon=(-sx, 0, 0), agiz_r=14.0, yaka_r=17.0, d=3))

# patlatilmis gorunumde bilek elemanlari el ile birlikte
for p in P:
    if p["grup"] == "El" and p["patlat"] == [0, 0, 0]:
        p["patlat"] = [0, -130, 0]

# ====================================================================== kutle ve agirlik merkezi
DOLULUK = 0.80          # kucuk, kalin cidarli PETG parcalar: 3-4 cevre + %20 dolgu -> etkin doluluk (tahmini)
RHO = {"PETG": A.PETG_RHO * DOLULUK, "Aluminyum": 2.70, "Celik": 7.85, "Celik 8.8": 7.85, "Pirinc": 8.50}
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
    if p["kod"] == "MG996R servo":
        p["kutle"] = MG["kutle_g"]          # datasheet 55 g (cikis mili dahil)
    elif p["kod"] == "(servo ile)":
        p["kutle"] = 0.0
    else:
        p["kutle"] = p["hacim"] / 1000.0 * RHO.get(p["malzeme"], 1.0)
    p["bb"] = p["shape"].BoundBox

# baski parcalari: baski yonu (robot koordinatinda tablaya gore yukari) ve aciklama
BASKI = {
    "Dirsek catali": dict(yukari=(0, -1, 0), yon="ters: pim ve bilezik ucu tablada, kollar yukari"),
    "On kol govdesi": dict(yukari=(0, 0, -1), yon="on yuzu tablada, acik arka yukari"),
    "Bilek flansi": dict(yukari=(0, -1, 0), yon="horn yuzu tablada, havsalar yukari"),
    "El": dict(yukari=(0, 1, 0), yon="ters: parmak ucu ve avuc alti tablada, yaka yukari"),
}

# ====================================================================== kinematik (omuz_parcalar Pp / Pr ile ayni)
XR = TX


def Pp(phi):      # omuz one kaldirma (S1): +phi kolu one kaldirir
    return App.Placement(V(0, 0, 0), App.Rotation(V(-1, 0, 0), phi), V(0, 0, 0))


def Pr(th):       # omuz yana acma (S2): +th kolu disari acar
    return App.Placement(V(0, 0, 0), App.Rotation(V(0, 0, 1), th), V(XR, 0, 0))


def Pe(al):       # dirsek: +al on kolu one buker (ust kola dogru)
    return App.Placement(V(0, 0, 0), App.Rotation(V(*D["eksen_yon"]), al), V(0, YE, ZE))


def Pb(be):       # bilek: on kol ekseni etrafinda
    return App.Placement(V(0, 0, 0), App.Rotation(V(*D["bilek_yon"]), be), V(XW, 0, ZE))


def grup_yer(grup, phi=0.0, th=0.0, al=0.0, be=0.0):
    """Dirsek grubunun omuz yerelindeki yerlesimi (omuz pozuyla birlikte)."""
    m = Pp(phi).multiply(Pr(th))
    if grup in ("OnKol", "El"):
        m = m.multiply(Pe(al))
    if grup == "El":
        m = m.multiply(Pb(be))
    return m


# tarama araliklari (dirsek_montaj ve 2. asama ayni araligi kullanir)
ALS = list(range(-60, 151, 5))
BES = list(range(-90, 91, 15))
YUK_UC = V(*D["el_ucu"])                       # el ucu (tasarim yuku burada)
YUK_KANCA = V(XW - 13.0, Y(S_UC - 20.0), ZE)   # kanca oturma noktasi (bilek torku icin)
