# -*- coding: utf-8 -*-
# Lale 1,58 m - kafa ici ses/USB yerlesim SECENEKLERI: secenek geometrisi (mevcut modeli DEGISTIRMEZ; hicbir dosyaya yazmaz).
# Cerceveler: "bas" = tilt ekseni orijin (kafa10_lib), "ky" = kafa yereli (bas + (0, YT, ZT)), "g" = global ev pozu (ky + (0, 1290, 0)).
# Duffy kararlari 04.11.2026: PAM8403 + USB ses karti kalir; MAX98357A secimle birlikte cikacak (burada yalniz kutle hesabinda dusulur, model degismez).
import os, sys, math
sys.dont_write_bytecode = True
import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
for p_ in (HERE, LALE, UST, os.path.join(UST, "kafa"), os.path.join(UST, "kabuk"), os.path.join(UST, "dirsek")):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import arayuz as A
import kablo_yolu_ekran as KY
from kabuk_lib import damla

YT, ZT = A.KAFA["tilt_nokta"][1], A.KAFA["tilt_nokta"][2]
Y0 = A.KAFA["taban_y"]
DY, ZB = A.KAFA["denge"]["dy"], A.KAFA["denge"]["zb"]
YU, YB = DY + A.KAFA["govde_y"][1], DY + A.KAFA["govde_y"][0]
KT = 2.5
X_IC, Y_IC_UST, Z_ARKA_IC = 135.0 - KT, YU - KT, ZB + KT


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cyl(r, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    return Part.makeCylinder(r, (p1 - p0).Length, p0, p1 - p0)


def bas_g(x, y, z):
    return (x, Y0 + YT + y, ZT + z)


def tasi(sh, v):
    s = sh.copy()
    s.translate(V(*v))
    return s


def bas2g(sh):
    return tasi(sh, (0, Y0 + YT, ZT))


# ------------------------------------------------------------------------- urun olculeri ve kaynaklari
URUN = dict(
    respeaker=dict(olcu="O70 (uretici wiki), PCB 1,2 (STEP) / 1,5 (cizim), bilesen ustu 5,4 (STEP, jak), pin alti 7,7 (STEP); toplam 13,1 (STEP) / 13,3 (Farnell)",
                   delik="3 x O2,2 (STEP: yaricap 1,1; cizim 27,1/7,7 ve 11,5/19,9 ile tutarli)",
                   mikrofon="4 x MP34DT01TR-M; port deligi O0,7 bilesen yuzunde kilifin ustunde (STEP); kare 45,7 x 45,7 (cizim)",
                   guc="5 V, 180 mA LED acik, 170 mA LED kapali (uretici wiki)", kutle_g=30.0,
                   kutle_durum="VARSAYIM. Uretici net kutle vermiyor: 70 g brut (Farnell/RobotShop 'G.W'), 18 g tek uclu satici (dogrulanmadi). Duyarlilik 18 ve 70 g ile ayrica hesaplandi.",
                   kaynak="https://wiki.seeedstudio.com/ReSpeaker_Mic_Array_v2.0/ ; kaynak/RESPEAKER-MIC-3D-v2.0.stp (Seeed), kaynak/respeaker-olcu-1.png"),
    hoparlor=dict(olcu="O40 x 20 (Motorobit sayfasi: '40x20mm', 4 ohm, 3 W)", adet_v4=1, kutle_g=27.0,
                  kutle_durum="VARSAYIM: 27 g Adafruit 3968 (baska urun, raporlar/kaynaklar/04). Motorobit sayfasinda kutle yok. Montaj deligi fotografta gorunmuyor.",
                  kaynak="https://www.motorobit.com/speaker-4-ohm-3w-40mm (v4 satir 30)"),
    pam=dict(olcu_model=(24.0, 18.0, 5.0), olcu_sayfa=(21.0, 18.0, 3.4), kutle_g=3.0, kutle_durum="VARSAYIM (kafa_lib PAM)",
             kaynak="https://www.robotistan.com/23w-mini-amfi-devresi-pam8403 (v4 satir 89): 'U x G x Y 21 x 18 x 3.4 mm', 5 V; akim ve delik yok. Olcumde modelin daha buyuk 24 x 18 x 5 zarfi kullanildi."),
    ses=dict(olcu=(48.0, 24.0, 11.0), fis_usb=12.0, kutle_g=8.0,
             olcu_durum="VARSAYIM: sayfada olcu yok. Fotograftan USB-A eni 12 mm olcegiyle govde ~48 x 24, fis 12 (kaynak/ses-karti-motorobit.jpg); kalinlik 11 kafa_lib tahmini. Modeldeki 45 x 18 x 11 fisi saymiyor.",
             kaynak="https://www.motorobit.com/usb-71-kanal-kulaklik-mikrofon-ses-karti (v4 satir 47): 'USB 2.0', '3.5mm jack giris ve cikis'. Kablosuz, USB-A fisli cubuk (fotograf)."),
    hub=dict(olcu=(72.0, 25.0, 19.0), kutle_g=25.0, kablo_mm=130.0,
             kaynak="https://www.robotistan.com/usb-hub-3lu-mini-usb-a-dahili-guc-anahtari (v4 satir 92): sayfa 72x25x19 ve 73x26x19; 24 g ve 26 g; kablo 130 mm"),
    ai_hat=dict(olcu=(65.0, 56.5), yig_mm=16.0, kutle_g=30.0, kutle_durum="VARSAYIM (olcu ve kutle dogrulanmadi; v4 satir 114 listede, CAD modelinde YOK)"),
)

# ------------------------------------------------------------------------- ReSpeaker (uretici STEP)
STP = os.path.join(HERE, "kaynak", "RESPEAKER-MIC-3D-v2.0.stp")
STP_MIC = [(23.29, 22.33, 1.1), (-23.30, -22.43, 1.1), (-22.39, 23.24, 1.1), (22.38, -23.34, 1.1)]   # STEP port delikleri (z 1,1 = kilif ustu)
STP_DELIK = [(-19.90, -11.54), (-7.73, 27.03), (19.94, -11.54)]
STP_USB_X = -6.82
GAP_JAK = 0.6                       # jak ustu <-> tavan ic yuzu (tasarim secimi)
JAK_UST = 5.4
Y_PCB_UST = Y_IC_UST - GAP_JAK - JAK_UST    # PCB ust yuzu (bas)
_stp = None


def stp_map(cx, cz, xs, ys, zs):
    """STEP -> bas: bilesen yuzu yukari (+Y), USB/jak kenari (STEP -y) +X'e bakar."""
    return (cx - ys, Y_PCB_UST + zs, cz - xs)


def respeaker(cx, cz):
    global _stp
    if _stp is None:
        _stp = Part.read(STP)
    s = _stp.copy()
    # X = -ys + cx, Y = zs + Y_PCB_UST, Z = -xs + cz
    m = App.Matrix(0, -1, 0, cx, 0, 0, 1, Y_PCB_UST, -1, 0, 0, cz, 0, 0, 0, 1)
    s.transformShape(m, True)
    return s


def mic_noktalari(cx, cz):
    return [stp_map(cx, cz, *m) for m in STP_MIC]


def dizi_parcalari(cx, cz):
    """Kabuk tavanina: 4 mikrofon deligi, 3 boss, 3 vida; USB fis zarfi. Tumu bas cercevesi."""
    mic = mic_noktalari(cx, cz)
    delik = [cyl(1.5, (m[0], Y_IC_UST - 0.5, m[2]), (m[0], YU + 1.0, m[2])) for m in mic]
    bo, pil, vi = [], [], []
    for (xs, ys) in STP_DELIK:
        x, y, z = stp_map(cx, cz, xs, ys, 0.0)
        p0 = V(x, Y_IC_UST + 0.05, z)
        bo.append(damla(p0, V(0, -1, 0), 2.5, Y_IC_UST + 0.05 - Y_PCB_UST, V(0, 0, -1)))
        pil.append(cyl(1.0, (x, Y_PCB_UST - 0.1, z), (x, Y_PCB_UST + 5.0, z)))
        vi.append(Part.makeCylinder(1.0, 8.0, V(x, Y_PCB_UST - 1.2, z), V(0, 1, 0)).fuse(Part.makeCylinder(1.9, 1.6, V(x, Y_PCB_UST - 2.8, z), V(0, 1, 0))))
    ux = stp_map(cx, cz, STP_USB_X, -35.0, 1.4)
    fis = box(ux[0], ux[0] + 20.0, ux[1] - 4.0, ux[1] + 4.0, ux[2] - 5.5, ux[2] + 5.5)
    return dict(mic=mic, delik=delik, boss=bo, pilot=pil, vida=vi, usb_fis=fis, usb_uc=(ux[0] + 20.0, ux[1], ux[2]))


# ------------------------------------------------------------------------- hoparlor modulu: hoparlor + basili kap + 2 boss + izgara. Duvar ic noktasi C, n = duvar dis normali
def hoparlor_modul(C, n, e1, yukari):
    """C: duvar ic yuzunde merkez; n: disa birim; e1: duvar duzleminde boss yonu; yukari: baski yukari yonu."""
    C, n, e1 = V(*C), V(*n), V(*e1)
    n.normalize()
    e1.normalize()
    i = n * -1
    hop = Part.makeCylinder(20.0, 20.0, C + i * 0.5, i)
    kap = Part.makeCylinder(23.0, 22.0, C + i * 0.2, i).cut(Part.makeCylinder(20.5, 24.0, C + i * 0.1, i))
    fl = Part.makeCylinder(35.0, 3.0, C + i * 7.2, i).cut(Part.makeCylinder(20.5, 5.0, C + i * 6.2, i))
    # flans yalniz iki kulak: e2 yonunde kirp
    e2 = n.cross(e1)
    e2.normalize()
    w = 11.0
    pts = [C + e1 * 36 + e2 * w, C - e1 * 36 + e2 * w, C - e1 * 36 - e2 * w, C + e1 * 36 - e2 * w, C + e1 * 36 + e2 * w]
    kirp = Part.Face(Part.makePolygon([q + i * 6.0 for q in pts])).extrude(i * 6.0)
    fl = fl.common(kirp)
    kap = kap.fuse(fl).removeSplitter()
    boss = []
    pilot = []
    for sg in (1, -1):
        p = C + e1 * (sg * 31.0) + n * 0.05
        boss.append(damla(p, i, 4.0, 7.25, V(*yukari) * -1))
        pilot.append(Part.makeCylinder(2.3, 6.2, C + e1 * (sg * 31.0) + i * 1.0, i))
    # izgara: O3,5, 6,5 aralik, r 17 icinde (kafes), duvardan gecer
    izg = []
    for a in range(-3, 4):
        for b in range(-3, 4):
            q = e1 * (a * 6.5 + (0.5 * 6.5 if b % 2 else 0.0)) + e2 * (b * 5.63)
            if q.Length <= 17.0:
                izg.append(Part.makeCylinder(1.75, 8.0, C + q + i * 1.0, n))
    return dict(hoparlor=hop, kap=kap, boss=boss, pilot=pilot, izgara=izg, eksen=n, merkez_diyafram=C + i * 0.5, arka=C + i * 20.5)


# gogus alti on duvar (Govde orta bandi): dis yuzu y 960 z 88 -> y 1018,8 z 129,2; dikis y 1005 altinda duz bolge (olcum: isin testi x = 45)
SP_Y, SP_X = 982.5, 45.0
_tan = (106.02 - 92.01) / 20.0                # ic yuzu egimi dz/dy (x = 45 isini: y 970 z 92,01; y 990 z 106,02)
SP_ALFA = math.atan(_tan)
SP_Z_IC = 92.01 + (SP_Y - 970.0) * _tan
SP_N = (0.0, -math.sin(SP_ALFA), math.cos(SP_ALFA))


def hoparlor_gogus():
    return hoparlor_modul((SP_X, SP_Y, SP_Z_IC), SP_N, (1, 0, 0), (0, 1, 0))


def hoparlor_kafa():
    """C secenegi: sol yan duvar (-X), tablanin altinda; bas cercevesinde verilir."""
    return hoparlor_modul((-X_IC, -70.0, -40.0), (-1, 0, 0), (0, 0, 1), (0, 0, 1))


# ------------------------------------------------------------------------- kartlar. sx: duvar (+1 sag, -1 sol)
def duvar_kutu(sx, yc, zc, l, w, h):
    xw = X_IC
    x0, x1 = sorted((sx * (xw - 1.0), sx * (xw - 1.0 - h)))
    return box(x0, x1, yc - w / 2, yc + w / 2, zc - l / 2, zc + l / 2)


def ses_karti(sx, yc, zc):
    """Govde + USB-A fis (-z ucu) + L USB dirsek + uzatma disi ucu (duvardan ice, kablo ice cikar) + L 3,5 mm fis (+z ucu).
    Duz uzatma + duz 3,5 mm fis sigmaz: 30 + 12 + 48 + 32 = 122 mm + 25 mm kablo donusu > 97 mm (z -87,4 ... +10 dikis) ilk olcumde dikis kenetine 30 mm3 girdi.
    Dirsek 16 x 18 x 12, disi uc 30 x 18 x 11, L fis 16 x 10 x 10: hepsi VARSAYIM; listede yok."""
    l, w, h = URUN["ses"]["olcu"]
    g = duvar_kutu(sx, yc, zc, l, w, h)
    fz = zc - l / 2
    usb = duvar_kutu(sx, yc, fz - 6.0, 12.0, 12.0, 4.5)
    dirsek = duvar_kutu(sx, yc, fz - 20.0, 16.0, 18.0, 12.0)
    x0, x1 = sorted((sx * (X_IC - 13.0), sx * (X_IC - 43.0)))
    ek = box(x0, x1, yc - 9.0, yc + 9.0, fz - 25.5, fz - 14.5)
    jak = duvar_kutu(sx, yc - 5.0, zc + l / 2 + 8.0, 16.0, 10.0, 10.0)
    return dict(govde=g, usb=usb, dirsek=dirsek, uzatma=ek, jak=jak, usb_uc=(sx * (X_IC - 43.0), yc, fz - 20.0), jak_uc=(sx * (X_IC - 12.0), yc - 5.0, zc + l / 2 + 8.0))


def ai_hat_zarf():
    x0 = -42.5
    z1 = -27.893
    return box(x0, x0 + 65.0, 41.6 + 16.0, 41.6 + 16.0 + 1.6 + 3.0, z1 - 56.5, z1)


def yarik_kutulari():
    out = []
    for (y0, n) in ((36.0, 3), (72.0, 4)):
        for (x0, x1) in ((-45.0, -10.0), (10.0, 45.0)):
            for k in range(n):
                out.append(box(x0, x1, y0 + 7.0 * k, y0 + 7.0 * k + 3.0, ZB - 1, ZB + KT + 1))
    return out


# ------------------------------------------------------------------------- kablo yollari (global)
KABLO_R = dict(usb=2.0, hoparlor=2.0, ses=1.75)
_Y = KY.yollar()
TRUNK = _Y["HDMI"][2:17]          # bas(-43.5,38,10) ... yer(-4,-40,-36)
INIS = _Y["HDMI"][17]
GOGUS_TOUCH_UC = _Y["USB dokunmatik"][3 + 15 + 1 + 1:]   # (-39, 1205, 30) ... port
GOGUS_TOUCH_ILK = _Y["USB dokunmatik"][3 + 15 + 1]        # (-39, 1205, -32)
PI_USB = dict(p1=(46.0, 51.0, -36.9), p2=(46.0, 44.0, -36.9), p3=(46.0, 51.0, -54.9), p4=(46.0, 44.0, -54.9))   # Pi 5 USB-A yuva agzi (yaklasik; VARSAYIM +-2)
KORIDOR = [bas_g(62.0, 47.0, -37.0), bas_g(62.0, 36.5, -14.0), bas_g(-43.5, 36.5, -13.0)]     # tabla ustu, SY8205 (z >= 3,9) onunde, micro HDMI fislerinin altinda


def bg(p):
    return bas_g(*p)


def gogus_hoparlor_ucu():
    a = hoparlor_gogus()["arka"]
    return [(30.0, 1190.0, -32.0), (62.0, 1185.0, -32.0), (62.0, 1185.0, 35.0), (62.0, 1060.0, 35.0), (62.0, 1003.0, 62.0), (a.x + 4.0, a.y + 2.0, a.z - 2.0)]


def dizi_usb_yolu(cx, cz, kapi="p1"):
    u = dizi_parcalari(cx, cz)["usb_uc"]
    p = PI_USB[kapi]
    return [bg(u), bg((u[0] + 6.0, 72.0, u[2] - 6.0)), bg((68.0, 55.0, p[2])), bg((p[0] + 16.0, p[1], p[2])), bg(p)]


def hub_kablosu_mevcut(kapi="p3"):
    """Pi USB -> modeldeki hub (+X duvar, y 50, z -28): hub'in sabit 130 mm kablosu."""
    p = PI_USB[kapi]
    return [bg(p), bg((p[0] + 16.0, p[1], p[2])), bg((90.0, 50.0, -50.0)), bg((112.0, 50.0, -50.0))]


def uzun(p):
    return sum(math.dist(a, b) for a, b in zip(p[:-1], p[1:]))


def tup(yol, r):
    t = None
    for a_, b_ in zip(yol[:-1], yol[1:]):
        a_, b_ = V(*a_), V(*b_)
        if (b_ - a_).Length < 1e-6:
            continue
        c = Part.makeCylinder(r, (b_ - a_).Length, a_, b_ - a_).fuse(Part.makeSphere(r, b_))
        t = c if t is None else t.fuse(c)
    return t


# ------------------------------------------------------------------------- SECENEKLER
R1 = dict(ad="R1 sag yari", cx=40.0, cz=-30.0, not_="x = 0 dikisine ve tepe civatasina dokunmaz; tek parca (Arka kafa kabugu sag)")
R2 = dict(ad="R2 pan ekseni uzerinde", cx=0.0, cz=-25.0, not_="merkez pan ekseninde; x = 0 dikisini ve 'arka ust' tepe civatasini gecer, civata z -72'ye tasinir; disk kenari z +10 dikisine degiyor")
SES_ADLAR = ("USB ses karti (govde)", "Ses karti USB-A fisi", "L USB dirsek", "USB uzatma disi ucu", "L 3,5 mm fis")
SES_Y, PAM_Y = 47.0, 72.0    # USB uzatma disi ucu y 38 ustunde kalir (tabla civatasi basi y 35); PAM sesin ustunde
SES_ZC = -34.0        # govde z -58 ... -10; L fis +6'ya kadar (dikis +10), dirsek -86'ya kadar (duvar -87,4)
D24_5V = (-80.0, 44.0, 6.0)      # D24V50F5 ustu (kart merkezi)
HUB_LID_Y = (1085.0, 1157.0)


def secenek(harf, lid_z=None):
    """harf: A, B, C ya da R2 (B yerlesimi + R2 dizi konumu).
    Doner: kafa=[...] (bas cercevesi), govde=[...] (global), kablo={ad:(yol,r,liste_boyu,not)}, kaldir=[model parca adlari]."""
    S = dict(harf=harf, kafa=[], govde=[], kablo={}, kaldir=["MAX98357A I2S amfi", "Kopuk bant (MAX98357A)"])
    pam_m, ses_m, hub_m, hop_m = URUN["pam"]["kutle_g"], URUN["ses"]["kutle_g"], URUN["hub"]["kutle_g"], URUN["hoparlor"]["kutle_g"]
    B_YER = harf in ("B", "R2")

    def kafa(ad, renk, sh, kutle=0.0, kurulum=False):
        S["kafa"].append(dict(ad=ad, renk=renk, sh=sh, kutle=kutle, zarf=kurulum))

    def govde(ad, renk, sh, kutle=0.0, kurulum=False):
        S["govde"].append(dict(ad=ad, renk=renk, sh=sh, kutle=kutle, zarf=kurulum))

    R = R2 if harf == "R2" else R1
    S["R"] = R
    d = dizi_parcalari(R["cx"], R["cz"])
    S["dizi"] = d
    kafa("ReSpeaker Mic Array v2.0", "dizi", respeaker(R["cx"], R["cz"]), URUN["respeaker"]["kutle_g"])
    kafa("Dizi USB fis zarfi", "zarf", d["usb_fis"], 0.0, True)
    for k, b in enumerate(d["boss"]):
        kafa("Dizi boss %d" % k, "boss", b, b.Volume / 1000.0 * 1.27 * 0.8)
    for k, v in enumerate(d["vida"]):
        kafa("Dizi vidasi M2x8 PT %d" % k, "celik", v, v.Volume / 1000.0 * 7.85)

    # ses karti + PAM: tum seceneklerde sol (-X) duvar. B'de once sag duvar denendi: PAM 5 V ve hoparlor kablosu dizi USB'sine 9,8 / 12,1 mm kaldi
    # (oneri satir 199: dizi USB'si guc kablolarindan ayri kanal); sol duvarda 129,8 / 89,5 mm.
    sx = -1
    s = ses_karti(sx, SES_Y, SES_ZC)
    S["ses"] = s
    S["kaldir"] += ["USB ses karti", "Kopuk bant (USB ses karti)", "PAM8403 amfi", "Kopuk bant (PAM8403 amfi)"]
    if B_YER:
        S["kaldir"] += ["USB Hub 4 lu", "Kopuk bant (USB Hub 4 lu)"]
    kafa(SES_ADLAR[0], "ses", s["govde"], ses_m)
    kafa(SES_ADLAR[1], "ses_zarf", s["usb"], 0.0, True)
    kafa(SES_ADLAR[2], "ses_zarf", s["dirsek"], 5.0, True)
    kafa(SES_ADLAR[3], "ses_zarf", s["uzatma"], 6.0, True)
    kafa(SES_ADLAR[4], "ses_zarf", s["jak"], 3.0, True)
    kafa("PAM8403", "pam", duvar_kutu(sx, PAM_Y, -19.5, 24.0, 18.0, 5.0), pam_m)
    xk = sx * (X_IC - 7.0)
    S["kablo"]["3,5 mm -> PAM giris"] = ([bg(s["jak_uc"]), bg((sx * (X_IC - 8.0), 50.0, 4.0)), bg((xk, PAM_Y, -8.0))], 1.75, None, "listede robot icin yok; AUX kablosu kesilir, L fis")
    if harf in ("A", "C"):
        S["kablo"]["USB uzatma (hub -> ses karti)"] = ([bg(p) for p in [(72.0, 58.0, -28.0), (40.0, 58.0, -14.0), (-60.0, 58.0, -14.0), (-80.0, 58.0, -60.0), s["usb_uc"]]], 2.0, None, "listede yok; USB-A erkek -> disi")
    S["kablo"]["PAM 5 V (VARSAYIM: D24V50F5)"] = ([bg((sx * (X_IC - 12.0), PAM_Y, -32.0)), bg((-100.0, 50.0, -13.0)), bg(D24_5V)], 1.5, None, "besleme noktasi elektrik.md'de dogrulanmadi")
    if B_YER:
        S["kablo"]["Ses karti uzatmasi (Pi -> ses karti)"] = ([bg(PI_USB["p2"]), bg((60.0, 52.0, -25.0)), bg((40.0, 58.0, -14.0)), bg((-60.0, 58.0, -14.0)), bg((-80.0, 58.0, -60.0)), bg(s["usb_uc"])], 2.0, None, "listede yok; USB-A erkek -> disi")
    S["kablo"]["Dizi USB (Pi -> micro B)"] = (dizi_usb_yolu(R["cx"], R["cz"]), 2.0, None, "listede yok (30 cm kablo ekran icin, 2 m'ler gogus + ESP32)")

    if harf == "C":
        h = hoparlor_kafa()
        S["hop"] = h
        S["hop_cerceve"] = "bas"
        kafa("Hoparlor 40 x 20", "hop", h["hoparlor"], hop_m)
        kafa("Hoparlor kabi (baski)", "boss", h["kap"], 12.0)
        for k, b in enumerate(h["boss"]):
            kafa("Hoparlor boss %d" % k, "boss", b, b.Volume / 1000.0 * 1.27 * 0.8)
        a = h["arka"]
        S["kablo"]["Hoparlor (PAM -> kafa ici)"] = ([bg((sx * (X_IC - 7.0), PAM_Y, -28.0)), bg((-90.0, 40.0, -45.0)), bg((-90.0, 15.0, -45.0)), bg((a.x + 2.0, a.y + 10.0, a.z - 8.0))], 2.0, None, "boyuna girmez; listede robot icin yok")
    else:
        h = hoparlor_gogus()
        S["hop"] = h
        S["hop_cerceve"] = "g"
        govde("Hoparlor 40 x 20", "hop", h["hoparlor"], hop_m)
        govde("Hoparlor kabi (baski)", "boss", h["kap"], 12.0)
        for k, b in enumerate(h["boss"]):
            govde("Hoparlor boss %d" % k, "boss", b, 0.0)
        ic = [bg((sx * (X_IC - 7.0), PAM_Y, -28.0)), bg((-100.0, 60.0, -13.0)), bg((-50.0, 42.0, -13.0)), bg((-43.5, 38.0, -13.0))]
        S["kablo"]["Hoparlor (PAM -> gogus)"] = (ic + TRUNK[2:] + [INIS] + gogus_hoparlor_ucu(), 2.0, None, "boyundan iner; listede robot icin yok")

    if harf in ("A", "C"):
        S["kablo"]["Gogus dokunmatik USB (koridor)"] = ([bg(PI_USB["p2"])] + KORIDOR + TRUNK[2:] + [INIS, GOGUS_TOUCH_ILK] + GOGUS_TOUCH_UC, 2.0, 2000.0, "v4 satir 58, 2 m")
        S["kablo"]["Hub kablosu"] = (hub_kablosu_mevcut(), 2.0, 130.0, "hub'in sabit kablosu")
    if B_YER:
        # kapak ic yuzu egik: y 1085 z -82,37; y 1125 z -80,78 (lid_z); y 1157 z -79,51. Hub yatay, y 1157 ucunda 1 mm bosluk, y 1085 ucunda 3,9 mm (takoz)
        lz = lid_z if lid_z is not None else -80.8
        hb = box(35.0, 60.0, HUB_LID_Y[0], HUB_LID_Y[1], lz + 2.3, lz + 21.3)
        govde("USB Hub 4 lu (kapak ici)", "hub", hb, hub_m)
        govde("Hub USB fis payi", "zarf", box(35.0, 60.0, HUB_LID_Y[0], HUB_LID_Y[1], lz + 21.3, lz + 61.3), 0.0, True)
        S["hub_g"] = hb
        ym = (HUB_LID_Y[0] + HUB_LID_Y[1]) / 2.0
        S["kablo"]["Hub uzatmasi (Pi -> hub)"] = ([bg(PI_USB["p3"])] + KORIDOR + TRUNK[2:] + [INIS, (30.0, 1190.0, -40.0), (47.5, HUB_LID_Y[1] + 4.0, lz + 10.0)], 2.0, None, "hub'in 130 mm kablosu + USB uzatma; listede yok")
        S["kablo"]["Gogus dokunmatik USB (hub'dan)"] = ([(47.5, ym, lz + 60.0), (24.0, 1190.0, -30.0), GOGUS_TOUCH_ILK] + GOGUS_TOUCH_UC, 2.0, 2000.0, "v4 satir 58, 2 m (kisalir)")
    return S
