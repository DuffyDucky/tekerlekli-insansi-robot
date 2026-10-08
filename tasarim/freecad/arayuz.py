# Robot V3 - FreeCAD modullerinin tek olcu ve arayuz kaynagi (saf Python; FreeCAD olmadan import edilir)
#
# Kurallar
# - Her modul (iskelet, omuz, sonra taban/kabuk/kafa/dirsek) olculeri buradan okur; olcu burada degisir.
# - Kaynak etiketleri: "rc:<satir>" = tasarim/cad/robot_cad.py satiri (V3 gecerli tasarim, yalniz okunur),
#   "04" = raporlar/kaynaklar/04-parca-olculeri.md, "cizim" = ureticinin cizimi. Kaynagi olmayan deger "tahmini".
# - Global koordinat: orijin = zemin, robot merkezi. +X robotun sagi, +Y yukari, +Z ileri (yuz), birim mm.
#   robot_cad.py ile ayni eksenler (rc:5).
import math

# =====================================================================================================
# 1) V3 ana olculeri
# =====================================================================================================
W0 = 340.0                      # rc:78  V1 sase genisligi (V3 olceklemesinin tabani)
L0 = 500.0                      # rc:79  sase derinligi (V3'te de ayni)
V3_H = 1250.0                   # rc:112 toplam boy
V3_W = 270.0                    # rc:112 sase disten genislik (aku 181 icin en dar)
HEAD_UP = 275.0                 # rc:92  traversin ust yuzunden kafa tepesine
S3 = V3_H - 20 - HEAD_UP        # rc:113 omuz ekseni = travers merkezi yuksekligi (955)
TEKER_D = 125.0                 # rc:29  teker capi (04: 125 x 58)
TEKER_W = 58.0                  # rc:29
AX = TEKER_D / 2                # rc:82  aks yuksekligi (62.5)
BR_UP = 29.0                    # rc:83  motor braketi flansi, mil ekseninin ustunde
PL_T = 3.0                      # rc:84  alt plaka kalinligi
Y_PL = AX + BR_UP               # rc:85  alt plaka alt yuzu (91.5)
Y_RAIL0 = Y_PL + PL_T           # rc:86  ray alt yuzu (94.5)
Y_RAIL1 = Y_RAIL0 + 40          # rc:87  ray ust yuzu (134.5)
Y_DECK0 = Y_RAIL1 + 40          # rc:88  elektronik kati alt yuzu (174.5)
DECK_T = 5.0                    # rc:412
Y_DECK1 = Y_DECK0 + DECK_T      # rc:89  (179.5)
Y_COV1 = 90.0 + 172.0           # rc:90-91 taban kapagi ust kenari = govde kabugu alti (262)
TORSO_Y0 = Y_COV1               # rc:466
TORSO3_Y1 = S3 + 30             # rc:114 govde kabugu ustu (985)

# =====================================================================================================
# 2) Sigma profil 40x40 agir, kanal 10 (sigma_profil.py bu degerleri kullanir)
#    04 + Robolink cizimi: kanal 10.2, dudak 4.3, merkez O9, kose delik O5.1 @ 30.2, 1.99 kg/m, kesit 7.32 cm2
# =====================================================================================================
SG = 40.0            # dis olcu
SG_R = 1.5           # dis kose radyusu (rc:183)
SLOT = 10.2          # kanal agzi (cizim)
LIP = 4.3            # dudak kalinligi (rc:49)
CAV_W = 20.0         # kanal ic genisligi (rc:49)
CAV_D = 7.5          # kanal ic derinligi, dudak altindan (rc:49)
CAV_TAB = 13.0       # kanal tabani genisligi (tahmini; kesit alani 732 mm2'ye gore secildi)
CAV_DIK = CAV_D - (CAV_W - CAV_TAB) / 2   # dik bolum; kalan derinlik 45 derece egim
BORE = 9.0           # merkez delik (cizim)
KOSE_D = 5.1         # kose delikleri (cizim)
KOSE_A = 30.2        # kose delik araligi (cizim)
SG_KG_M = 1.99       # uretici kg/m (04)
SG_ALAN = 732.0      # uretici kesit alani mm2 (04)
SG_RHO = 2.70        # 6063 aluminyum g/cm3
SG_E = 69000.0       # elastisite modulu MPa (6063, literatur degeri; tahmini)
SG_RP02 = 110.0      # akma dayanimi MPa (6063-T5 alt sinir, EN 755-2; temper bilinmiyor: tahmini)
# Turetilmis: kanal derinlikleri profil yuzunden olculur
DUDAK_ALTI = LIP                     # cekic somunun ust yuzu yuzden bu kadar iceride
KANAL_TABAN = LIP + CAV_D            # kanal tabani yuzden 11.8 mm iceride (orta 13 mm genislikte duz)
LIP_ALTI_MERKEZ = SG / 2 - LIP       # dudak alt yuzunun profil merkezine uzakligi (15.7)
STOK_BOY = 1000.0                    # satis boyu (Robolink "1 metre"; ozel kesim de var) mm
TESTERE = 3.0                        # kesim payi (tahmini)

# =====================================================================================================
# 3) Standart baglanti elemanlari (ISO/DIN nominal; ortak_lib bunlarla cizer)
# =====================================================================================================
DIN912 = {3: (5.5, 3.0, 2.5), 4: (7.0, 4.0, 3.0), 5: (8.5, 5.0, 4.0), 6: (10.0, 6.0, 5.0)}   # dk, k, s
CLEAR = {3: 3.4, 4: 4.5, 5: 5.5, 6: 6.6}                                                   # gecme delik (ISO 273 orta)
NUT934 = {3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0), 6: (10.0, 5.0)}                      # s, m
NUT985 = {3: (5.5, 4.0), 4: (7.0, 5.0), 5: (8.0, 5.0), 6: (10.0, 6.0)}                      # kontra (naylon) somun
WASH125 = {3: (3.2, 7.0, 0.5), 4: (4.3, 9.0, 0.8), 5: (5.3, 10.0, 1.0), 6: (6.4, 12.0, 1.6)}  # di, do, t
DIN913 = {6: 3.0}                                                                          # set (grub) vida, M6 anahtar 3
INSERT = {3: (4.6, 5.7), 5: (7.0, 7.0)}            # isil gomme somun: dis cap, boy (tahmini tipik)
CEKIC_SOMUN = dict(d=6, L=16.0, W=10.0, T=5.0)     # M6 cekic somun, kanal 10 (tahmini; uzun yonu kanala dik kilitlenir)

# =====================================================================================================
# 4) Kose baglantilari
# =====================================================================================================
# 40x40 genis kose baglanti (satin alinan, Robolink). 37 x 37 x 37.7, 75 g: 04 + rc:436 + Robolink cizimi.
# Cizimde her ayakta ortada TEK oval delik ve kanala giren 9 mm genislikte kama var; iki yanda ceyrek daire
# yan duvar. rc:428 bu parcayi ayak basina z = +-9'da iki delik + orta destekle ciziyor: 40x40 yuzde tek kanal
# oldugu icin +-9 delikler kanala denk gelmez; cizimdeki "9" kama genisligidir. Burada cizim izlendi.
KOSE = dict(
    A=37.0, B=37.0, W=37.7, kutle_g=75.0,        # 04 / rc:436 / cizim
    T=4.5,                                       # ayak kalinligi (tahmini)
    DUVAR=3.0,                                   # yan duvar kalinligi (tahmini)
    DELIK_D=6.6,                                 # rc:432 (r 3.3) -> M6 gecme
    DELIK_M=22.0,                                # delik merkezi, dis koseden (rc:432)
    DELIK_BOY=10.0,                              # oval delik boyu, ayak boyunca (tahmini)
    KAMA_W=9.0,                                  # cizim
    KAMA_H=2.0,                                  # kamanin kanal agzina girme derinligi (tahmini)
    KAMA_X0=8.0,                                 # kama baslangici, dis koseden (tahmini)
    civata=(6, 16),                              # M6x16 DIN 912 + DIN 125 pul + M6 cekic somun
)
# Civata boyu kontrolu (yuzden icerisi): pul 1.6 + ayak 4.5 -> kanal: dudak 4.3 + somun 5.0 = 15.4 <= 16;
# civata ucu yuzden 16 - 6.1 = 9.9 iceride, kanal tabani 11.8 -> 1.9 mm pay.

# Ic kose baglanti, kanal 10 (sase T birlesimleri). Ayaklar iki profilin kanal agzinda + dudak altinda durur,
# disari tasmaz; 2x M6 DIN 913 set vida kanal tabanina dayanip flansi dudaklara sikar. Tum olculer tahmini.
IC_KOSE = dict(
    LEG=26.0,            # ayak boyu, birlesim yuzunden
    BOYUN_W=9.6,         # kanal agzindaki boyun genisligi (agiz 10.2)
    FLANS_W=17.0,        # dudak altindaki flans genisligi (kanal ici 20)
    FLANS_T=3.0,         # flans kalinligi
    VIDA_M=15.0,         # set vidanin birlesim yuzune uzakligi
    vida=(6, 10),        # M6x10 DIN 913: ust ucu yuzden 1.8 iceride, alt ucu kanal tabaninda (11.8)
    rho=7.85,            # celik (tahmini)
)

# =====================================================================================================
# 5) Iskelet yerlesimi (global)  - rc:706-768, V3 olceklemesi rc:836-858 (place_base)
# =====================================================================================================
# Uzun raylar: rc:708 x = +-(W0/2-20), xm='s' -> +-(W0/2-20) + (V3_W-W0)/2 = +-115; Z boyunca L0
UZUN_RAY_X = (W0 / 2 - 20) + (V3_W - W0) / 2       # 115
RAY_YC = Y_RAIL0 + 20                              # 114.5 (rc:708-710)
UZUN_RAY_L = L0                                    # 500 (rc:711)
# Ara raylar: rc:710-712 boy W0-80, sx='Win' -> (V3_W-80)/(W0-80) olcegi -> V3_W - 80 = 190; z = -230, 0, 230
ARA_RAY_L = V3_W - 80                              # 190 (uzun raylarin ic yuzleri arasi)
ARA_RAY_Z = (-(L0 / 2 - 20), 0.0, L0 / 2 - 20)     # rc:709
# Govde diregi: rc:759-761 y = Y_RAIL1'den S3-20'ye (sy='col' olcegi rc:840)
DIREK_Y0 = Y_RAIL1                                 # 134.5
DIREK_Y1 = S3 - 20                                 # 935
DIREK_L = DIREK_Y1 - DIREK_Y0                      # 800.5
# Omuz traversi: rc:765-766, 200 mm, merkez y = S3
TRAVERS_L = 200.0
TRAVERS_Y = S3
# Direk-ray ve direk-travers kose baglantilari: rc:762-768 (direk x yuzlerinde, ikiser adet)
KOSE_YER = [
    # (ad, kose noktasi, donus) donus: "I" = ayak A +X'e yatay / ayak B +Y'ye dik; "Ry180"; "Rx180"; "Rz180"
    ("Direk-ray sag", (20.0, Y_RAIL1, 0.0), "I"),
    ("Direk-ray sol", (-20.0, Y_RAIL1, 0.0), "Ry180"),
    ("Direk-travers sag", (20.0, DIREK_Y1, 0.0), "Rx180"),
    ("Direk-travers sol", (-20.0, DIREK_Y1, 0.0), "Rz180"),
]

# =====================================================================================================
# 6) Modul yerlesimleri: her modulun yerel orijininin global konumu ve donusu
# =====================================================================================================
# ayna=True: yerel geometri once X'te aynalanir (x -> -x), sonra konuma tasinir.
MODULLER = {
    "iskelet": dict(konum=(0.0, 0.0, 0.0), ayna=False, not_="yerel = global"),
    "omuz_sag": dict(konum=(0.0, S3, 0.0), ayna=False,
                     not_="yerel orijin = travers merkezi; X disari (sag), Y yukari, Z ileri"),
    "omuz_sol": dict(konum=(0.0, S3, 0.0), ayna=True, not_="sag omuzun X aynasi"),
    "kabuk": dict(konum=(0.0, 0.0, 0.0), ayna=False, not_="yerel = global; govde kabugu + taban etegi + Nextion + braketler"),
}

# Omuz yuvasi: traversin ucuna gecer (omuz yerel x 70...103), 4x M6 + cekic somunla baglanir
OMUZ_YUVA_X = (70.0, 103.0)          # omuz yerel
OMUZ_YUVA_YZ = 25.0                  # yuva dis yari olcusu (y, z +-25)


def modul_konum(ad):
    m = MODULLER[ad]
    return m["konum"], m["ayna"]


def yerelden_globale(ad, p):
    """Saf Python nokta donusumu (FreeCAD'siz kontrol icin)."""
    (tx, ty, tz), ayna = modul_konum(ad)
    x, y, z = p
    if ayna:
        x = -x
    return (x + tx, y + ty, z + tz)


# =====================================================================================================
# 7) Ayrilmis bolgeler (global kutular). Sonraki moduller bunlarla cakismamali; carpisma.py, henuz
#    cizilmemis modullerin bolgelerini mevcut modullere karsi kontrol eder. Bir modul cizilince kendi
#    bolgeleri yerine gercek geometrisi kontrol edilir.
#    kutu = (x0, x1, y0, y1, z0, z1); bosluk = kutudan cikarilan kutular (ornek: direk gecis deligi)
# =====================================================================================================
def _k(x0, x1, y0, y1, z0, z1):
    return (float(x0), float(x1), float(y0), float(y1), float(z0), float(z1))


def _xs(v):  # V3 'p' olceklemesi (rc:845): x * W/W0
    return v * V3_W / W0


BOLGELER = []


def _b(ad, sahip, kutu, kaynak, not_="", bosluk=()):
    BOLGELER.append(dict(ad=ad, sahip=sahip, kutu=kutu, kaynak=kaynak, not_=not_, bosluk=list(bosluk)))


# --- iskelet (bu modul): sonraki moduller bu hacimlere girmemeli
_h = SG / 2
_b("Sase sigma cercevesi", "iskelet", _k(-V3_W / 2, V3_W / 2, Y_RAIL0, Y_RAIL1, -L0 / 2, L0 / 2), "rc:706-712",
   "uzun raylar x +-(95...135), ara raylar z -230/0/230; ust yuzde orta ray uzerinde direk kose baglantilari")
_b("Govde diregi", "iskelet", _k(-_h, _h, DIREK_Y0, DIREK_Y1, -_h, _h), "rc:759-761")
_b("Direk dibi kose baglantilari", "iskelet", _k(-57, 57, Y_RAIL1, Y_RAIL1 + 37, -18.85, 18.85), "rc:762-764")
_b("Omuz traversi", "iskelet", _k(-TRAVERS_L / 2, TRAVERS_L / 2, S3 - _h, S3 + _h, -_h, _h), "rc:765-766")
_b("Direk-travers kose baglantilari", "iskelet", _k(-57, 57, DIREK_Y1 - 37, DIREK_Y1, -18.85, 18.85), "rc:767-768")
# --- omuz yuvalari (omuz modulu): traversin uclari
for s, ad in ((1, "sag"), (-1, "sol")):
    x0, x1 = sorted((s * OMUZ_YUVA_X[0], s * OMUZ_YUVA_X[1]))
    _b("Omuz yuvasi " + ad, "omuz_" + ad, _k(x0, x1, S3 - OMUZ_YUVA_YZ, S3 + OMUZ_YUVA_YZ, -OMUZ_YUVA_YZ, OMUZ_YUVA_YZ),
       "omuz_montaj.py", "traversin x 70...103 ucu; 4 yuzde M6 civata + cekic somun (x = 86)")
# --- kafa: boyun plakasi traversin ust yuzunun ortasinda (kafa cizildi: carpisma.py bu bolgeler yerine kafa geometrisini tarar)
_b("Boyun plakasi (70x70x3 Al)", "kafa", _k(-35, 35, S3 + _h, S3 + _h + 3, -25, 45), "rc:647-654, rc:783, rc:873",
   "traversin ust yuzu x -35...35 kafaya ayrilmis; baglanti 2x M6 + cekic somun x = +-40, z = 0 (KAFA['boyun_plaka']; V3'teki "
   "4x M5 x +-25, z -15/35 delikleri kanala denk gelmiyordu)")
_b("Kafa pan servosu ve boyun (tahmini zarf)", "kafa", _k(-35, 35, S3 + _h + 3, S3 + _h + 95, -25, 45), "rc:784-788",
   "MG996R pan + U braket + kafa tasiyici; kafa kabugu y = S3+20+95'ten yukari (tahmini)")
# --- taban: plakalar, burclar, aku, guc, elektronik, tahrik, etek braketleri
_b("Alt plaka 3 mm Al", "taban", _k(-V3_W / 2, V3_W / 2, Y_PL, Y_RAIL0, -L0 / 2, L0 / 2), "rc:715, rc:416")
_b("Elektronik kati 5 mm kontrplak", "taban", _k(-V3_W / 2, V3_W / 2, Y_DECK0, Y_DECK1, -L0 / 2, L0 / 2), "rc:716, rc:418",
   "direk icin 44x44 kesik", bosluk=[_k(-22, 22, Y_DECK0 - 1, Y_DECK1 + 1, -22, 22)])
for sx in (-1, 1):
    for sz in (-1, 1):
        _b("M5x40 burc %+d%+d" % (sx, sz), "taban",
           _k(sx * UZUN_RAY_X - 5.3, sx * UZUN_RAY_X + 5.3, Y_RAIL1, Y_DECK0, sz * (L0 / 2 - 20) - 5.3, sz * (L0 / 2 - 20) + 5.3),
           "rc:717-719", "uzun ray ust kanalinda")
_b("LiFePO4 aku (yatik)", "taban", _k(-90.5, 90.5, Y_RAIL0, Y_RAIL0 + 77, -121.5 - 83.5, -121.5 + 83.5), "rc:733, rc:46-47",
   "181 x 77 x 167; uzun ray ic yuzune 4.5 mm")
for x in (-85, 85):
    _b("BTS7960 %+d" % x, "taban", _k(_xs(x) - 25, _xs(x) + 25, Y_RAIL0, Y_RAIL0 + 43, 165 - 25, 165 + 25), "rc:734-735, rc:43")
for (x, z) in ((-62, 75), (62, 75), (0, 170)):
    _b("XL4016 (%d,%d)" % (x, z), "taban", _k(_xs(x) - 32.5, _xs(x) + 32.5, Y_RAIL0, Y_RAIL0 + 23.5, z - 23.5, z + 23.5),
       "rc:736-737, rc:55")
_X_BR = (W0 / 2 - 2) + (V3_W - W0) / 2          # rc:95 + xm='s' (133)
_X_WH = _X_BR + 2 + 14 + TEKER_W / 2            # rc:96 (178)
_Z_WH = L0 / 2 - 65                             # rc:97 (185)
for sx in (-1, 1):
    for sz in (-1, 1):
        _b("Motor + L braket %+d%+d" % (sx, sz), "taban",
           _k(min(sx * (_X_BR - 70), sx * (_X_BR + 2)), max(sx * (_X_BR - 70), sx * (_X_BR + 2)), AX - 21, Y_PL,
              sz * _Z_WH - 21, sz * _Z_WH + 21), "rc:721-727", "plaka altinda")
        _b("Teker %+d%+d" % (sx, sz), "taban",
           _k(sx * _X_WH - TEKER_W / 2, sx * _X_WH + TEKER_W / 2, 0, TEKER_D, sz * _Z_WH - TEKER_D / 2, sz * _Z_WH + TEKER_D / 2),
           "rc:729")
# Etek tasiyici L braketleri (rc:604-609, V3'te taban bolgesiydi) artik kabuk modulunun parcasi: bolgeleri asagida
# (8. bolum, KABUK_ETEK_BRAKET) kabuk sahipli olarak tanimli.
for (x, z, l, w, ad) in ((-75, -120, 85, 56, "Raspberry Pi 5"), (65, -135, 52, 28, "ESP32"), (65, -65, 62.2, 25.4, "PCA9685"),
                         (0, 60, 27, 20, "BNO055"), (-65, 40, 19.4, 17.8, "MAX98357A")):
    _b(ad + " (elektronik kati)", "taban", _k(_xs(x) - l / 2 - 3, _xs(x) + l / 2 + 3, Y_DECK1, Y_DECK1 + 25, z - w / 2 - 3, z + w / 2 + 3),
       "rc:739-743, rc:34-45", "kart olcusu + 3 mm pay; yukseklik 6 mm burc + bilesenler (tahmini)")


# =====================================================================================================
# 8) 3D yazici (ekibin yazicisi, Duffy 08.10.2026: "bizim 3D makine X2D")
#    Uretici teknik sayfasi (08.10.2026'da okundu): https://bambulab.com/en/x2d/specs
# =====================================================================================================
YAZICI = dict(
    model="Bambu Lab X2D",
    nozul="2 (ana + yardimci nozul, cift nozullu sistem)",
    hacim_ana=(256.0, 256.0, 260.0),        # W x D x H, "Main Nozzle Printing"
    hacim_yardimci=(235.5, 256.0, 256.0),   # "Auxiliary Nozzle Printing"
    hacim_cift=(235.5, 256.0, 256.0),       # "Dual Nozzle Printing" (ornek: PETG + destek malzemesi)
    pay=10.0,                               # her eksende birakilan pay (tahmini; kenar, brim, kalibrasyon)
    hazne="aktif isitmali hazne, en cok 65 C",
    nozul_c=300.0, tabla_c=120.0,
    malzeme="PLA, PETG, ABS, ASA, TPU, PA, PC, PET, PVA, 'Support for PLA/PETG' (ana ve yardimci hotend)",
    kaynak="https://bambulab.com/en/x2d/specs",
    durum="dogrulandi (uretici sayfasi, 08.10.2026)",
)
# Tek malzeme PETG ana nozulla basilir: kullanilabilir hacim = ana hacim - pay
YAZICI["kullanilabilir"] = tuple(v - YAZICI["pay"] for v in YAZICI["hacim_ana"])            # 246 x 246 x 250
YAZICI["kullanilabilir_cift"] = tuple(v - YAZICI["pay"] for v in YAZICI["hacim_cift"])      # 225.5 x 246 x 246

# =====================================================================================================
# 9) Kabuk modulu (govde kabugu + taban etegi). V3 bicimi: torso_shell3 (rc:611-634), base_cover3 (rc:582-602),
#    cover_bracket3 (rc:604-609), COV3_* (rc:115-117), CHEST3_* (rc:118). Global koordinat, mm.
# =====================================================================================================
KABUK_T = 3.0            # duvar (V3 2,5): bindirmede her yarim 1,5 mm = 3-4 cevre cizgisi (0,42 mm); kararlar raporda
KABUK_BINDIRME = 12.0    # bindirme (dil) genisligi
PETG_RHO = 1.27          # g/cm3 (rc:68)
KABUK_DOLULUK = 0.90     # 3 mm duvar: 2 x 3 cevre (~2,5 mm dolu) + %15 dolgu -> etkin doluluk (tahmini)
PETG_HACIM_HIZI = 10.0   # mm3/s ortalama baski debisi, sure tahmini icin (tahmini; X2D en cok 40 mm3/s)

# --- gogus ekrani: Nextion NX1060P101_011 (donanim/datasheet/NX1060P101-011C-I_dimension.pdf + nextion.tech sayfasi)
NEXTION = dict(
    pcb=(258.0, 152.0, 1.6),                 # cizim: 258.00 x 152.00, PCB 1.60
    cam=(236.8, 144.8),                      # cizim: 236.80 x 144.80 (LCD + dokunmatik)
    kalinlik=9.8,                            # cizim: 9.80 +-0.2 (cam onu -> PCB arkasi); sayfa "11.5 mm(H)" (bilesenlerle)
    aa=(222.72, 125.28),                     # cizim/sayfa: aktif alan
    va=(235.0, 143.0),                       # sayfa: gorunen alan
    delik_d=3.2, delik_ara=(251.6, 145.6),   # cizim: 4x O3.20, 251.60 x 145.60
    cam_kenar=(10.4, 3.8),                   # cizim: PCB ust (uzun) kenari -> cam 10.40, sag kenar -> cam 3.80
    aa_kenar=(5.64, 9.51),                   # cizim: cam -> aktif alan 5.64 (uzun yon), 9.51 (kisa yon)
    konnektor=(68.44, 15.12, 7.81),          # cizim arka gorunus alt kenar: soldan 68.44, 15.12 genis, kenardan 7.81 (4 pin XH2.54, yorum tahmini)
    bilesen_h=6.0,                           # cizim yan gorunus "6.00": PCB arkasinda en yuksek bilesen (tahmini yorum)
    kutle_g=535.0,                           # nextion.tech/datasheets/nx1060p101-011c-i: Weight 535g
    pencere_pay=1.5,                         # kabuk penceresi = aktif alan + her kenarda 1,5 mm (tahmini)
    kablo_bosluk=30.0,                       # konnektor arkasinda kablo/fis icin (tahmini)
)
GOGUS_Y = S3 - 135.0     # rc:118 CHEST3_Y: ekran merkezi (820)
GOGUS_Z = 95.0           # rc:118 CHEST3_ZC: cam on yuzu merkezde
GOGUS_EGIM = 15.0        # rc:118 CHEST3_TILT: ekran 15 derece yukari bakar
_c15, _s15 = math.cos(math.radians(GOGUS_EGIM)), math.sin(math.radians(GOGUS_EGIM))


def ekran_noktasi(s, v, w):
    """Ekran cercevesi -> global: s = +X (uzun kenar), v = ekranin yukarisi, w = ekran normali (disari, cam onu w=0)."""
    return (s, GOGUS_Y + v * _c15 + w * _s15, GOGUS_Z - v * _s15 + w * _c15)


def gogus_z(y):
    """Gogus egik on duvarinin DIS yuzu (cam duzlemi + duvar): ic yuzu cam onune 0,1 mm (yatay ofset 3 / cos15)."""
    return GOGUS_Z + KABUK_T / _c15 + (GOGUS_Y - y) * _s15 / _c15


# --- govde kabugu: yuvarlatilmis dikdortgen kesitler (y, a = yari genislik, bf = on, bb = arka, r = kose), cizgisel
#     (ruled) loft. V3 elips kesitlerinin olculeri (rc:613-623: 112x82 -> 132x88 -> 152x78) korunup omuzda duz yan duvar
#     (omuz_parcalar "Govde kabugu yan yuzu (referans)": x = 147...152, O84) ve egik gogus on duvari icin kosesi kucuk.
GOVDE_Y0 = Y_COV1 + 1.0                         # etek ustu 262 + 1 mm montaj boslugu
GOVDE_Y1 = TORSO3_Y1                            # 985 (rc:114)
GOVDE_KESIT = [
    (GOVDE_Y0, 112.0, 82.0, 82.0, 40.0),        # rc:613 alt elips 112 x 82
    (690.0, 138.0, 88.0, 88.0, 36.0),           # rc:613 orta elips 132 x 88 (y 705); genislik ekran icin 138
    (735.0, 145.0, gogus_z(735.0), 88.0, 16.0), # gogus duzlemi basi (ekran alt kenari 746,6)
    (905.0, 152.0, gogus_z(905.0), 80.0, 16.0), # omuz duz yan duvari basi (x = 152)
    (GOVDE_Y1, 152.0, gogus_z(905.0), 78.0, 16.0),  # rc:613 ust elips 152 x 78
]
GOVDE_DIKIS = (476.5, 690.0, 883.0)   # yatay birlesimler: 883 = ekran penceresinin ust kenari (pencere ust bantta kopru olmasin)
OMUZ_DUVAR = dict(x0=147.0, x1=152.0, delik_r=42.0, ped_r=58.0)   # omuz_parcalar referansi: x 147...152, O84; 5 mm ped
UST_KAPAK_ERISIM = dict(x=86.0, r=7.0)   # omuz yuvasi ust M6 civatasi (omuz_parcalar SLEEVE x = 86, basi y 981,6...987,6): kapakta O14 erisim deligi
BOYUN_ACIKLIK_R = 62.0      # ust kapakta boyun deligi: kafa bolgesi (x+-35, z -25...45) pan ekseni etrafinda donunce r 57 + 5
ARKA_KAPAK = dict(x=80.0, y0=500.0, y1=690.0, z0=-200.0, z1=-40.0, r=15.0)   # sokulebilir servis kapagi (ust kenari dikiste)

# --- taban etegi: V3 base_cover3 (rc:582-602). Teker etrafinda her yonde 12 mm (rc:105 COV2_GAP)
_X_WH3 = (W0 / 2 - 2) + (V3_W - W0) / 2 + 2 + 14 + TEKER_W / 2     # 178 (teker merkezi)
_Z_WH3 = L0 / 2 - 65                                               # 185
ETEK_BOSLUK = 12.0
ETEK_A = _X_WH3 + TEKER_W / 2 + ETEK_BOSLUK + KABUK_T              # 222
ETEK_B = _Z_WH3 + TEKER_D / 2 + ETEK_BOSLUK + KABUK_T              # 262.5 (V3: L0/2 + 10 = 260, onde/arkada 10 mm kaliyordu)
ETEK_KESIT = [
    (35.0, ETEK_A, ETEK_B, ETEK_B, 15.0),       # rc:105 Y_COV2_0 = 35 (yerden); kose r 15 (V3 r 25: teker kosesinde 7 mm kaliyordu)
    (140.0, ETEK_A, ETEK_B, ETEK_B, 15.0),      # rc:117 COV3_Y_KNEE: dik bolum (teker ustu 125)
    (Y_COV1, 150.0, 245.0, 245.0, 60.0),        # rc:116 COV3_TOP 300 x 490, rc:589 r 60
]
ETEK_DIKIS_Z = 87.5          # etek z bolmesi (on / orta / arka), x = 0'da sag-sol
ETEK_ACIKLIK = dict(a=100.0, b=70.0, r=30.0)     # ust plakada govde icine kablo/direk gecisi (govde ic izi 109 x 79)
ACIL_STOP = dict(x=(W0 / 2 - 70) * V3_W / W0, y=Y_COV1, z=-(L0 / 2 - 50), delik_d=22.4)   # rc:757 + 04 (Emas O22,4)
SONAR = dict(x=tuple(v * V3_W / W0 for v in (-100.0, 0.0, 100.0)), y=110.0, dx=13.0, delik_r=8.5)  # rc:752, rc:597

# --- kabugun iskelete baglantisi
KABUK_GOVDE_BRAKET = dict(y=(400.0, 780.0), t=3.0, en=30.0, a_boy=50.0, c_boy=40.0, m6_y=(15.0, 40.0), m5_y=25.0,
                          civata_m6=(6, 16), civata_m5=(5, 10), insert_bosluk=10.0,
                          not_="3 mm Al U braket: direk +-X yuzu kanalina 2x M6x16 + pul + cekic somun, govde yan duvari "
                               "boss'una M5x10 + pul + M5 isil gomme somun (tahmini)")
KABUK_ETEK_BRAKET = dict(z=(-105.0, 0.0, 105.0), t=2.0, en=30.0, x0=105.0, x_ic=214.0, y_alt=106.5,
                         civata_m6=(6, 14), civata_m3=(3, 8), m3_y=121.0,
                         not_="V3 cover_bracket3 (rc:604-609): 2 mm Al L, uzun ray ust kanalina M6x14 + pul + cekic somun, "
                              "etek duvari boss'una M3x8 + M3 isil gomme somun")
ISO7380 = {3: (5.7, 1.65, 2.0)}      # bombe basli imbus M3: dk, k, s (ISO 7380-1 nominal)

# --- kabuk bolgeleri: etek braketleri kabuk modulunun (V3'te taban bolgesiydi); taban elektronigi (sonar, acil stop)
for sx in (-1, 1):
    for z in KABUK_ETEK_BRAKET["z"]:
        x0, x1 = sorted((sx * KABUK_ETEK_BRAKET["x0"], sx * KABUK_ETEK_BRAKET["x_ic"]))
        _b("Etek tasiyici L braket %+d%+d" % (sx, z), "kabuk", _k(x0, x1, Y_RAIL1, Y_RAIL1 + KABUK_ETEK_BRAKET["t"], z - 15, z + 15),
           "rc:604-609 (V3 cover_bracket3)", "uzun ray ust yuzunde; asagi bukulu ucu etek duvarinda (kabuk_parcalar)")
for x in SONAR["x"]:
    _b("HC-SR04 sonar %+.0f (etek arkasi)" % x, "taban", _k(x - 23.5, x + 23.5, SONAR["y"] - 11, SONAR["y"] + 11, L0 / 2 + 0.5,
                                                           ETEK_B - KABUK_T - 3.0),
       "rc:752, 04 (45 x 20 x 15)", "PCB + arka bilesenler; transduserler etek deliklerinden (O17) gecer")
_es = ACIL_STOP
_b("Acil stop govdesi (etek plakasi alti)", "taban", _k(_es["x"] - 21, _es["x"] + 21, _es["y"] - 48, _es["y"] - KABUK_T - 3,
                                                      _es["z"] - 15, _es["z"] + 15), "rc:357-365, rc:757, 04 (Emas B200E60)",
   "arka govde 42 x 30, panelin 48 mm altina")
_b("Acil stop mantari (etek plakasi ustu)", "taban", _k(_es["x"] - 30, _es["x"] + 30, _es["y"] + 0.5, _es["y"] + 28,
                                                      _es["z"] - 30, _es["z"] + 30), "rc:357-365, 04", "O60 mantar, panel onu 28")


def _nextion_kablo_kutu():
    """Nextion konnektoru arkasindaki kablo/fis boslugu (ekran cercevesinde kutu -> global eksen hizali sinir kutusu)."""
    L, Wd, _ = NEXTION["pcb"]
    s0 = -L / 2
    k0, kw, kk = NEXTION["konnektor"]
    v0, v1 = -Wd / 2 + k0 - 8.0, -Wd / 2 + k0 + kw + 8.0
    w0, w1 = -(NEXTION["kalinlik"] + NEXTION["bilesen_h"] + NEXTION["kablo_bosluk"]), -NEXTION["kalinlik"]
    pts = [ekran_noktasi(s, v, w) for s in (s0, s0 + kk + 25.0) for v in (v0, v1) for w in (w0, w1)]
    return _k(min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts),
              min(p[2] for p in pts), max(p[2] for p in pts))


_b("Nextion konnektor ve kablo boslugu", "kabuk", _nextion_kablo_kutu(), "Nextion cizimi (konnektor), tahmini 30 mm",
   "4 pin XH2.54 fis + kablo donusu; govde braketleri ve diger moduller girmemeli")


def bolgeler(sahip=None, haric=()):
    return [b for b in BOLGELER if (sahip is None or b["sahip"] == sahip) and b["sahip"] not in haric]


# =====================================================================================================
# 10) Dirsek modulu (sag kol; sol kol = X aynasi). Yerel koordinat = omuz yereli (travers merkezi, X disari, Y yukari,
#     Z ileri). Dirsek parcalarinin hepsi omuzun "Kol" grubuna bagli (omuz S1 + S2 ile birlikte hareket eder); kendi
#     eklemleri dirsek (X ekseni) ve bilek (on kol ekseni). Ev pozu: kol asagida duz (dirsek 0, bilek 0).
#     Ust kol tupu omuz_parcalar'dan (degismez): eksen x = XR 185, z = ZC -1,25; y -40...-140; O56 / O51.
# =====================================================================================================
DIRSEK = dict(
    bagli="omuz:Kol",                         # ust grup omuzun Kol grubuna sabit (Pp(phi) * Pr(th))
    tup_x=185.0, tup_z=-1.25,                 # omuz_parcalar XR, ZC
    tup_uc_y=-140.0, tup_ri=25.5, tup_ro=28.0,  # omuz_parcalar "Ust kol tupu"
    eksen_y=-173.0, eksen_z=-1.25,            # dirsek ekseni (X'e paralel), tup ucundan 33 mm asagida
    eksen_x=(156.0, 224.9),                   # catalin ic ve dis kolu arasi (eksen dogrusu)
    eksen_nokta=(216.6, -173.0, -1.25),       # horn alt yuzu (eklem noktasi)
    eksen_yon=(-1.0, 0.0, 0.0),               # +aci on kolu one (+Z) buker (omuz Pp ile ayni isaret)
    aralik=(0.0, 105.0),                      # yazilim siniri (derece): tarama 110 serbest (1,6 mm), 115 carpar; 105te 4,2 mm
    servo="MG996R (180 derece)",
    bilek_x=185.0, bilek_z=-1.25,             # bilek ekseni (Y'ye paralel) = ust kol tupu ekseni hizasi
    bilek_nokta=(185.0, -173.0 - 83.1, -1.25),  # bilek horn ust yuzu (servo tarafi)
    bilek_yon=(0.0, 1.0, 0.0),
    bilek_aralik=(-90.0, 90.0),               # 180 derece servo, ev 0 = avuc ice (-X) bakar
    el_ucu=(185.0, -173.0 - 152.5, -1.25),    # el ucu (omuz eksenine 325,5 mm)
    yuk_g=500.0,                              # el ucunda tasarim yuku (hafif nesne)
    kaynak="dirsek/dirsek_parcalar.py",
)
MODULLER["dirsek_sag"] = dict(konum=(0.0, S3, 0.0), ayna=False,
                              not_="yerel = omuz_sag yereli; omuz Kol grubuna bagli, eklemler dirsek (X) + bilek (on kol ekseni)")
MODULLER["dirsek_sol"] = dict(konum=(0.0, S3, 0.0), ayna=True, not_="sag dirsegin X aynasi (omuz_sol Kol grubuna bagli)")


# =====================================================================================================
# 11) Kafa modulu (boyun + pan + tilt + kafa). Yerel koordinat: orijin = traversin ust yuzu ortasi (0, S3 + 20, 0)
#     (rc:870 Mh ile ayni), X sag, Y yukari, Z ileri. Pan ekseni yerel Y ekseni (x = z = 0; kabuk R62 boyun acikligi bu
#     eksen etrafinda). Ev pozu: duz bakis (pan 0, tilt 0). Gruplar: Govde (traverse sabit), Pan (pan ekseninde doner),
#     Kafa (Pan * tilt). Ayrintilar ve dayanaklari kafa/kafa_parcalar.py ve kafa/rapor.html'de.
# =====================================================================================================
KAFA = dict(
    taban_y=S3 + SG / 2,                       # 975: traversin ust yuzu (yerel y = 0)
    pan_nokta=(0.0, 44.6, 0.0),                # pan horn alt yuzu (pan servosu kasa ustu 41,6 + 3)
    pan_yon=(0.0, 1.0, 0.0),                   # +aci: yuz (+Z) robotun sagina (+X) doner
    pan_aralik=(-90.0, 90.0),                  # MG996R 180 derece; kablo halkasi +-90 icin (kafa_montaj taramasi)
    tilt_nokta=(26.9, 130.0, 25.0),            # tilt horn alt yuzu; eksen X'e paralel, y = 130, z = 25
    tilt_yon=(1.0, 0.0, 0.0),                  # +aci: basi one egme (yuz asagi)
    tilt_aralik=(-25.0, 30.0),                 # yazilim siniri (derece); kafa_montaj taramasi serbest araligi raporlar
    servo="MG996R (180 derece), pan ve tilt",
    kafa_kutu=(210.0, 180.0, 150.0),           # rc:472 head_shell w x h x d (V3); merkez (0, 95 + 90, 10), tepe y = 275 = HEAD_UP
    kafa_alt_y=95.0,                           # rc:789 kafa kabugu alt yuzu (yerel)
    boyun_plaka=dict(t=3.0, x=(-35.0, 35.0), z=(-25.0, 45.0), kulak_x=48.0, kulak_z=10.0, civata_x=40.0,
                     not_="V3 70x70 (rc:647) + iki yan kulak; 2x M6 traversin ust kanalina (kanal z = 0'da; rc:650'deki "
                          "z -15/35 delikleri kanala denk gelmiyordu)"),
    kaynak="kafa/kafa_parcalar.py",
)
MODULLER["kafa"] = dict(konum=(0.0, S3 + SG / 2, 0.0), ayna=False,
                        not_="yerel orijin = traversin ust yuzu ortasi; gruplar Govde (sabit), Pan, Kafa (Pan * tilt)")
# Boyun plakasi kulaklari ve M6 civata baslari, kafaya ayrilmis 70x70 bolgenin disina tasar (yalniz ekleme):
_b("Boyun plakasi kulaklari + M6 civata baslari", "kafa", _k(-53.0, 53.0, S3 + _h, S3 + _h + 16.0, -10.0, 10.0),
   "kafa/kafa_parcalar.py", "traversin ust yuzu x +-35...53; kulak 5 mm PETG + plaka 3 mm, M6x20 + pul + cekic somun x = +-40")


# =====================================================================================================
# 12) Taban modulu (plakalar, tahrik, aku, guc, elektronik kati, sonar, acil stop). Yerel = global (iskelet ve kabuk gibi).
#     V3 yerlesimi (rc:715-757) korunur; degisiklikler ve gerekceleri taban/rapor.html'de. Kaynagi olmayan deger "tahmini".
#     Kat iki parca: on "Elektronik kati" (Pi, ESP32, PCA, BNO, amfi) + arka "Guc paneli" (sigorta kutusu, role, ana sigorta);
#     arka parca akunun ustunde, akuyu degistirirken elektronige dokunmadan sokulur.
# =====================================================================================================
_Z_BAT = -121.5                                   # rc:100 (V3 aku merkezi z)
TABAN = dict(
    plaka=dict(x=V3_W / 2, z=L0 / 2, r=10.0, malzeme="Al 5754, 3 mm (rc:416)"),
    plaka_ray_z=(-235.0, -90.0, 90.0, 235.0),     # uzun ray alt kanalina M6 (x = +-115)
    plaka_ara_x=(-50.0, 50.0),                    # ara ray alt kanallarina M6 (z = -230 / 0 / 230)
    plaka_civata=(6, 14),                         # M6x14 DIN 912 + pul + M6 cekic somun: uc yuzden 9,4 (somun ustu 9,3, taban 11,8)
    braket_civata=dict(x=UZUN_RAY_X, dz=16.0, civata=(4, 16)),   # motor braketi flansi -> plaka -> uzun ray alt kanali (M4 cekic somun)
    motor_kablo_delik=((80.0, 200.0), (80.0, 36.0)),            # (x, z) +-x; on motor kablosu z 200, arka motor kablosu plaka altindan z 36
    kablo_delik_d=16.0,
    burc_z=(-230.0, -40.0, 40.0, 230.0),          # M5x40 burc, uzun ray ust kanalinda (V3 -230/230 + kat ayrimi icin -40/40)
    kat_ayrim_z=24.0,                             # on kat z 24,25...250, arka guc paneli z -250...23,75 (0,5 mm aralik)
    kat_kesik_on=(-60.0, 60.0, 150.0, 175.0),     # rc:410 deck_cut (kablo gecisi XL4016 / BTS -> kat)
    aku=dict(merkez=(0.0, Y_RAIL0, _Z_BAT), olcu=(181.0, 77.0, 167.0), kutle_g=2800.0,
             not_="rc:46-47 Landport LFP12-20 olcusu; alinacak Limacell 24 Ah'in olcusu yok (README acik is)"),
    kayis_z=(-140.0, -80.0), kayis_en=25.0, kayis_t=1.5,       # 25 mm cirt bant, plakadaki yariklardan (x 90,75...94,25)
    takoz=dict(x=(-80.0, 80.0), y=(Y_RAIL0, Y_RAIL0 + 25.0), z=(-37.5, -20.5)),   # aku on takozu (baski), orta ara rayin arka yuzu -20
    bts=((-85.0 * V3_W / W0, 165.0), (85.0 * V3_W / W0, 165.0)),   # rc:734 (x 'p' olcegi)
    bts_burc=8.0,                                 # M3x8 naylon burc (Al plakaya kisa devre olmasin; ust + alt vida 7,4 mm)
    xl=((-62.0 * V3_W / W0, 75.0, "Pi 5,1 V"), (62.0 * V3_W / W0, 75.0, "cevre 5 V"), (0.0, 170.0, "servo 6 V")),   # rc:736
    xl_burc=8.0,
    pi=dict(merkez=(-90.5, 80.0), burc=8.0),      # on kat sol: SD yuvasi -X kenarinda (x -135,5, z 80: etek orta sol hizasi)
    esp=dict(merkez=(80.0, 75.0), tasiyici=(70.0, 50.0), burc=8.0),   # ESP32 delikli pertinaks tasiyici + disi header ustunde
    pca=dict(merkez=(83.0, 125.0), burc=8.0),
    bno=dict(merkez=(0.0, 60.0), burc=8.0),       # rc:742 (0, 60)
    amp=dict(merkez=(-65.0 * V3_W / W0, 40.0)),   # rc:743, kopuk bantla (montaj deligi yok)
    sigorta_kutusu=dict(merkez=(0.0, -203.0), olcu=(105.0, 60.0, 35.0), delik_x=47.0, delik_z=-213.0),   # tahmini zarf; somun akunun arkasinda
    role=dict(merkez=(-112.0, -130.0), olcu=(30.0, 30.0, 45.0)),                         # ISO mini role + soket, tahmini zarf
    ana_sigorta=dict(merkez=(112.0, -130.0), olcu=(30.0, 60.0, 20.0)),                   # kablolu kapakli yuva, tahmini zarf
    ana_anahtar=dict(merkez=(-(W0 / 2 - 70) * V3_W / W0, -(L0 / 2 - 50)), olcu=(50.0, 50.0, 40.0)),   # acil stobun aynasi; tahmini zarf
    sonar_on_z=256.0,                             # HC-SR04 PCB on yuzu; transduserler 12 mm, etek dis yuzunden 5,5 mm tasar
    acil_stop="Emas B200E60 (rc:357-365; 04). Elde B200E-E (40 mm mantar): O60 zarf buyuk tarafta kalir",
)
MODULLER["taban"] = dict(konum=(0.0, 0.0, 0.0), ayna=False,
                         not_="yerel = global; plakalar, tahrik, aku, guc, elektronik kati, sonar, acil stop (statik)")
_T = TABAN
# --- taban: V3 bolgelerine ek yeni bolgeler (yalniz ekleme; eski taban bolgeleri taban cizilince zaten taranmaz)
for sx in (-1, 1):
    for z in (-40.0, 40.0):
        _b("M5x40 burc %+d%+d (kat ayrimi)" % (sx, z), "taban",
           _k(sx * UZUN_RAY_X - 5.3, sx * UZUN_RAY_X + 5.3, Y_RAIL1, Y_DECK0, z - 5.3, z + 5.3), "taban_parcalar",
           "on kat / arka guc paneli birlesimi icin ek burc (uzun ray ust kanali)")
for (x, z) in _T["bts"]:
    _b("BTS7960 %+.0f (8 mm burc ustunde)" % x, "taban", _k(x - 25, x + 25, Y_RAIL0, Y_RAIL0 + _T["bts_burc"] + 43, z - 25, z + 25),
       "taban_parcalar", "V3 bolgesi 8 mm yukseldi: Al plakaya kisa devre olmasin diye naylon burc")
for (x, z, _) in _T["xl"]:
    _b("XL4016 %+.0f,%.0f (8 mm burc ustunde)" % (x, z), "taban", _k(x - 32.5, x + 32.5, Y_RAIL0, Y_RAIL0 + _T["xl_burc"] + 23.5, z - 23.5, z + 23.5),
       "taban_parcalar", "V3 bolgesi 8 mm yukseldi (naylon burc)")
_b("Elektronik kati on yerlesimi (Pi, ESP32, PCA, BNO, amfi)", "taban", _k(-136, 116, Y_DECK1, Y_DECK1 + 30, 30, 140),
   "taban_parcalar", "kartlar akunun ustunden on kata alindi (kat alti somun akuya degmesin, aku servisi)")
_b("Pi 5 fan hava payi", "taban", _k(-128, -60, Y_DECK1 + 24, Y_DECK1 + 39, 55, 105), "taban_parcalar",
   "Active Cooler ustunde 15 mm bos (tahmini)")
_b("Guc paneli (sigorta kutusu, role, ana sigorta)", "taban", _k(-128, 128, Y_DECK1, Y_DECK1 + 46, -234, -99), "taban_parcalar",
   "arka kat; sigorta kutusu tahmini zarf 105 x 60 x 35")
_aa = _T["ana_anahtar"]
_b("Ana anahtar govdesi (etek plakasi alti, oneri)", "taban",
   _k(_aa["merkez"][0] - 25, _aa["merkez"][0] + 25, Y_COV1 - KABUK_T - 3 - 40, Y_COV1 - KABUK_T - 3, _aa["merkez"][1] - 25, _aa["merkez"][1] + 25),
   "taban_parcalar", "ASW-A01 tahmini zarf; kabukta delik acilmasi gerekir (2. asama)")
for x in SONAR["x"]:
    _b("Sonar tutucu %+.0f" % x, "taban", _k(x - (36 if x <= 0 else 26), x + (36 if x >= 0 else 26), 96, 125, ARA_RAY_Z[2] + 20, 257.6),
       "taban_parcalar", "on ara ray on yuzu, M6 ISO 7380 + cekic somun")
_b("Aku on takozu + aku kayislari", "taban", _k(-95, 95, Y_PL - 1.5, Y_RAIL0 + 77 + 2, -205, -20.5), "taban_parcalar",
   "kayis plaka altindan doner (y 90...91,5)")


if __name__ == "__main__":
    print("S3 =", S3, "direk", DIREK_Y0, "->", DIREK_Y1, "=", DIREK_L, "mm; uzun ray x", UZUN_RAY_X, "ara ray", ARA_RAY_L)
    print("ayrilmis bolge sayisi:", len(BOLGELER), "; sahipler:", sorted(set(b["sahip"] for b in BOLGELER)))
