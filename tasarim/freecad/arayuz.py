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
V3_H = 1250.0                   # rc:112 toplam boy (V3 / 125 cm tasarim; yalniz referans)
V3_W = 270.0                    # rc:112 sase disten genislik (aku 181 icin en dar)
# BOY TEK PARAMETRE: 1,65 m (Duffy, 29 Ekim 2026: "boy 1700 degil 1650"). 25 Ekim: "ana projeye 170den devam edeceğiz" (taslak 1,65 m,
# boy karari hoca + ekip 21 Ekim 2026). Govde uzatmasi UZAMA = BOY'dan turer (1650 -> 385; 1700 -> 435); bantlar, direk, omuz, kol, kafa
# konumlari bundan. Taslak varyanti
# tasarim/freecad/taslak-170/ (arsiv) ana tasarima tasindi (Y2a, 26 Ekim 2026). 125 cm geometrisi git gecmisinde (6594c63 ve oncesi).
BOY = 1650.0                    # yerden kafa tepesine (Duffy, 29 Ekim 2026; taslak-170'de 1700)
HEAD_UP = 290.0                 # traversin ust yuzunden kafa tepesine: 10,1" kafa alt yuzu kafa yerelinde y 75 + govde 215 (eski V3 275)
S3 = BOY - 20 - HEAD_UP         # omuz ekseni = travers merkezi yuksekligi (1340; V3 955)
S3_V3 = V3_H - 20 - 275.0       # 955: 125 cm tasarimin omuz ekseni (uzatma referansi)
UZAMA = S3 - S3_V3              # 385 (taslak 1,65 m'de 435): govde kabugu 476,5 dikisinden yukarisi bu kadar yukarida (iki sabit kesitli uzatma bandi)
# Taban genisligi 520 (Duffy, 25 Ekim 2026): tahrik + alt plaka her yana TABAN_DX, etek 520 (kabuk 9. bolum)
TABAN_W_V3 = 444.0              # 125 cm etek genisligi (2 x 222)
TABAN_W = 520.0
TABAN_DX = (TABAN_W - TABAN_W_V3) / 2   # 38
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
TORSO3_Y1 = S3 + 30             # rc:114 govde kabugu ustu (1370; V3 985)

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
DIREK_STOK = 2000.0                  # govde diregi DIREK_L (1650'de 1.185,5; 1700'de 1.235,5) mm TEK PARCA, 2 m stok boydan kesilir (Duffy, 25 Ekim 2026; ek yeri yok)
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
INSERT_DELIK = {3: 4.0, 5: 6.4}                    # baski deligi capi (dis captan kucuk: somun eriyip plastige gomulur).
#   M3 4,0: ruthex M3x5,7 tablosu (dis 4,6); M5 6,4 tahmini (dis - 0,6). Tolerans kuponuyla dogrulanacak.
#   Montajda somun govdesi delik capinda cizilir (takilmis hal); BOM/kutle icin fark ihmal edilir.
GECME = dict(tup_pim=0.25,                       # radyal bosluk, mm: ust kol tupu ic yuzu <-> kol catali pimi
             tup_bilezik=0.25,                  # radyal bosluk, mm: ust kol tupu dis yuzu <-> dirsek sikma bilezigi ic yuzu (M2: 0,1 -> 0,25)
             kabul_max=0.3)                     # dirsek kontrolunun kabul siniri: olculen radyal bosluk bunu asmamali (tup_pim, tup_bilezik)
TUP_PIM_R = 25.4                                 # kol catali / dirsek pimi yaricapi (O50,8); tup ic yaricapi = TUP_PIM_R + GECME['tup_pim']
KABUK_BINDIRME_BOSLUK = 0.25                       # kabuk dili ile komsunun dis yarisi arasi (dil 0,25 mm incelir; 14 Ekim 2026: 0,2 -> 0,25, 15 derece egik gogus duvarinda loft payi 0,15 mm sartina yetmiyordu)
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
DIREK_Y1 = S3 - 20                                 # 1320 (V3 935)
DIREK_L = DIREK_Y1 - DIREK_Y0                      # 1185.5 (V3 800.5)
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
    "kabuk": dict(konum=(0.0, 0.0, 0.0), ayna=False, not_="yerel = global; govde kabugu + taban etegi + S1 kasetleri + braketler"),
}

# Omuz yuvasi: traversin ucuna gecer (omuz yerel x 70...103), 4x M6 + cekic somunla baglanir
OMUZ_YUVA_X = (70.0, 103.0)          # omuz yerel
OMUZ_YUVA_YZ = 25.0                  # yuva dis yari olcusu (y, z +-25)

# Omuz eklem sinirlari (yazilim siniri, derece) - TEK KAYNAK: omuz_montaj (FreeCAD eklemi), carpisma (eklem araligi, tarama
# izgarasi), dirsek_montaj / kabuk_rapor / omuz_rapor (siniri ici suzgeci) ve kod/ortak/eklem_sinirlari.json buradan okur.
OMUZ = dict(
    one_arka_aralik=(-45.0, 135.0),      # S1: DS3235 180 derece, horn kol asagidayken 45'te; geometri -60...180 serbest
    yana_aralik=(5.0, 120.0),            # S2: alt sinir 0 -> +3 (C1, 14 Ekim) -> +5 (S1 kablo kaseti, 15 Ekim 2026): kol S2 3'te
                                         # x 158,8'e, 5'te 160,07'ye iner; tambur / flans x <= 159,5 (planlama/adim2/S1-kaset.md)
    yana_alt_bosluk_mm={0: 4.7, -2: 0.6, -3: 0.0},   # kol/el <-> kabuk en kucuk bosluk (duzeltme plani C1, tarama; -3'te temas)
    servo="DS3235 (180 derece), S1 ve S2",
    # Karar (Duffy, 24 Ekim 2026; taslak-170 kol x1,25): DS3218MG -> DS3235. Govde DS3218 ile ayni kabul (40 x 20 x 40, kulak delikleri
    # 49,5 x 10, 25T): geometri degismedi. Govde yuksekligi kaynaklarda 38,5 / 40 / 40,5: servo gelince kumpasla dogrulanacak. 60 g (datasheet).
    servo_kod="DS3235 servo", servo_ad="DS3235", servo_kutle_g=60.0,
    servo_tork="29 / 32 / 35 kg.cm @ 5 / 6 / 7,4 V (satici tablosu + datasheet); stall servo hattinda ~30,4 @ 5,48 V (taslak-170/kol-analiz HAT modeli)",
    servo_stall_kgcm=30.4,
    # baski parcalari etkin yogunluk = rho x doluluk (M4 omuz baski analizi, 15 Ekim 2026: PETG-CF 0,8...0,9, PETG tup 0,8). Tork
    # icin ust deger (0,9) alinir. rho tahmini (PETG-CF 1,25...1,30).
    baski_rho={"PETG-CF": (1.27, 0.9), "PETG": (1.27, 0.8)},
)


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
_X_BR = (W0 / 2 - 2) + (V3_W - W0) / 2 + TABAN_DX   # rc:95 + xm='s' (133) + TABAN_DX = 171
_X_WH = _X_BR + 2 + 14 + TEKER_W / 2            # rc:96 (178) + TABAN_DX = 216
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
# K4 (3. adim): Raspberry Pi 5 ve MAX98357A kafada (kafa_parcalar; KAFA modulu cizili): eski V3 taban bolgeleri kaldirildi (K3 kontrolu).
for (x, z, l, w, ad) in ((65, -135, 52, 28, "ESP32"), (65, -65, 62.2, 25.4, "PCA9685"),
                         (0, 60, 27, 20, "BNO055")):
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
# Okul yazicisi tablasi 25 x 25 x 25 cm (hoca; model dogrulanmadi; taslak-170 TABLA). 1,65 m'de tum baski parcalari buna da sigmali (Y2a).
YAZICI_OKUL = dict(tabla=(250.0, 250.0, 250.0), hedef=230.0, not_="okul yazicisi (hoca); hedef <= 230 pay icin (taslak-170)")

# =====================================================================================================
# 9) Kabuk modulu (govde kabugu + taban etegi). V3 bicimi: torso_shell3 (rc:611-634), base_cover3 (rc:582-602),
#    cover_bracket3 (rc:604-609), COV3_* (rc:115-117), CHEST3_* (rc:118). Global koordinat, mm.
# =====================================================================================================
KABUK_T = 3.0            # duvar (V3 2,5): bindirmede her yarim 1,5 mm = 3-4 cevre cizgisi (0,42 mm); kararlar raporda
KABUK_BINDIRME = 12.0    # bindirme (dil) genisligi
PETG_RHO = 1.27          # g/cm3 (rc:68)
KABUK_DOLULUK = 0.90     # 3 mm duvar: 2 x 3 cevre (~2,5 mm dolu) + %15 dolgu -> etkin doluluk (tahmini)
PETG_HACIM_HIZI = 10.0   # mm3/s ortalama baski debisi, sure tahmini icin (tahmini; X2D en cok 40 mm3/s)

# --- gogus: egik on duvar (V3 CHEST3 bicimi). Nextion gogus ekrani KALDIRILDI (Duffy, 25 Ekim 2026): ekran, tutucu boss'lar, kablo
#     boslugu ve kabuk penceresi yok; gogus bandi duz / kapali kabuk. Egik duzlem kabuk bicimi olarak kalir (kesit gogus_z ile).
GOGUS_Y = S3 - 135.0     # rc:118 CHEST3_Y: egik duzlemin referans yuksekligi (125 cm'de ekran merkezi 820; 1,65 m'de 1205)
GOGUS_Z = 95.0           # rc:118 CHEST3_ZC: referans yuksekliginde duzlemin (125 cm'de cam onu) z'si
GOGUS_EGIM = 15.0        # rc:118 CHEST3_TILT: duzlem 15 derece yukari bakar
_c15, _s15 = math.cos(math.radians(GOGUS_EGIM)), math.sin(math.radians(GOGUS_EGIM))


def gogus_z(y):
    """Gogus egik on duvarinin DIS yuzu z'si (y'de); 125 cm'de cam duzlemi + duvar."""
    return GOGUS_Z + KABUK_T / _c15 + (GOGUS_Y - y) * _s15 / _c15


# --- govde kabugu: yuvarlatilmis dikdortgen kesitler (y, a = yari genislik, bf = on, bb = arka, r = kose), cizgisel
#     (ruled) loft. V3 elips kesitlerinin olculeri (rc:613-623: 112x82 -> 132x88 -> 152x78) korunup omuzda duz yan duvar
#     (omuz_parcalar "Govde kabugu yan yuzu (referans)": x = 147...152, O84) ve egik gogus on duvari icin kosesi kucuk.
#     1,65 m (Y2a, 26 Ekim 2026): 476,5 dikisinin ustundeki her sey UZAMA (385) yukarida; araya SABIT KESITLI iki uzatma bandi
#     (476,5 ... 861,5). Uzatma kesiti = 125 cm loft'unun 476,5'teki kesiti (cizgisel loft: parametreler dogrusal -> a 125, bf 85,
#     bb 85, r 38). Taslakta kesit 488,5'tekiydi (alt ve ust dikiste 0,7 mm disa basamak birakiyordu); burada basamak yok.
GOVDE_Y0 = Y_COV1 + 1.0                         # etek ustu 262 + 1 mm montaj boslugu
GOVDE_Y1 = TORSO3_Y1                            # 1370 (V3 985)
_GK_V3 = [                                      # 125 cm alt loft'u (V3 y), yalniz referans
    (GOVDE_Y0, 112.0, 82.0, 82.0, 40.0),        # rc:613 alt elips 112 x 82
    (690.0, 138.0, 88.0, 88.0, 36.0),           # rc:613 orta elips 132 x 88 (y 705); genislik eski ekran icin 138
]
UZATMA_Y0 = 476.5                               # uzatma bantlarinin alt dikisi (125 cm'deki ilk yatay dikis)
UZATMA_BANT = 2                                 # 385 / 2 = 192,5 mm (+ 12 dil = 204,5 <= tabla 250; tek bant 397 sigmaz)


def _gk_ara(y):
    """125 cm alt loft'unda (GOVDE_Y0 ... 690) y'deki kesit parametreleri (a, bf, bb, r; dogrusal)."""
    (y0, *a0), (y1, *a1) = _GK_V3[0], _GK_V3[1]
    t = (y - y0) / (y1 - y0)
    return tuple(a0[k] + t * (a1[k] - a0[k]) for k in range(4))


_S_UZ = _gk_ara(UZATMA_Y0)                       # (125, 85, 85, 38)
GOVDE_KESIT = [
    _GK_V3[0],
    (UZATMA_Y0,) + _S_UZ,                        # uzatmanin alt ucu
    (UZATMA_Y0 + UZAMA,) + _S_UZ,                # uzatmanin ust ucu (861,5); ustu 125 cm loft'u UZAMA yukarida
    (690.0 + UZAMA, 138.0, 88.0, 88.0, 36.0),
    (735.0 + UZAMA, 145.0, gogus_z(735.0 + UZAMA), 88.0, 16.0),   # gogus duzlemi basi
    (905.0 + UZAMA, 152.0, gogus_z(905.0 + UZAMA), 80.0, 16.0),   # omuz duz yan duvari basi (x = 152)
    (GOVDE_Y1, 152.0, gogus_z(905.0 + UZAMA), 78.0, 16.0),        # rc:613 ust elips 152 x 78
]
UZATMA_DIKIS = tuple(UZATMA_Y0 + UZAMA * k / UZATMA_BANT for k in range(UZATMA_BANT + 1))   # 476,5 / 669 / 861,5
# yatay birlesimler (1650): 476,5 (alt bant | uzatma 1), 669 (uzatma 1 | 2), 861,5 (uzatma 2 | orta), 1075 (orta | gogus; arka kapak ust kenari),
# 1268 (gogus | omuz; 125 cm'de ekran penceresinin ust kenariydi, pencere artik yok)
GOVDE_DIKIS = UZATMA_DIKIS + (690.0 + UZAMA, 883.0 + UZAMA)
OMUZ_DUVAR = dict(x0=147.0, x1=152.0, delik_r=42.0, ped_r=58.0)   # omuz_parcalar referansi: x 147...152, O84; 5 mm ped
UST_KAPAK_ERISIM = dict(x=86.0, r=7.0)   # omuz yuvasi ust M6 civatasi (omuz_parcalar SLEEVE x = 86, basi S3 + 26,6 ... 32,6): kapakta O14 erisim deligi
BOYUN_ACIKLIK_R = 62.0      # ust kapakta boyun deligi: kafa bolgesi (x+-35, z -25...45) pan ekseni etrafinda donunce r 57 + 5
ARKA_KAPAK = dict(x=80.0, y0=500.0 + UZAMA, y1=690.0 + UZAMA, z0=-200.0, z1=-40.0, r=15.0)   # sokulebilir servis kapagi (ust kenari dikiste)

# --- taban etegi: V3 base_cover3 (rc:582-602). Teker etrafinda her yonde 12 mm (rc:105 COV2_GAP)
# TABAN 520 (Duffy, 25 Ekim 2026; taslak TASLAK_TABAN_W=520 davranisi): tahrik (motor + braket + kaplin + teker) ve alt plaka her yana
# TABAN_DX; etek her yana TABAN_DX genis. Etek x'te UC hucreye bolunur: sag / sol yarilar (125 cm etek yarilariyla ayni sekil, TABAN_DX
# kaymis) + ortada 2 x TABAN_DX dolgu seridi (arka ve on). Boylece her baski parcasi 250 tablaya sigar.
_X_WH3 = (W0 / 2 - 2) + (V3_W - W0) / 2 + 2 + 14 + TEKER_W / 2 + TABAN_DX     # 216 (teker merkezi; V3 178)
_Z_WH3 = L0 / 2 - 65                                               # 185
ETEK_BOSLUK = 12.0
ETEK_A = _X_WH3 + TEKER_W / 2 + ETEK_BOSLUK + KABUK_T              # 260 (V3 222)
ETEK_B = _Z_WH3 + TEKER_D / 2 + ETEK_BOSLUK + KABUK_T              # 262.5 (V3: L0/2 + 10 = 260, onde/arkada 10 mm kaliyordu)
ETEK_KESIT = [
    (35.0, ETEK_A, ETEK_B, ETEK_B, 15.0),       # rc:105 Y_COV2_0 = 35 (yerden); kose r 15 (V3 r 25: teker kosesinde 7 mm kaliyordu)
    (140.0, ETEK_A, ETEK_B, ETEK_B, 15.0),      # rc:117 COV3_Y_KNEE: dik bolum (teker ustu 125)
    (Y_COV1, 150.0 + TABAN_DX, 245.0, 245.0, 60.0),   # rc:116 COV3_TOP 300 x 490, rc:589 r 60 (+ TABAN_DX)
]
ETEK_DIKIS_Z = 87.5          # etek z bolmesi (on / orta / arka)
ETEK_DIKIS_X = (-TABAN_DX, TABAN_DX)   # etek x bolmesi: sol yari | dolgu seridi | sag yari (125 cm'de tek dikis x = 0)
ETEK_ACIKLIK = dict(a=100.0, b=70.0, r=30.0)     # ust plakada govde icine kablo/direk gecisi (govde ic izi 109 x 79). 520'de genisletilmedi:
#   taslakta yarilar kayinca aciklik 276 x 140 oluyor, govde kabugunun iki yaninda 26 mm acik bosluk kaliyordu
ACIL_STOP = dict(x=(W0 / 2 - 70) * V3_W / W0 + TABAN_DX, y=Y_COV1, z=-(L0 / 2 - 50), delik_d=22.4)   # rc:757 + 04 (Emas O22,4); sag yariyla +TABAN_DX
SONAR = dict(x=tuple(v * V3_W / W0 for v in (-100.0, 0.0, 100.0)), y=110.0, dx=13.0, delik_r=8.5)  # rc:752, rc:597 (sonarlar yerinde)

# --- kabugun iskelete baglantisi. Govde braketleri: 400 (alt bant), her uzatma bandina bir cift (bant ortasi - m5_y; taslakla ayni),
#     780 + UZAMA (gogus bandi)
KABUK_GOVDE_BRAKET = dict(y=(400.0,) + tuple(UZATMA_DIKIS[k] + UZAMA / UZATMA_BANT / 2 - 25.0 for k in range(UZATMA_BANT)) + (780.0 + UZAMA,),
                          t=3.0, en=30.0, a_boy=50.0, c_boy=40.0, m6_y=(15.0, 40.0), m5_y=25.0,
                          civata_m6=(6, 14), civata_m5=(5, 10), insert_bosluk=10.0,
                          not_="3 mm Al U braket: direk +-X yuzu kanalina 2x M6x14 pulsuz + cekic somun (14 Ekim 2026), govde yan duvari "
                               "boss'una M5x10 + pul + M5 isil gomme somun (tahmini)")
KABUK_ETEK_BRAKET = dict(z=(-105.0, 0.0, 105.0), t=2.0, en=30.0, x0=105.0, x_ic=214.0 + TABAN_DX, y_alt=106.5,
                         civata_m6=(6, 14), civata_m3=(3, 8), m3_y=121.0,
                         not_="V3 cover_bracket3 (rc:604-609): 2 mm Al L, uzun ray ust kanalina M6x14 + pul + cekic somun, "
                              "etek duvari boss'una M3x8 + M3 isil gomme somun; 520 tabanda yatay kol TABAN_DX uzun")
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



def bolgeler(sahip=None, haric=()):
    return [b for b in BOLGELER if (sahip is None or b["sahip"] == sahip) and b["sahip"] not in haric]


# =====================================================================================================
# 10) Dirsek modulu (sag kol; sol kol = X aynasi). Yerel koordinat = omuz yereli (travers merkezi, X disari, Y yukari,
#     Z ileri). Dirsek parcalarinin hepsi omuzun "Kol" grubuna bagli (omuz S1 + S2 ile birlikte hareket eder); kendi
#     eklemleri dirsek (X ekseni) ve bilek (on kol ekseni). Ev pozu: kol asagida duz (dirsek 0, bilek 0).
#     Ust kol tupu omuz_parcalar'dan: eksen x = XR 185, z = ZC -1,25; y -40...-170 (1,65 m; 125 cm'de -140); O56 / O51,3.
# =====================================================================================================
DIRSEK = dict(
    bagli="omuz:Kol",                         # ust grup omuzun Kol grubuna sabit (Pp(phi) * Pr(th))
    tup_x=185.0, tup_z=-1.25,                 # omuz_parcalar XR, ZC
    tup_uc_y=-170.0, tup_ro=28.0,             # omuz_parcalar "Ust kol tupu" (dis yaricap omuzda elle 28); 1,65 m: tup 100 -> 130 (125 cm'de -140)
    # Kol x1,25 (Duffy, 24 Ekim 2026; taslak-170 KOL125-NOTLAR.md): omuz ekseninden el ucuna 325,5 -> 406,9 mm. Uzama uc yerde:
    #   tup_uzama   : ust kol tupu 100 -> 130 (omuz modulu); dirsek ekseni bu kadar asagi
    #   on_kol_uzama: on kol govdesi, dirsek servosu ile bilek servosu arasindaki U bolum (ara duvar alti s 42 ile bilek servosu
    #                 tabani arasi); bilek servosu + bilek flansi + el bu kadar daha asagi (dirsek_parcalar S sabitleri)
    #   el_uzama    : el yakasi (boyun) 13,6 -> 32,6 mm (O34; ici O22 bos, uclari 1,5 kapali)
    tup_uzama=30.0, on_kol_uzama=32.4, el_uzama=19.0,
    # Dirsek catali DIS kolu (horn tarafi) 5 -> 8 mm, disa (+X) kalinlastirma (Duffy, 25 Ekim 2026: "8mm yap"; kontrol ajani L3 SF 2,99,
    # L4 1,22). Kopru ayni duzleme uzar, kopru ustundeki 45 derece destek dis yuze kadar. Horn civatasi M3x12 + 2x DIN 125-A M3 pul
    # (M3x11 standart degil; uc eski yerde x 216,9: horn'da 3,0 mm dis, kasaya 3,3; pulsuz M3x12 cikis kubbesine 0,58 -> ret).
    catal_dis_kol=8.0, horn_civata=(3, 12), horn_pul=(2, 0.5),
    tup_ri=TUP_PIM_R + GECME["tup_pim"],      # tup ic yaricapi (omuz_parcalar: 25,4 + GECME) = 25,65
    bilezik_ri=28.0 + GECME["tup_bilezik"],   # dirsek sikma bilezigi ic yaricapi = tup_ro + GECME
    bilezik_yarik=4.0,                        # sikma bilezigi yarik genisligi (mm, acik hal). Kapaninca ic yaricap ~ yarik/(2*pi) iner (4 mm -> 0,64);
                                              # tup pime ancak toplam radyal bosluk (tup_pim + tup_bilezik = 0,5) kapanir ve on yuk kalirsa sikisir (eski 2 mm -> 0,32: yetmiyordu)
    bilezik_on_yuk_min=0.1,                   # kapali bilezikte toplam bosluktan arta kalmasi gereken en az radyal on yuk (mm)
    eksen_y=-203.0, eksen_z=-1.25,            # dirsek ekseni (X'e paralel), tup ucundan 33 mm asagida (125 cm'de -173)
    eksen_x=(156.0, 227.9),                   # catalin ic ve dis kolu arasi (eksen dogrusu; dis kol 8 mm: 224,9 -> 227,9)
    eksen_nokta=(216.6, -203.0, -1.25),       # horn alt yuzu (eklem noktasi)
    eksen_yon=(-1.0, 0.0, 0.0),               # +aci on kolu one (+Z) buker (omuz Pp ile ayni isaret)
    aralik=(0.0, 105.0),                      # yazilim siniri (derece): tarama 110 serbest (1,6 mm), 115 carpar; 105te 4,2 mm
    servo="MG996R (180 derece)",
    bilek_x=185.0, bilek_z=-1.25,             # bilek ekseni (Y'ye paralel) = ust kol tupu ekseni hizasi
    bilek_nokta=(185.0, -203.0 - 83.1 - 32.4, -1.25),  # bilek horn ust yuzu (servo tarafi): dirsek ekseninden 83,1 + on_kol_uzama = 115,5
    bilek_yon=(0.0, 1.0, 0.0),
    bilek_aralik=(-90.0, 90.0),               # 180 derece servo, ev 0 = avuc ice (-X) bakar
    el_ucu=(185.0, -203.0 - 152.5 - 32.4 - 19.0, -1.25),    # el ucu (omuz eksenine 406,9 mm; 125 cm'de 325,5)
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
#     1,65 m (Y2a; karar 21 Ekim 2026): 10,1" HDMI yuz ekranli YENI KAFA (kafa/kafa10_lib.py; taslak-170/kafa10.py'den tasindi).
#     Govde ve Pan gruplari 125 cm kafasindan (kafa/kafa7_parcalar.py, KAFA7 olculeri) aynen; egme catali + tilt servosu + 625ZZ pimi
#     boyun yukseltme adaptoruyle (PETG, 4x M3 saplama) adaptor_h yukari; tilt ekseni kafa (Bas) grubunun AM'sinden gecer (denge).
# =====================================================================================================
KAFA7 = dict(                                  # 125 cm kafasi (7" LCD) olculeri: kafa7_parcalar (Govde + Pan + eski Bas) bunlarla kurulur
    tilt_nokta=(26.9, 130.0, 25.0), tilt_aralik=(-25.0, 30.0), kafa_kutu=(210.0, 180.0, 150.0), kafa_alt_y=95.0,
    not_="rc:472 head_shell 210 x 180 x 150; tilt ekseni y 130, z 25; Govde/Pan geometrisi 1,65 m kafasinda aynen kullanilir")
KAFA_EKRAN10 = dict(
    model="Waveshare 10.1inch HDMI LCD (B) 1280x800 (TAHMINI MODEL: hocanin verecegi ekran gelince olculecek)",
    cam=(253.96, 168.60), cam_pencere=(217.96, 136.60), aktif=(216.96, 135.60), kalinlik=18.0,
    panel_t=4.0, kart_ic=6.0, kart_t=5.0, konnektor=(45.0, 12.0, 30.0),   # robot_cad lcd10(): panel 4, arka kart kenardan 6 iceride, 5 kalin
    kutle_g=600.0,
    kaynak="04-parca-olculeri.md (Waveshare 10.1inch HDMI LCD (B) 2D PDF) + robot_cad.py l10_*; kutle robot_cad m_l10 0,60 (tahmini)",
)
_KAFA_ALT = 75.0                 # kafa kabugu alt yuzu (yerel): pan suprulmesinde omuz S1 kaseti tepesi y ~57 + 18 mm pay (V3 95)
_KAFA_GOVDE_Y = (-100.0, 115.0)  # kafa kabugu alt / ust dis yuzu, ekran merkezine gore (215 mm)
_KAFA_DENGE = dict(dy=-13.255, zb=-89.893,      # kafa10_lib.dengele() sonucu (ekran merkezinin tilt eksenine gore y'si, arka dis yuz z'si)
                   kaynak="kafa10_lib.dengele (sekant, 3 tur; taslak-170 26 Ekim 2026 dokumu: Bas 1.431,7 g, AM eksenden 0,046 mm). "
                          "Sabit parametre: kafa_montaj AM'nin eksende kaldigini her kosuda olcer")
KAFA = dict(
    taban_y=S3 + SG / 2,                       # 1360: traversin ust yuzu (yerel y = 0)
    pan_nokta=(0.0, 44.6, 0.0),                # pan horn alt yuzu (pan servosu kasa ustu 41,6 + 3)
    pan_yon=(0.0, 1.0, 0.0),                   # +aci: yuz (+Z) robotun sagina (+X) doner
    pan_aralik=(-90.0, 90.0),                  # MG996R 180 derece; kablo halkasi +-90 icin (kafa_montaj taramasi)
    tilt_nokta=(26.9, _KAFA_ALT - _KAFA_GOVDE_Y[0] - _KAFA_DENGE["dy"], 25.0),   # tilt horn alt yuzu; eksen X'e paralel, y 188,255, z 25 (V3 130)
    tilt_yon=(1.0, 0.0, 0.0),                  # +aci: basi one egme (yuz asagi)
    tilt_aralik=(-13.0, 13.0),                 # yazilim siniri (karar 29 Ekim 2026, Y2a KZ3: +-13; once +-15, ilk cakisma +18 / -17; 125 cm -25...30)
    servo="MG996R (180 derece), pan ve tilt",
    kafa_alt_y=_KAFA_ALT,
    govde_y=_KAFA_GOVDE_Y,
    kafa_kutu=(270.0, _KAFA_GOVDE_Y[1] - _KAFA_GOVDE_Y[0], 47.0 - _KAFA_DENGE["zb"]),   # 270 x 215 x 136,9 (on dis yuz eksenin 47 onunde)
    ekran=KAFA_EKRAN10,
    denge=_KAFA_DENGE,
    adaptor_h=_KAFA_ALT - _KAFA_GOVDE_Y[0] - _KAFA_DENGE["dy"] - KAFA7["tilt_nokta"][1],    # 58,255: boyun yukseltme adaptoru
    kablo_payi=dict(kutle_g=25.0, kaynak="FPC, micro HDMI, USB-C, 12 V (125 cm kafa analizi tahmini); tork hesabina nokta kutle"),
    boyun_plaka=dict(t=3.0, x=(-35.0, 35.0), z=(-25.0, 45.0), kulak_x=48.0, kulak_z=10.0, civata_x=40.0,
                     not_="V3 70x70 (rc:647) + iki yan kulak; 2x M6 traversin ust kanalina (kanal z = 0'da; rc:650'deki "
                          "z -15/35 delikleri kanala denk gelmiyordu)"),
    kaynak="kafa/kafa_parcalar.py (kafa7_parcalar Govde + Pan, kafa10_lib Bas + adaptor)",
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
    plaka=dict(x=V3_W / 2 + TABAN_DX, z=L0 / 2, r=10.0, malzeme="Al 5754, 3 mm (rc:416)"),   # 520 tabanda her yana TABAN_DX (346 x 500)
    plaka_ray_z=(-235.0, -90.0, 90.0, 235.0),     # uzun ray alt kanalina M6 (x = +-115)
    plaka_ara_x=(-50.0, 50.0),                    # ara ray alt kanallarina M6 (z = -230 / 0 / 230)
    plaka_civata=(6, 14),                         # M6x14 DIN 912 PULSUZ (taban_parcalar.PLAKA_PUL=False, 14 Ekim 2026) + M6 cekic somun: bas 3 mm plakada, uc rayin alt yuzunden 11,0 (somun ustu 9,3 -> pay 1,7; kanal tabani 11,8 -> pay 0,8)
    braket_civata=dict(x=UZUN_RAY_X + TABAN_DX, dz=16.0, civata=(4, 16)),   # motor braketi flansi -> plaka; 520 tabanda (x 153) ray disinda:
                                                  # M4x16 + pul alttan, plaka ustunde M4 DIN 985 (125 cm'de uzun ray alt kanalinda cekic somun)
    motor_kablo_delik=((80.0, 200.0), (80.0, 36.0)),            # (x, z) +-x; on motor kablosu z 200, arka motor kablosu plaka altindan z 36
    kablo_delik_d=16.0,
    burc_z=(-230.0, -40.0, 40.0, 230.0),          # M5x40 burc, uzun ray ust kanalinda (V3 -230/230 + kat ayrimi icin -40/40)
    kat_ayrim_z=24.0,                             # on kat z 24,25...250, arka guc paneli z -250...23,75 (0,5 mm aralik)
    kat_kesik_on=(-60.0, 60.0, 150.0, 175.0),     # rc:410 deck_cut (kablo gecisi XL4016 / BTS -> kat)
    aku=dict(merkez=(0.0, Y_RAIL0, _Z_BAT), olcu=(181.0, 77.0, 167.0), kutle_g=2800.0,
             not_="rc:46-47 Landport LFP12-20 olcusu; alinacak Limacell 24 Ah'in olcusu yok (README acik is)"),
    # Aku 75 mm one (Duffy, 25 Ekim 2026 karari; devrilme analizi kutle noktasi olarak): GEOMETRIK OLARAK UYGULANAMADI (Y2a, 26 Ekim 2026).
    # Aku (181 x 77 x 167, yatik) arka bolmede orta ara ray (z -20...20, y 94,5...134,5) ile arka ara ray arasinda; 75 mm onde on yuzu
    # z +37'ye gelir: orta ara ray, direk dibi kose baglantilari (y 134,5...171,5) ve govde diregi (y >= 134,5) akunun icinde kalir.
    # Akunun kutuplari on yuzde (9 mm cikinti) ve takoz araligindan kablolanir -> yerinde birakildi. Secenekler planlama/y2/Y2a-gunluk.md.
    aku_one_karar_mm=75.0, aku_one_uygulanan_mm=0.0,
    kayis_z=(-140.0, -80.0), kayis_en=25.0, kayis_t=1.5,       # 25 mm cirt bant, plakadaki yariklardan (x 90,75...94,25)
    takoz=dict(x=(-80.0, 80.0), y=(Y_RAIL0, Y_RAIL0 + 25.0), z=(-37.5, -20.5)),   # aku on takozu (baski), orta ara rayin arka yuzu -20
    bts=((-85.0 * V3_W / W0, 165.0), (85.0 * V3_W / W0, 165.0)),   # rc:734 (x 'p' olcegi)
    bts_burc=8.0,                                 # M3x8 naylon burc (Al plakaya kisa devre olmasin; ust + alt vida 7,4 mm)
    # E1 (15 Ekim 2026): servo beslemesi ikiye bolundu. K4 ile Pi kafaya gitti; Pi'nin XL4016'si (-49,2; 75) servo B oldu (sayi 3 kalir).
    # Yuk dengesi (planlama/adim3/elektrik.md): A = sag kol + pan (yogun ~4,4 A), B = sol kol + tilt (~4,7 A); XL4016 surekli <= 5 A.
    xl=((-62.0 * V3_W / W0, 75.0, "servo 6 V B (sol kol + tilt)"), (62.0 * V3_W / W0, 75.0, "cevre 5 V"),
        (0.0, 170.0, "servo 6 V A (sag kol + pan)")),   # rc:736 yerleri
    xl_burc=8.0,
    # K4 (14 Ekim 2026): Raspberry Pi 5 kafada (kafa/kafa_parcalar.py). On kattaki eski Pi yeri (-90,5; 80) arayuz kartina verildi.
    arayuz_karti=dict(merkez=(-90.5, 80.0), olcu=(70.0, 50.0), burc=8.0,
                      not_="E2/E3 pertinaks: sonar bolucu x3, aku ADC bolucu, PC817 x2 (acil stop durumu, anahtarli 12 V), role surucu MOSFET + diyot"),
    servo_dagitim=dict(A=(72.0, 205.0), B=(-72.0, 205.0), olcu=(70.0, 50.0), burc=8.0,
                       not_="E1: 16 AWG giris + 2200 uF + 3 pinli cikislar; sinyal PCA9685'ten kisa kopruyle, V+ PCA uzerinden GECMEZ"),
    esp=dict(merkez=(80.0, 75.0), tasiyici=(70.0, 50.0), burc=8.0),   # ESP32 delikli pertinaks tasiyici + disi header ustunde
    pca=dict(merkez=(83.0, 125.0), burc=8.0),
    bno=dict(merkez=(0.0, 60.0), burc=8.0),       # rc:742 (0, 60)
    amp=None,                                     # K4: MAX98357A Pi ile kafaya gitti (I2S boyundan gecmesin); eski yer (-51,6; 40)
    sigorta_kutusu=dict(merkez=(0.0, -203.0), olcu=(105.0, 60.0, 35.0), delik_x=47.0, delik_z=-213.0),   # tahmini zarf; somun akunun arkasinda
    role=dict(merkez=(-112.0, -130.0), olcu=(30.0, 30.0, 45.0)),                         # ISO mini role + soket, tahmini zarf
    ana_sigorta=dict(merkez=(112.0, -130.0), olcu=(30.0, 60.0, 20.0)),                   # kablolu kapakli yuva, tahmini zarf
    ana_anahtar=dict(merkez=(-(W0 / 2 - 70) * V3_W / W0 - TABAN_DX, -(L0 / 2 - 50)), olcu=(50.0, 50.0, 40.0)),   # acil stobun aynasi (sol yariyla -TABAN_DX); tahmini zarf
    sonar_on_z=256.0,                             # HC-SR04 PCB on yuzu; transduserler 12 mm, etek dis yuzunden 5,5 mm tasar
    acil_stop="Emas B200E60 (rc:357-365; 04). Elde B200E-E (40 mm mantar): O60 zarf buyuk tarafta kalir",
    # E0 (15 Ekim 2026): yerinde donus / yay donusu hesabi (taban/donus_hesap.py). OLCUM GELINCE yalniz *_olculen alanlarini doldur:
    # mu_olculen (teker-zemin yanal surtunme), stall_kgcm_olculen (12 V'ta durma torku), stall_A_olculen (durma akimi).
    donus=dict(mu_senaryo=(0.4, 0.5, 0.6), mu_olculen=None,
               stall_kgcm=21.0, stall_kgcm_olculen=None,          # Direnc.net JGB37-520 60 dev/dk sayfasi "21 kg" (durma)
               stall_A=2.8, stall_A_olculen=None, bos_A=0.12,     # 06-aku-secimi.md: 2,4-2,8 A tahmini; bosta 0,08-0,15 A (Direnc)
               surekli_oran=0.30,                                 # surekli = durmanin %30'u (01-donanim-maliyet, mevcut taban hesabi)
               crr=0.03,                                          # yuvarlanma direnci (mevcut taban hesabi)
               omni_mu_yan=0.05,                                  # omni makara yanal direnci (tahmini, olculecek)
               yaw_ivme=1.0,                                      # rad/s2 donus ivmesi (tahmini, yazilim siniri)
               kayma_c=0.05,                                      # lastik kayma (creep) olcegi: kayma/hiz = 0,05'te kuvvet ~0,7 mu N (tahmini)
               not_="Coulomb surtunme dairesi (ana model) + 'yanal tam muN' ust sinir (Wong mu_t(R)); ayrinti donus_hesap.py"),
    # K1 secenegi (a): on iki teker omni. VARSAYILAN KAPALI; True (ya da ortam degiskeni TABAN_OMNI=1) taban CAD'ini omni ile kurar.
    # Aks yeri ayni (motor, braket, kaplin degismez); teker ic yuzu ayni x'te kalir, omni dar oldugu icin merkezi iceri kayar.
    omni=dict(aktif=False, cap=127.0, en=29.0, makara_d=19.0, makara=22, kutle_g=480.0, gobek="12 mm altigen adaptor (tahmini; Nexus 14075 gobegi teyit edilecek)",
              kaynak="Nexus Robot 14075 5 inch double aluminum omni wheel: O127, eksenel 29 mm, 22 makara O19, 480 g, 30 kg "
                     "(ozrobotics.com/shop/double-aluminum-omni-wheel-5-inches-basic-14075/)"),
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
_b("Elektronik kati on yerlesimi (arayuz karti, ESP32, PCA, BNO)", "taban", _k(-136, 116, Y_DECK1, Y_DECK1 + 30, 30, 140),
   "taban_parcalar", "kartlar akunun ustunden on kata alindi; K4 (15 Ekim 2026): Pi kafaya gitti, yerinde arayuz karti")
_b("Servo dagitim kartlari A / B (E1)", "taban", _k(-110, 110, Y_DECK1, Y_DECK1 + 30, 177, 233), "taban_parcalar",
   "on katin on bandi x +-37...107; 16 AWG giris ve servo uzatmalari icin ust pay")
_b("E7 fan yeri (olcume bagli, 40 x 40 x 10)", "taban", _k(-25, 25, Y_DECK0 - 12, Y_DECK0, 85, 135), "planlama/adim3/elektrik.md",
   "uc XL4016'nin ortasinda (-49/75, 49/75, 0/170) kat altina asili 12 V fan, asagi ufler; olcum sart koyarsa takilir (tahmini zarf)")
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


# =====================================================================================================
# 13) Eklem sinirlari ve kafa-kol yasak kutusu (yazilim siniri, derece) - kod/ortak/eklem_sinirlari.json'un kaynagi.
#     Sinirlar modullerdeki tanimlardan (OMUZ, DIRSEK, KAFA) okunur; yeni sayi burada yazilmaz. Uretici: kod/ortak/eklem_sinirlari_uret.py
# =====================================================================================================
# Kafa-kol yasak bolgesi: carpisma taramasinin (5 derece adim, 8 Ekim 2026) buldugu el <-> on yuz kabugu cakismasi.
# Satir satir tablo yerine TEK KUTU: olculen aralik her eksende +-YASAK_PAY genisletilir, eklem araligina kirpilir
# (duzeltme plani C2). Yasak, kol "kol_kosulu" kutusundayken kafanin o kola dogru pan x tilt kutusuna girmesidir;
# sol kol ve sol kafa yonu sag kolun X aynasi (pan isareti ters, tilt ayni).
YASAK_PAY = 5.0
YASAK_OLCULEN = dict(                    # carpisma-sonuc.json kafa_tarama.kol.sag.yasak_ozet (El / Yuz kabugu (on)), 198 kol alt pozu
    one_arka=(125.0, 135.0), yana=(0.0, 0.0), dirsek=(70.0, 105.0), bilek=(-90.0, 90.0),
    pan=(30.0, 55.0), tilt=(25.0, 30.0),
)


def _genislet(aralik, sinir, pay=YASAK_PAY):
    return (max(aralik[0] - pay, sinir[0]), min(aralik[1] + pay, sinir[1]))


_YS_SINIR = dict(one_arka=OMUZ["one_arka_aralik"], yana=OMUZ["yana_aralik"], dirsek=DIRSEK["aralik"],
                 bilek=DIRSEK["bilek_aralik"], pan=KAFA["pan_aralik"], tilt=KAFA["tilt_aralik"])
_YS_KUTU = {k: _genislet(YASAK_OLCULEN[k], _YS_SINIR[k]) for k in YASAK_OLCULEN}
# 1,65 m (Y2a, 26 Ekim 2026): tilt araligi +-15 oldu; 125 cm'de olculen yasak tilt 25...30 araligin DISINDA kaldi -> yasak kutu bos.
# Taslak-170 taramasi (taslak-170/analiz/kafakol_*-yeni.json, kafakol_ince_*): S2 >= 5'te kafa x kol cakismasi 0, en az 7,71 mm
# (El <-> yuz kabugu); S2 = 0 (aralik disi) 357 cakisma. Kesin karar Y4 tam taramasinda.
_YS_AKTIF = all(v[0] < v[1] for v in _YS_KUTU.values())
KAFA_KOL_YASAK = dict(
    aktif=_YS_AKTIF,
    kutu_sag_kol=dict(pan=_YS_KUTU["pan"], tilt=_YS_KUTU["tilt"]) if _YS_AKTIF else None,
    kutu_sol_kol=dict(pan=tuple(-v for v in reversed(_YS_KUTU["pan"])), tilt=_YS_KUTU["tilt"]) if _YS_AKTIF else None,
    kol_kosulu={k: _YS_KUTU[k] for k in ("one_arka", "yana", "dirsek", "bilek")} if _YS_AKTIF else None,
    pay=YASAK_PAY, olculen=YASAK_OLCULEN,
    not_=("kol_kosulu disinda kafa-kol cakismasi taramada yok; kosulsuz uygulamak guvenli ama kafayi gereksiz kisitlar. "
          "Olculen yana 0 idi; S2 alt siniri +5 oldugundan (15 Ekim 2026, S1 kaseti) kosul yana 5...5 olur. Kutu C7 tam taramasiyla dogrulanacak.")
         if _YS_AKTIF else
         ("1,65 m: yasak kutu yok. 125 cm olcumu (tilt 25...30) yeni tilt araliginin (+-13) disinda; taslak-170 kafa x kol taramasi S2 >= 5'te "
          "cakisma 0 (en az 7,71 mm, El <-> yuz kabugu). Y4 tam taramasinda yeniden dogrulanacak."),
)


def eklem_sinirlari():
    """Tum eklem sinirlari + yasak kutu (kod/ortak/eklem_sinirlari_uret.py JSON'a yazar). Saf Python."""
    def j(ad, aralik, servo, neden, **ek):
        return dict(ad=ad, min=float(aralik[0]), max=float(aralik[1]), servo=servo, neden=neden, **ek)

    tek = {
        "s1": j("omuz one-arka (S1)", OMUZ["one_arka_aralik"], OMUZ["servo"],
                "DS3235 180 derece; horn kol asagidayken 45'te; geometri -60...180 serbest"),
        "s2": j("omuz yana acma (S2)", OMUZ["yana_aralik"], OMUZ["servo"],
                "alt sinir +5 (S1 kablo kaseti: kol S2 3'te tambura/flansa yaklasir, 5'te 0,77 mm); kabuk boslugu 0'da 4,7 mm, -3'te temas",
                bosluk_mm={str(k): v for k, v in OMUZ["yana_alt_bosluk_mm"].items()}),
        "dirsek": j("dirsek", DIRSEK["aralik"], DIRSEK["servo"], "MG996R, catal dayanagi"),
        "bilek": j("bilek", DIRSEK["bilek_aralik"], DIRSEK["servo"], "MG996R 180 derece, ev 0 = avuc ice bakar"),
    }
    taraf = {}
    for t, on in (("r", "sag"), ("l", "sol")):
        for k, v in tek.items():
            taraf["%s_%s" % (t, k)] = dict(v, taraf=on, ayna=(t == "l"))
    return dict(
        surum=1, birim="derece", kaynak="tasarim/freecad/arayuz.py (OMUZ, DIRSEK, KAFA, KAFA_KOL_YASAK, KOL_KABLO s1 s2_s1_kosul)",
        eklemler=dict(taraf,
                      pan=j("kafa pan", KAFA["pan_aralik"], KAFA["servo"], "MG996R 180 derece; kablo halkasi +-90"),
                      tilt=j("kafa tilt", KAFA["tilt_aralik"], KAFA["servo"], "yazilim siniri (karar 29 Ekim 2026, Y2a KZ3: +-15 -> +-13; ilk cakisma +18 / -17, planlama/y2/Y2a-kontrol.md); serbest aralik kafa/kafa-analiz.json")),
        teker=dict(sinirsiz=True,
                   ivme_sinir_m_s2=dict(duz_surus=0.5, duz_fren=1.8, rampa_surus=0.1, rampa_fren=0.1),
                   not_=("hiz / ivme siniri yazilimda: duz zeminde <= 0,5 m/s2 (motor surekli torkunun ~%50'si; devrilme payi >= 1,5 "
                         "icin sinir ~2,0 m/s2, el yuku <= 100 g, planlama/y2/Y2b-ivme.json); rampada / egimde <= 0,1 m/s2 ve kollar "
                         "ev pozunda (karar 29 Ekim 2026, Y2a KZ1; aku yerinde). Yazilim / acil stop freni duz zeminde <= 1,8 m/s2 (karar 29 Ekim 2026, "
                         "Y2b): duzde el yukunde 0,5 kg ile bile pay >= 1,54 (yuksuz 1,72, 100 g 1,68; Y2b-ivme.json fren_pay). Rampada / egimde "
                         "yavaslama ve fren de <= 0,1 m/s2 (karar 29 Ekim 2026, Duffy; rampada 1,8 frende ev pozu payi 2,366 / 1,8 = 1,31 < 1,5)")),
        bagimli=[dict(ad="S1 kaseti: S2 lopu <-> kaset kapagi flansi", taraf=t, kosul={"%s_s1" % t: [_K["s1_min"], OMUZ["one_arka_aralik"][1]]},
                      sinir={"%s_s2" % t: [OMUZ["yana_aralik"][0], _K["s2_max"]]},
                      neden="S1 >= %g iken S2 <= %g: S2 lopu (dirsek/bilek kablolari) S2 120'de kaset kapagi flansina yaklasir "
                            "(pahsiz -0,30 mm; 1,2 mm pahla S2 120 +0,39, S2 117 0,89). K3, planlama/adim2/K2-s1-kontrol.md" % (_K["s1_min"], _K["s2_max"]),
                      bosluk_mm=dict(_K["bosluk_mm"]))
                 for t, _K in (("r", KOL_KABLO["s1"]["s2_s1_kosul"]), ("l", KOL_KABLO["s1"]["s2_s1_kosul"]))],
        sol_isaret=dict(deger=-1, durum="tahmini; montajdan sonra her servo tek tek dogrulanir (duzeltme plani C4)"),
        kafa_kol_yasak=(dict(
            aktif=True,
            aciklama="kol kol_kosulu icindeyken kafa o kola dogru kutu icine girmemeli (pan x tilt); sol kol: sol_kol.kutu",
            pay=KAFA_KOL_YASAK["pay"],
            sag_kol=dict(kol_kosulu={k: list(v) for k, v in KAFA_KOL_YASAK["kol_kosulu"].items()},
                         kutu={k: list(v) for k, v in KAFA_KOL_YASAK["kutu_sag_kol"].items()}),
            sol_kol=dict(kol_kosulu={k: list(v) for k, v in KAFA_KOL_YASAK["kol_kosulu"].items()},
                         kutu={k: list(v) for k, v in KAFA_KOL_YASAK["kutu_sol_kol"].items()}),
            olculen={k: list(v) for k, v in YASAK_OLCULEN.items()}, not_=KAFA_KOL_YASAK["not_"])
            if KAFA_KOL_YASAK["aktif"] else
            dict(aktif=False, aciklama="kafa-kol yasak kutusu yok (eklem araliklari icinde cakisma bulunmadi)", pay=KAFA_KOL_YASAK["pay"],
                 olculen_125cm={k: list(v) for k, v in YASAK_OLCULEN.items()}, not_=KAFA_KOL_YASAK["not_"])),
    )


# =====================================================================================================
# 14) Kol kablo yolu (duzeltme plani M1, 14 Ekim 2026). Sag kol, omuz yereli (X disari, Y yukari, Z ileri), ev pozu;
#     sol kol = X aynasi. Dirsek + bilek servo kablolari: on kol -> dirsek arkasindaki serbest lop -> catal koprusu
#     altindaki oluk -> O10 delik -> ust kol tupu ici (birlesim: servo kablosu -> uzatma) -> tupun arka penceresi ->
#     tup / yaka / kopru arkasi -> S2 lopu (kol catali arka plakasinin arkasinda) -> gobek ic seridi. S1 gecisi ACIK
#     (planlama/adim2/M1-kablo-yolu.md: 180 derecelik S1 araliginda tup alt sektoru doldurdugu icin kompakt serbest lop yok).
#     Loplar dirsek/kablo_yolu.py'de duzlemsel elastika ile cozulur; kalici kontrol dirsek_montaj.py (kablo).
# =====================================================================================================
KOL_KABLO = dict(
    serit=(4.2, 1.4),                 # 22 AWG 3 damar duz servo kablosu: genislik, kalinlik (mm). Iletken 0,34 mm2 (Maplin
                                      # Futaba 22AWG); damar dis capi ~1,4 (0,66 iletken + PVC) TAHMINI, kumpasla olculmeli.
                                      # KABLO SPESIFIKASYONU (S1 K1, 25 Ekim 2026; planlama/adim2/K2-s1-kontrol.md B1): butun uzatmalar
                                      # "ince duvarli PVC duz 22 AWG servo kablosu, tek tel (damar) <= 1,5 mm (tercihen <= 1,4)";
                                      # ALMADAN ONCE kumpasla olculur. Neden: S1 U'su (R 12,91 >= 7,5 d + d) ve tambur kanali (dudak arasi
                                      # 4,8 >= 3 d + 0,6) d <= 1,5'te gecer. 22 AWG silikon (60 x 0,08, dis cap 1,7 +-0,1) U'ya da kanala da
                                      # SIGMAZ (R 12,58 < 14,45; 3 x 1,7 = 5,1 > 4,8). Yalniz not: silikon sart olursa kaset duvari r +6
                                      # (75,2 -> 81,2), kanal >= 5,7, L ~190,5, cep/pim yeniden (gorunum ~+6 mm). 26 AWG onerilmez (gerilim
                                      # dusumu ~2,5x; DS3235 stall 3 A).
    servo_kablo_boy=300.0,            # MG996R 30 cm (Tower Pro datasheet), DS3218 300 +-5 (DSServo datasheet)
    jr_disi=(7.9, 2.75, 14.0),        # servo ucundaki disi JR govdesi (Pololu 1924 cizimi)
    jr_erkek=(10.3, 4.0, 18.0),       # uzatmanin erkek JR govdesi (Pololu 1925 cizimi)
    jr_eslesik=(10.3, 4.0, 26.0),     # erkek + disi takili (boy tahmini)
    r_dinamik_kat=7.5, r_sabit_kat=4.0,   # en kucuk bukulme yaricapi = kat x serit kalinligi (Helukabel ornegi: sabit 4 d, dinamik 7,5 d)
    pay_bosluk=0.5,                   # lop ve sabit yol: demet zarfi ile parcalar arasi en az bosluk (mm)
    boy_payi=10.0,                    # servo kablosu tup icine (y -122) ulastiktan sonra en az artan (mm); disi JR ucu orada
                                      # uzatmanin erkek ucuna takilir (birlesim tup icinde y -122...-62 arasinda serbest)
    bag_tabani=(10.0, 10.0, 3.5),     # yapiskan tabanli kablo bagi yuvasi (K noktasi; olcu tahmini) + 2,5 mm kablo bagi
    # --- geometri kesimleri (yalniz malzeme cikarir)
    catal_oluk=dict(x=(182.0, 188.0), y=(-178.0, -173.5), z=(-34.0, -1.25)),   # 1,65 m: tup ucu -170 (125 cm'de y -148...-143,5)   # dirsek catali koprusu + alin kapagi alti: delikten
                                      # kapagin arka kenarina (r31 -> z -32,25) acik oluk; 2 serit (4,2 x 2,8) + pay. Kablo burada sicak tutkal noktasi
    onkol_centik=dict(x=(176.5, 182.5), dz=(-14.01, -9.0)),   # on kol ara duvari (dirsek-bilek servo arasi) arka kenari: bilek kablosu
    onkol_tirnak=dict(x=(172.5, 176.5), dy=(10.5, 16.5), dz=(-19.5, -13.0)),   # yanagin ust-arka kosesinde geriye kanat (eksenden
                                      # dy, dz): iki kablo burada birlesir, kablo bagi kanat + demeti sarar (M). Baskida yukari (on yuz tablada) -> desteksiz
    tup_pencere=dict(x=(180.0, 190.0), y=(-89.0, -65.0), uc=5.0, z=(-32.0, -20.0)),   # ust kol tupu arka duvari: 10 genis, 14 duz +
                                      # iki ucta 45 derece sivri (dik baskida desteksiz); disi JR (7,9 x 2,75) gecer
    # --- serbest loplar (duzlemsel elastika) ve baglama noktalari (konum, cikis tegeti, bagli grup)
    # 1,65 m (Y2a): dirsek ve catal noktalari 30 mm asagi (tup 130), bilek servosu noktalari ayrica on_kol_uzama (32,4) asagi
    dirsek_lop=dict(M=(179.3, -188.0, -17.75), M_teget=(0.0, 0.0, -1.0), M_grup="OnKol",     # on kol tirnagi (eksenden dy 15, dz -16,5), demet geriye
                    F=(185.0, -174.9, -32.75), F_teget=(0.0, 0.0, 1.0), F_grup="UstKol",    # catal olugunun arka agzi (kablo one girer)
                    L=120.0, serit=2, duzlem="x", eklem="dirsek"),
    s2_lop=dict(M=(193.0, -26.0, -38.6), M_teget=(0.0, 1.0, 0.0), M_grup="Kol",              # K: kol catali arka plakasi (z -33) arkasinda kablo bagi tabani
                F=(165.5, -15.0, -32.6), F_teget=(0.0, -1.0, 0.0), F_grup="Gobek",           # G2: gobek kutusu arka yuzu ic seridi (x 163...168; catal plakasi buraya hic girmez)
                L=80.0, serit=2, duzlem="z", eklem="yana", gecis=15.0),                      # z: K duzleminde, son 15 mm'de G2'ye
    # --- sabit yollar (cokgen; her kosede r_sabit yaricapli yay sigmali). Gruplar: OnKol (dirsek), UstKol / Kol (omuz kolu).
    yol_dirsek_servo=dict(grup="OnKol", serit=1, nokta=[(181.0, -192.3, -1.25), (180.0, -185.8, -1.25), (179.3, -188.0, -17.75)],
                          cikis=2.0),         # servo ust yuzundeki cikistan yukari, sonra geriye tirnaga
    yol_bilek_servo=dict(grup="OnKol", serit=1, nokta=[(174.3, -282.9, -1.25), (168.0, -282.9, -1.25), (168.0, -282.9, -12.75),
                                                       (179.5, -281.9, -12.75), (179.5, -194.0, -12.75), (179.3, -188.0, -17.75)],
                         cikis=2.0),          # mil ucu cikisindan ice, geriye, ara duvar centiginden dirsek servosunun arkasindan yukari
    yol_ustkol=dict(grup="UstKol", serit=2, nokta=[(185.0, -174.9, -32.75), (185.0, -174.9, -1.25), (185.0, -152.0, -1.25)]),
    birlesim=(185.0, -105.0, -1.25),  # servo kablosu -> uzatma (tup ici, O51,3; iki eslesik JR yan yana 10,3 x 8 x 26 sigar)
    # Bilek servosu kablosu (1,65 m, Y2a): on kol 32,4 uzadi -> MG996R 300 mm kablosu tup girisine (y -152) ancak ~0,5 mm artanla
    # ulasir (boy_payi 10 saglanmaz). JR yerine LEHIMLI EK (B10 yontemi: lehim + isiyla daralan makaron O <= 4,5, ~25 mm) tup icinde:
    # makaron tup girisinin ustunde serbest kalir. Alternatif: 40 cm kablolu MG996R ya da 15 cm servo uzatmasi (ikinci JR cifti tupte).
    bilek_ek=dict(yontem="lehim + isiyla daralan makaron (B10 ile ayni)", pay_min=0.0, makaron=(4.5, 25.0),
                  not_="dirsek_montaj boy kontrolu: bilek icin artan >= pay_min (JR yok); dirsek servosu JR ile (boy_payi)"),
    yol_uzatma_kol=dict(grup="Kol", serit=2, nokta=[(185.0, -105.0, -1.25), (185.0, -92.0, -12.0), (185.0, -77.0, -31.0),
                                                    (190.5, -60.0, -30.5), (191.0, -46.0, -30.4), (191.0, -40.0, -30.4),
                                                    (191.5, -35.5, -35.0), (192.0, -30.0, -37.2), (193.0, -26.0, -38.6)]),   # tup civatasi basinin (x 185, y -50) yanindan
    # --- S1 gecisi: doner U-lop kaseti (A', 15 Ekim 2026; planlama/adim2/S1-kaset.md). Aci psi: S1 ekseni (omuz yerel X)
    #     etrafinda psi = atan2(-z, y) derece: +Y 0, arka (-Z) 90, asagi 180, on (+Z) 270; S1 +phi gobekteki noktanin psi'sini phi
    #     kadar arttirir (Pp). Kablo G2'den asagi (+psi) iner, tambura +psi yonunde sarilir (ic kosu, tamburla doner), U'da doner,
    #     sabit duvar boyunca -psi yonunde (dis kosu) duvar bagina gelir. U sekli temasli elastika (kablo_yolu.u_lop): pozdan bagimsiz,
    #     yalniz doner. Tambur omuz Gobek grubunda (omuz_parcalar), kaset govdesi kabuk modulunde (kabuk_parcalar).
    s1=dict(durum="A' doner U-lop kaseti (15 Ekim 2026)",
            serit=3,                                    # dirsek + bilek + S2 uzatmalari: uc ayni PVC 22 AWG serit (K1). S2 servo
                                                        # kablosu artik U'dan gecmez, gobekte uzatmaya eklenir (s2_birlesim; B10)
            kanal_x=(153.5, 158.3),                     # tambur dudaklari arasi eksenel kanal: demet 4,2 + 0,6
            tambur=dict(r=(37.0, 39.0), x=(152.5, 159.3), dudak_r=43.7, dudak_t=1.0,     # ic r 37: kapak M3 basi r 36,3 -> 0,7
                        kol_psi=(-30.0, 0.0, 30.0), kol_r=(31.0, 39.0), kol_gen=9.0, kol_x=(159.3, 163.0),   # gobek on yuzune 3 kol
                        vida_r=33.75, vida=(3, 8),       # M3x8 DIN 912 +x yonunde (bas tamburun ic tarafinda), gobekte isil gomme
                        bag_psi=145.0, yay_psi=(142.0, 395.0),    # gobek cercevesi: kablo bagi; halka yalniz ic kosunun gezdigi
                                                        # yayda (C halka): arka-ust 35...142 bos (S2 lopu S2 120'de oradan gecer)
                        # Kablo bagi (K2, 25 Ekim 2026; K2-s1-kontrol B2): halkanin altindan gecen 1,0 mm kablo bagi kayisi kapak
                        # civatasina (r 36,3) carpiyordu. Kelepce sigmiyor (demet 4,2 kanalda 4,8, dudak <-> flans 0,5 radyal; kanal
                        # disinda ankraj yeri yok) -> mumlu polyester BAGLAMA IPI O0,4 (ya da 0,3 x 1,2 serit): ip demetin ustunden,
                        # iki dudak icinde cep (dudak_cep derinlik) boyunca, halkadan radyal kanaldan ve halka ic yuzundeki oluktan
                        # (oluk derinlik) gecen kapali ilmek; ip halka zarfinin icinde kalir (r >= 37 + oluk - d). Iki ilmek ip_psi'de
                        # (eski kayis yariklari: bag + 3 / bag + 11), dugum demetin ustunde kanal ortasinda.
                        ip_psi=(148.0, 156.0), ip=dict(d=0.4, gen=1.0, oluk=0.5, dudak_cep=0.3, delik_eksenel=0.8)),
                        # KZ2 (Y2a, 26 Ekim 2026; K3 baski riski): halka ip deligi eksenel genisligi 0,45 (d + 0,05) -> delik_eksenel 0,8
                        # (yalniz kablo kanalinin altinda: x 153,2...154,0 ve 157,8...158,6; dudak cebi derinligi ayni). +X baskida 4 katman.
            # kaset iki baski parcasi: govde (arka plaka x 152-153 + duvar + dikmeler; arka yuz tablada) ve kapak (flans + dikme
            # basliklari + ust uc pimi; flans tablada). Arka plaka kabugun duz omuz yuzune (x 152) oturur; kabugun x 152'den geri
            # cekildigi on kose ve ust kapak ustunde de kablonun -x kenarini tutar.
            duvar=dict(r=(75.2, 77.2), x0=152.0, arka_t=1.0, flans_x=(158.3, 159.5), flans_r_ic=44.2, psi0=190.0,
                       u_pay=6.5, ic_kes_r=46.5, bolum_x=155.0, havsa_x=156.5, pim=dict(r=57.0, d=3.0, post_r=3.5, bosluk=1.0),
                       # KZ1 (Y2a, 26 Ekim 2026; K3 kontrolu): pim bosluk 0,5 -> 1,0. U ucu esigi pim dikmesiyle sinirliydi (L +2,73 / S1 +3,80);
                       # hesap L +3,73 / S1 +5,19 (hedef >= +3 / +4). u_pay 6,5 KALIR (7,0 esigi degistirmez, yalniz kaseti buyutur).
                       # u_pay 4,5 -> 6,5 (K4, 25 Ekim 2026; B4): U ucu <-> cep ucu 0,34 mm idi (L +0,7 / S1 +1 derece ile temas)
                       # flans ic kenarinin dis (x 159,5) kosesine tam kalinlik pah (K3; B3): S2 lopu S2 120'de flansa -0,30 ->
                       # pahla +0,39; S1 >= 120 iken S2 <= 117 yazilim siniriyla (s2_s1_kosul) 0,89. Ic yuz (x 158,3) r 44,2 korunur.
                       pah=1.2,
                       # ikinci pim (B9 onerisi): ust uc psi 240...335 konsolu govde <-> kapak tek kesit calissin. Pim U'nun suprudugu
                       # halkanin (r < 75,2, psi <= U ucu) icine konamaz -> duvarin disina kulak (govde: dikme + kopru x 152...158,3;
                       # kapak: flans uzantisi + O3 pim -x). Delik r - d/2 - 0,1 > duvar dis r 77,2.
                       pim2=dict(psi=300.0, r=80.0, d=3.0, post_r=3.5, kopru_r=76.2),   # kopru duvarin icinde baslar (r >= 75,2: kanala girmez)
                       # duvar bagi (K4; B4): kaset duvarinda baglama ipi delikleri (O0,4 ip, tamburla ayni). Kayisli kablo bagi
                       # sigmaz: demet <-> arka plaka 0,8, demet <-> flans 0,3 eksenel. Ip duvarin disindan, arka plaka dibindeki
                       # radyal yariktan ve duvar ust kenarindaki centikten gecer, demeti duvara baglar; dugum duvarin disinda.
                       ip_psi=(226.5, 230.0), ip=dict(gen=1.2, arka_x=(153.0, 153.8), ust_x=(157.5, 158.3))),
            alfa_min=10.0,                              # ic / dis kosu en kisa yay acisi (derece; kontrol esigi)
            bag_duvar_psi=228.3, L=171.4,               # duvar bagi (sabit) ve bagdan baga kablo boyu: phi 135'te ic kosu ~10,
                                                        # phi -45'te dis kosu ~10 derece (kontrol dirsek_montaj'da yeniden hesaplar)
            L_tol=(-5.0, 0.0),                          # montaj talimati (K4): lop boyu L 171,4 tek yonlu -5...0 (uzun L U ucunu cebe,
                                                        # kisa L ic kosuyu tambura daha cok sarar); S1 yazilim ust siniri 135 kesin
            # Yazilim bagimli siniri (K3, 25 Ekim 2026; B3): S1 >= s1_min iken S2 <= s2_max. S2 lopu S2 120'de kaset kapagi flansina
            # yaklasir (pahsiz -0,30, pahli +0,39; S2 117'de pahli 0,89). eklem_sinirlari.json "bagimli" listesine girer.
            s2_s1_kosul=dict(s1_min=120.0, s2_max=117.0, bosluk_mm={"S2 120 pahsiz": -0.30, "S2 120 pahli": 0.39, "S2 117 pahli": 0.89}),
            # S2 servo kablosu gobekte uzatmaya eklenir (B10; K2-s1-kontrol "Ayrica"): U'dan 3 ayni PVC serit gecer, DS3235'in 300 +-5 mm
            # kablosunun yarik payi sorunu (en kotu 5 < 7) kalkar. Servo kablosu servodan sonra kisaltilir, ek G2'den once gobek
            # kutusunun arka ic seridinde (sabit; S2 lopundan once) lehim + isiyla daralan makaron ile yapilir, kablo bagiyla tutturulur.
            s2_birlesim=dict(yer="gobek arka ic seridi, G2 oncesi (sabit, S2 lopundan once)", G2_once=20.0,
                             ek="lehim + isiyla daralan makaron (O <= 4,5, ~25 mm); JR cifti (10,3 x 4 x 26) de olur",
                             not_="G2_once ve s2_servo_kablo tahmini; montajda yerinde olculur"),
            dikme=((200.0, 53.0), (226.0, 54.0)), dikme_r=4.0, dikme_vida=(3, 8),   # (psi, r): kabuk omuz pedinde isil gomme
            kulak=dict(x=(138.0, 152.0), z=(38.0, 56.0), t=3.0, vida_xz=(144.0, 47.0), vida=(3, 8)),   # kabuk ust kapagina yatay kulak
            cikis=dict(psi=214.0, r_don=52.0, x_ic=140.0, yarik=(12.0, 6.0)),   # duvar bagi -> duvar boyunca -> psi 214'te radyal
                                                        # ice -> r 52'de ped yarigi (radyal 12 x 6: JR erkek 10,3 x 4 gecer) -> govde ici
            gecis=dict(G2_r=(35.9, 41.1), x=(165.5, 155.9), n=24),   # G2 -> tambur bagi: r ve x, psi boyunca Hermite (sabit yol)
            # govde ici: yarik -> travers arkasi (omuz yereli) -> taban YOL 'Servo 6 V A' (taban_parcalar, global) -> dagitim karti A
            govde_ici=((140.0, -62.0, 18.0), (105.0, -62.0, -26.0), (0.0, -55.0, -26.0)),
            govde_dikey=((0.0, S3 - 55.0, -26.0), (0.0, 400.0, -26.0), (25.0, 262.0, -26.0), (25.0, 230.0, 26.0), (40.0, 205.0, 180.0)),   # global; ilk nokta travers alti (125 cm'de 900)
            s2_servo_kablo=40.0,                        # S2 servo cikisindan G2'ye (tahmini; DS3218 300 mm kablonun kalan boyu bundan)
            jr_pay=30.0),                               # her birlesimde konnektor + bag payi (tahmini)
)


if __name__ == "__main__":
    print("S3 =", S3, "direk", DIREK_Y0, "->", DIREK_Y1, "=", DIREK_L, "mm; uzun ray x", UZUN_RAY_X, "ara ray", ARA_RAY_L)
    print("ayrilmis bolge sayisi:", len(BOLGELER), "; sahipler:", sorted(set(b["sahip"] for b in BOLGELER)))
