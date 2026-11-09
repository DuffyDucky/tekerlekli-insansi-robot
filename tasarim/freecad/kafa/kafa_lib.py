# Kafa modulu - parca kutuphanesi (FreeCAD 1.1, Part)
# Genel elemanlar ../ortak_lib.py'de; MG996R, 25T horn, ISO 7380 ve baski analizi ../dirsek/dirsek_lib.py'den (ayni cizim,
# ayni yontem). Burada kafaya ozgu: 6808-2RS rulman (omuzdaki ile ayni), WaveShare 10,1" QLED (qled_local) ve geri donus icin Waveshare 7" HDMI LCD (C)
# (rc lcd() ile ayni hacim), Raspberry Pi Camera Module 3 (rc camera()), M2 vida, yuvarlatilmis kafa kutusu.
import os, sys, math
import FreeCAD as App
import Part

_HERE = os.path.dirname(os.path.abspath(__file__))
_UST = os.path.dirname(_HERE)
for _p in (_UST, os.path.join(_UST, "dirsek"), os.path.join(_UST, "kabuk")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from dirsek_lib import *   # noqa  (ortak_lib + MG, HORN_MG, mg996r_local, mg_delikler, horn_mg_local, baski_analiz, screw7380)
import arayuz as A

# ------------------------------------------------------------------ 6808-2RS (omuz_parcalar ile ayni cizim: 40 x 52 x 7)
R6808 = dict(d=40.0, D=52.0, B=7.0, ri_out=22.3, ro_in=24.4)


def rulman_6808(p, yon):
    return bearing(R6808["d"], R6808["D"], R6808["B"], p, yon, R6808["ri_out"], R6808["ro_in"])


# ------------------------------------------------------------------ Waveshare 7" HDMI LCD (C): 04 + rc:39, rc:374-386
# Kulaklarla 164,9 x 124,25; PCB 148,9 x 107,02; delik 156,9 x 114,96 (O3,2); aktif alan 154,21 x 85,92; panel 3,5;
# modul ~15 kalin (tahmini). Yerel: panel on yuzu z = 0 (+Z disari), merkez orijinde; aktif alan merkezi y = +2 (rc).
LCD = dict(l=164.9, h=100.0, ear_h=124.25, t=15.0, al=154.21, ah=85.92, aa_dy=2.0, pcb=(148.9, 107.02),
           delik=(156.9, 114.96), delik_d=3.2, panel_t=3.5, arka_t=1.6, kutle_g=230.0)


def lcd_local():
    l, h = LCD["l"], LCD["h"]
    pt, at = LCD["panel_t"], LCD["arka_t"]
    panel = box(-l / 2, l / 2, -h / 2, h / 2, -pt, 0)
    eh = LCD["ear_h"]
    back = box(-LCD["pcb"][0] / 2, LCD["pcb"][0] / 2, -LCD["pcb"][1] / 2, LCD["pcb"][1] / 2, -pt - at, -pt)
    ears = box(-l / 2, l / 2, -eh / 2, -eh / 2 + 9, -pt - at, -pt).fuse(box(-l / 2, l / 2, eh / 2 - 9, eh / 2, -pt - at, -pt))
    hx, hy = LCD["delik"][0] / 2, LCD["delik"][1] / 2
    for x in (-hx, hx):
        for y in (-hy, hy):
            ears = ears.cut(cyl(LCD["delik_d"] / 2, (x, y, -pt - at - 1), (x, y, -pt + 0.01)))
    hdmi = box(l / 2 - 30, l / 2 - 10, -25, 15, -LCD["t"], -pt - at).fuse(box(-40, 30, -30, 20, -9, -pt - at))
    s = panel.fuse(back).fuse(ears).fuse(hdmi)
    return s.removeSplitter()


def lcd_delikler():
    hx, hy = LCD["delik"][0] / 2, LCD["delik"][1] / 2
    return [(x, y) for x in (-hx, hx) for y in (-hy, hy)]


# ------------------------------------------------------------------ WaveShare 10,1" QLED (arayuz.KAFA_EKRAN_QLED; olcu kaynagi orada: uretici 2D PDF + STEP)
# Yerel: cam on yuzu z = 0 (+Z disari), cam merkezi orijinde. Tek kati: cam seridi (0,9) + panel (cam + panel 6,3) + kart (0,3 ara + 1,6) + kart ustu bilesen zarfi + konnektorler.
def qled_local():
    E = A.KAFA_EKRAN_QLED
    cw, ch = E["cam"][0] / 2, E["cam"][1] / 2
    cam = box(-cw, cw, -ch, ch, -E["cam_t"], 0.0)
    ez = [e for e in cam.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    cam = cam.makeFillet(E["cam_r"], ez)
    zp = -E["cam_panel_t"]                       # panel arka yuzu
    panel = box(E["panel_x"][0], E["panel_x"][1], E["panel_y"][0], E["panel_y"][1], zp, -E["cam_t"])
    zk = zp - 1.9                                # kart bilesen yuzu (STEP y -1,9)
    kart = box(E["kart_x"][0], E["kart_x"][1], E["kart_y"][0], E["kart_y"][1], zk, zp)
    # kart ustu bilesenler (STEP): cip / FPC / dugme zarfi 2,1; hoparlor basligi 6,0 (x -13,9...-8,9); konnektorler port tablosundan
    ek = [box(-50.0, 43.0, E["kart_y"][0] + 2.0, E["kart_y"][1] - 2.0, zk - 2.1, zk),
          box(-13.9, -8.9, 3.03 - 42.82, 3.03 - 32.82, zk - 6.0, zk)]
    for ad, q in E["port"].items():
        if ad == "durum":
            continue
        t = q["t_kart"] if ad != "hdmi" else E["kalinlik"] + zk      # HDMI govdesi toplam kalinliga kadar (zarf 15,03)
        ek.append(box(q["x"][0], q["x"][1], q["y"] - q["en"] / 2, q["y"] + q["en"] / 2, zk - t, zk))
    return cam.fuse(panel).fuse(kart).fuse(ek).removeSplitter()


# SY8205 5 V kart: Motorobit sayfasi 43,5 x 20,2 x 5 (tubitak-2209b/malzeme-listesi/rapor.md); kutle sayfada yok, 8 g TAHMIN. P6KE6V8A: DO-15 govde O3,6 x 7,6 (tipik paket, TAHMIN), 1 g TAHMIN.
SY8205 = dict(l=43.5, w=20.2, h=5.0, kutle_g=8.0, model="SY8205 5 V dusurucu kart (kafa ekrani ayri hat)")
TVS = dict(d=3.6, l=7.6, kutle_g=1.0, model="P6KE6V8A TVS (kafa ekrani 5 V)")
# Hub: Robotistan 72 x 25 x 19, 130 mm kablo (rapor.md); kutle sayfada yok, 25 g TAHMIN. USB ses karti + PAM8403: boyut sayfada yok, 45 x 18 x 11 ve 24 x 18 x 5, 8 g + 3 g TAHMIN (parca gelince olculecek).
HUB = dict(l=72.0, w=25.0, h=19.0, kutle_g=25.0, model="USB Hub 4 lu 72 x 25 x 19")
SES = dict(l=A.SES_USB["ses"]["olcu"][0], w=A.SES_USB["ses"]["olcu"][1], h=A.SES_USB["ses"]["olcu"][2], kutle_g=A.SES_USB["ses"]["kutle_g"], model="USB ses karti (PAM8403 girisi; olcu VARSAYIM, fotograftan)")
PAM = dict(l=24.0, w=18.0, h=5.0, kutle_g=3.0, model="PAM8403 2 x 3 W amfi karti (olcu TAHMIN)")


def tvs_local():
    return cyl(TVS["d"] / 2, (-TVS["l"] / 2, TVS["d"] / 2, 0), (TVS["l"] / 2, TVS["d"] / 2, 0))


# ------------------------------------------------------------------ Raspberry Pi Camera Module 3 (04 + rc:390-396)
# PCB 25 x 23,86 x 1,12; delik O2,2, 21 x 12,5; lens merkezi alt kenardan 14,4; blok 10,8; toplam 11,3.
# Delik dizisinin dikey yeri cizimden alinmadi: alt delikler alt kenardan 2,0 (tahmini, CM2 cizimi gibi).
CAM = dict(l=25.0, w=23.86, t=1.12, delik_d=2.2, delik=(21.0, 12.5), delik_alt=2.0, lens_y=14.4, blok=10.8,
           kutle_g=4.0)


def kamera_local():
    """Yerel: PCB on yuzu z = 0, lens +Z; orijin = lens ekseni (PCB on yuzunde). Doner (pcb+lens tek kati)."""
    l, w, t = CAM["l"], CAM["w"], CAM["t"]
    y0 = -CAM["lens_y"]                       # PCB alt kenari
    pcb = box(-l / 2, l / 2, y0, y0 + w, -t, 0)
    for (x, y) in kamera_delikler():
        pcb = pcb.cut(cyl(CAM["delik_d"] / 2, (x, y, -t - 1), (x, y, 1)))
    b = CAM["blok"] / 2
    lens = box(-b, b, -b, b, 0, 6.0).fuse(cyl(3.6, (0, 0, 6.0), (0, 0, 10.2))).fuse(cyl(2.875, (0, 0, 10.2), (0, 0, 10.5)))
    return pcb.fuse(lens).removeSplitter()


def kamera_delikler():
    y0 = -CAM["lens_y"] + CAM["delik_alt"]
    dx = CAM["delik"][0] / 2
    return [(x, y) for x in (-dx, dx) for y in (y0, y0 + CAM["delik"][1])]


def screw_m2(L, p, direction):
    """M2 kendinden kilavuzlu (PT tipi) vida, silindir basli yaklasik: bas O3,8 x 1,6 (tahmini)."""
    u = unit(direction)
    p = V(*p)
    head = Part.makeCylinder(1.9, 1.6, p - u * 1.6, u)
    return head.fuse(Part.makeCylinder(1.0, L, p, u)).removeSplitter()


# ------------------------------------------------------------------ K4 (15 Ekim 2026): Raspberry Pi 5 kafada
# Pi 5 + Active Cooler: bilesen kutulari planlama/adim1/pi_kafada_dogrula.py GOVDE listesinden (resmi STEP'ten alinmis; kart
# koordinati: x 0...85 uzun kenar, y 0...56, y = 0 kenarinda USB-C + 2x micro HDMI + 2x CSI, z kart ust yuzu = 1,6).
# Delikler O2,7, kenardan 3,5, 58 x 49 (donanim/datasheet/raspberry-pi-5-mechanical-drawing.pdf). microSD yuvasi altta x -2,5...12.
PI5 = dict(l=85.0, w=56.0, t=1.6, delik_d=2.7, delik=[(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)], kutle_g=46.0 + 12.0,
           kaynak="taban_lib PI (46 g kart + 12 g Active Cooler); olculer resmi mekanik cizim + STEP")
PI5_BILESEN = [("USB-C + micro HDMI", 6.5, 46.0, -1.7, 6.2, 1.6, 4.6), ("CSI x2", 47.0, 57.0, 0.0, 17.0, 1.6, 5.3),
               ("USB / Ethernet", 66.4, 88.1, 2.3, 54.2, -0.7, 17.5), ("GPIO", 7.0, 58.0, 50.0, 55.5, 1.6, 11.0),
               ("Active Cooler", 6.0, 69.5, 6.5, 49.0, 1.6, 15.0), ("microSD yuvasi", -2.5, 12.0, 22.0, 34.0, -1.4, 0.0)]
# kart koordinati -> kafa: kafa_x = x + T.x, kafa_y = z + T.y, kafa_z = -y + T.z (bilesen yuzu yukari, kablo kenari +Z = one)
PI5_R = ((1, 0, 0), (0, 0, 1), (0, -1, 0))


def pi5_kafa(T):
    """Pi 5 + Active Cooler tek kati, kafa koordinatinda; T = kart alt yuzu kosesi (kart x 0, y 0) konumu."""
    def kutu(x0, x1, y0, y1, z0, z1):
        b = box(x0, x1, y0, y1, z0, z1)
        m = App.Matrix(1, 0, 0, T[0], 0, 0, 1, T[1], 0, -1, 0, T[2], 0, 0, 0, 1)
        b.transformShape(m)
        return b
    pcb = kutu(0, PI5["l"], 0, PI5["w"], 0, PI5["t"])
    for (x, y) in PI5["delik"]:
        pcb = pcb.cut(cyl(PI5["delik_d"] / 2, (x + T[0], T[1] - 1, -y + T[2]), (x + T[0], T[1] + PI5["t"] + 1, -y + T[2])))
    return pcb.fuse([kutu(*b[1:]) for b in PI5_BILESEN]).removeSplitter()


def pi5_delikler_kafa(T):
    return [(x + T[0], -y + T[2]) for (x, y) in PI5["delik"]]


# M2,5 elemanlari (taban_lib ile ayni nominal): DIN 912 M2,5 dk 4,5 k 2,5 s 2; gecme deligi O2,9; pirinc burc AA 5 x 8 disi-disi
def screw912_25(L, p, direction):
    u = unit(direction)
    p = V(*p)
    head = Part.makeCylinder(2.25, 2.5, p - u * 2.5, u).cut(hexprism(2.0, p - u * 2.6, p - u * 1.0))
    return head.fuse(Part.makeCylinder(1.25, L, p, u)).removeSplitter()


def burc25(L, p0, direction):
    u = unit(direction)
    p0 = V(*p0)
    return hexprism(5.0, p0, p0 + u * L, V(1, 0, 0) if abs(u.x) < 0.9 else V(0, 0, 1)).cut(Part.makeCylinder(1.25, L + 2, p0 - u, u))


# 5 V cevirici: Pololu D24V50F5 (Ahmet 01.11.2026; raporlar/kaynaklar/07 Tablo 2, Robotistan PL-2851: 17,8 x 20,3 x 8,8 mm, maks. 38 V, 5 V %4, 5 A surekli,
# ters gerilim / asiri akim / kisa devre / termal korumali). Eski D36V50F5 25,4 x 25,4 x 9,5 idi; kuculdu, tablada yer sorunu yok. Kutle sayfada yok: 7 g eski model degeri (tahmini).
# Bilesen yuksekligi 8,8 icinde tek blok (tahmini dagilim). Yerel: kart alt yuzu y = 0, merkez orijin.
CEV = dict(l=17.8, w=20.3, h=8.8, t=1.0, kutle_g=7.0, model="Pololu D24V50F5 5 V 5 A")


def cevirici_local():
    l, w = CEV["l"], CEV["w"]
    b = box(-l / 2, l / 2, 0, CEV["t"], -w / 2, w / 2)
    return b.fuse(box(-l / 2 + 1.5, l / 2 - 1.5, CEV["t"], CEV["h"], -w / 2 + 1.5, w / 2 - 1.5)).removeSplitter()


# I2S amfi (taban_lib AMP: Adafruit 3006, 19,4 x 17,8, montaj deligi yok -> kopuk bant). YALNIZ 125 cm kafasi (kafa7_parcalar) kullanir;
# 1,58 m kafasinda ses yukseltici PAM8403 + USB ses karti (asagida SES, PAM; kafa10_lib).
AMP = dict(l=19.4, w=17.8, kutle_g=2.0)


def amp_local():
    l, w = AMP["l"], AMP["w"]
    b = box(-l / 2, l / 2, 0, 1.6, -w / 2, w / 2)
    return b.fuse([box(-3, 3, 1.6, 2.6, -3, 3), box(-8, 8, 1.6, 4.1, w / 2 - 4, w / 2 - 1)]).removeSplitter()


# ------------------------------------------------------------------ yuvarlatilmis kutu (kafa kabugu)
def kafa_kutu(x0, x1, y0, y1, z0, z1, r_on, r_kenar):
    """Kutu: Z'ye paralel 4 kenar r_on (ondan bakista koseler), sonra on ve arka yuzun tum kenarlari r_kenar."""
    b = box(x0, x1, y0, y1, z0, z1)
    ez = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    b = b.makeFillet(r_on, ez)
    on_arka = []
    for f in b.Faces:
        bb = f.BoundBox
        if bb.ZLength < 1e-6 and (abs(bb.ZMin - z0) < 1e-6 or abs(bb.ZMin - z1) < 1e-6):
            on_arka += f.Edges
    return b.makeFillet(r_kenar, on_arka)


def yuv_dikdortgen_y(x0, x1, z0, z1, r, y0, y1):
    """Y boyunca prizma, XZ'de yuvarlatilmis dikdortgen."""
    b = box(x0, x1, y0, y1, z0, z1)
    ey = [e for e in b.Edges if abs(e.Vertexes[0].Point.y - e.Vertexes[-1].Point.y) > 1e-6]
    return b.makeFillet(r, ey)


def yuv_dikdortgen_x(y0, y1, z0, z1, r, x0, x1):
    b = box(x0, x1, y0, y1, z0, z1)
    ex = [e for e in b.Edges if abs(e.Vertexes[0].Point.x - e.Vertexes[-1].Point.x) > 1e-6]
    return b.makeFillet(r, ex)


def yuv_dikdortgen_z(x0, x1, y0, y1, r, z0, z1):
    b = box(x0, x1, y0, y1, z0, z1)
    ez = [e for e in b.Edges if abs(e.Vertexes[0].Point.z - e.Vertexes[-1].Point.z) > 1e-6]
    return b.makeFillet(r, ez)


# ------------------------------------------------------------------ baski analizi (dirsek_lib.baski_analiz ile ayni yontem)
# Fark: onceki katmanin 1 mm ofseti yuz basina alinir; ofseti kurulamayan yuz (ince serit) ofsetsiz kullanilir (daha
# tutucu) ve sorun bolgesinin merkezi (baski cercevesinde) kaydedilir. Kabuk yuzlerinde makeOffset2D bazen bos donuyordu.
def baski_analiz(ad, sh, yukari, doluluk):
    import numpy as np
    import MeshPart
    Y = A.YAZICI
    UX, UY, UZ = Y["kullanilabilir"]
    rot = App.Rotation(V(*yukari), V(0, 0, 1))
    s = sh.copy()
    s.transformShape(App.Placement(V(0, 0, 0), rot).toMatrix(), True)
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.1, AngularDeflection=0.3)
    pts, tris = mesh.Topology
    X = np.array([[p.x, p.y, p.z] for p in pts])
    Tn = np.array(tris)
    zmin, zmax = X[:, 2].min(), X[:, 2].max()
    en = None
    for th in range(0, 91, 1):
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        x = X[:, 0] * c - X[:, 1] * s_
        y = X[:, 0] * s_ + X[:, 1] * c
        w, h = x.max() - x.min(), y.max() - y.min()
        w, h = max(w, h), min(w, h)
        if en is None or w < en[1]:
            en = (th, w, h)
    sigar = en[1] <= UX and en[2] <= UY and (zmax - zmin) <= UZ
    sigar_cift = en[1] <= Y["kullanilabilir_cift"][1] and en[2] <= Y["kullanilabilir_cift"][0] and (zmax - zmin) <= Y["kullanilabilir_cift"][2]
    a, b, c3 = X[Tn[:, 0]], X[Tn[:, 1]], X[Tn[:, 2]]
    cr = np.cross(b - a, c3 - a)
    alan = 0.5 * np.linalg.norm(cr, axis=1)
    nz = cr[:, 2] / np.maximum(2 * alan, 1e-12)
    zc = (a[:, 2] + b[:, 2] + c3[:, 2]) / 3
    tabla = zc < zmin + 0.05
    cik = (nz < -math.cos(math.radians(45))) & ~tabla
    oran = float(alan[cik].sum() / alan.sum())
    sorun, uyari, atla = [], 0, []
    kaydir = []          # F6a (P6.1; F1b P1.5 kalibi): acik tel / gecersiz yuz yuzunden kaydirilarak kesilen katmanlar (z, dz)
    onceki = None
    n_kat = int((zmax - zmin) // 1.0)
    inv = App.Placement(V(0, 0, 0), rot).inverse()
    for kk in range(n_kat):
        z = zmin + 0.47 + kk * 1.0      # 0,5 yerine 0,47: 2,5 mm duvarin ic yuzu kesit duzlemiyle cakismasin
        # F6a (P6.1; F1b P1.5 kabuk_montaj.baski_analiz kalibi, F1b-kontrol 14): kesit duzlemi yatay eksenli bir silindire / fillete teget
        # gelince OCC acik tel ya da gecersiz yuz veriyor; eskiden makeFace hatasi katmani sessizce atliyordu. Simdi teller kapali degilse
        # (ya da yuz gecersizse) duzlem 0,05 / 0,1 / 0,25 mm kaydirilip yeniden kesilir, yuz katman duzlemine geri tasinir. Hic kapanmazsa
        # destek sorunu sayilir; yalniz gecersiz kalirsa eskisi gibi atlanir (atlanan_katman).
        yuz, gecersiz = None, False
        for _dz in (0.0, 0.05, -0.05, 0.1, -0.1, 0.25, -0.25):
            try:
                ws = s.slice(V(0, 0, 1), z + _dz)
            except Exception:
                ws = None
            if not ws:
                break
            if all(w.isClosed() for w in ws):
                try:
                    yuz = Part.makeFace(ws, "Part::FaceMakerBullseye")
                except Exception:
                    yuz = None
                if yuz is not None and not yuz.isValid():
                    yuz, gecersiz = None, True    # gecersiz kesit yuzu (teget fillet katmani): kaydirilarak yeniden denenir
                    continue
                if yuz is not None and _dz != 0.0:
                    yuz.translate(V(0, 0, -_dz))
                    kaydir.append((round(z - zmin, 1), _dz))
                break
        else:
            if gecersiz:
                atla.append(round(z - zmin, 1))
            else:
                sorun.append(dict(z=round(z - zmin, 1), hata="kesit teli kapanmadi (z +-0,25 mm)"))
        if yuz is not None and onceki is not None:
            dl = []
            for f in onceki.Faces:
                try:
                    o = f.makeOffset2D(1.0, 0)
                    dl.append(o if o.Area > f.Area else f)
                except Exception:
                    dl.append(f)
                    uyari += 1
            try:
                dest = dl[0].fuse(dl[1:]) if len(dl) > 1 else dl[0]
                dest.translate(V(0, 0, 1.0))
                acik = yuz.cut(dest)
            except Exception as e:
                acik = None
                sorun.append(dict(z=round(z - zmin, 1), hata=repr(e)[:80]))
            if acik is not None:
                for f in acik.Faces:
                    if f.Area < 0.5:
                        continue
                    try:
                        dar = f.makeOffset2D(-1.0, 0)
                        dar_alan = sum(g.Area for g in dar.Faces)
                    except Exception:
                        dar_alan = 0.0
                    boy = max(f.BoundBox.XLength, f.BoundBox.YLength)
                    if dar_alan > 0.01 and boy > BRIDGE:
                        m = inv.multVec(f.BoundBox.Center)
                        sorun.append(dict(z=round(z - zmin, 1), alan=round(f.Area, 1), boy=round(boy, 1),
                                          robot=[round(m.x, 1), round(m.y, 1), round(m.z, 1)]))
        onceki = yuz
    hac = sh.Volume
    kutle = hac / 1000 * A.PETG_RHO * doluluk
    return dict(ad=ad, olcu=[round(en[1], 1), round(en[2], 1), round(zmax - zmin, 1)], tabla_aci=en[0], sigar=bool(sigar),
                sigar_cift=bool(sigar_cift), cikinti_orani=round(oran, 4), cikinti_alan_cm2=round(float(alan[cik].sum()) / 100, 2),
                yuzey_cm2=round(float(alan.sum()) / 100, 1), destek_sorun=sorun[:20], destek_sorun_sayi=len(sorun),
                desteksiz=len(sorun) == 0, ofset_uyari=uyari, atlanan_katman=atla, kesit_kaydirma=kaydir, hacim_cm3=round(hac / 1000, 1), kutle_g=round(kutle, 1),
                filament_g=round(kutle * 1.05, 1), sure_saat=round(hac * doluluk / A.PETG_HACIM_HIZI / 3600, 2), katman=n_kat)
