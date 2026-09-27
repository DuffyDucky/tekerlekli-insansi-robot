# -*- coding: utf-8 -*-
"""
Tekerlekli insansi robot - parametrik CAD modeli (CadQuery 2.8)

Koordinat sistemi SolidWorks ile ayni: Y yukari, Z ileri (robotun yuzu +Z), X sag-sol. Birim: mm.
Ciktilar:
  Humanoid-Robot-Montaj.step  -> SolidWorks / Fusion / FreeCAD / eDrawings ile acilir
  parca-listesi.csv           -> gercek parca listesi (olcu, adet, kutle)
  model.json                  -> tarayici demosu icin parca aglari + yerlesim kurallari
Calistirma:  python robot_cad.py <cikti_klasoru> [model_json_yolu]
"""
import sys, os, json, math, base64, csv
import numpy as np
import cadquery as cq
from cadquery import Vector as V

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
MODEL_JSON = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUT, "model.json")
os.makedirs(OUT, exist_ok=True)

# =====================================================================
# 1) GERCEK PARCA OLCULERI (mm) ve KUTLELERI (kg)  -- kaynaklar: parca-listesi.csv
# =====================================================================
D = dict(
    # JGB37-520 12V enkoderli, 60 rpm (~1:90): reduktor O37x24, motor O33x22, mil O6 D x15, 7 mm kacik, 6xM3 O31 [satici]
    gb_d=37.0, gb_l=24.0, mot_d=33.0, mot_l=22.0, enc_d=34.0, enc_l=18.0,
    sh_d=6.0, sh_l=15.0, sh_off=7.0, gb_pcd=31.0, m_motor=0.20,
    # 125 x 58 arazi tekerlegi (Robotistan), 12 mm altigen gobek, 140 g; kaplin 12 altigen x 30, 35 g
    wh_d=125.0, wh_w=58.0, m_wheel=0.14, cp_hex=12.0, cp_l=30.0, m_cp=0.035,
    # DS3218MG: 40 x 20 x 40.4, kulaklarla 54.5, delik 49.5 x 10, kulak alti tabandan 27.7 [datasheet]
    ds_l=40.0, ds_w=20.0, ds_h=40.4, ds_tab=54.5, ds_tab_top=40.4 - 27.7 - 2.5, ds_tab_t=2.5, ds_sh=10.0, m_ds=0.060,
    # MG996R: 40.7 x 19.7, kasa ustu 36.6, kulaklarla 53.6, kulak alti 26.6 [Tower Pro datasheet]
    mg_l=40.7, mg_w=19.7, mg_h=36.6, mg_tab=53.6, mg_tab_top=36.6 - 26.6 - 2.5, mg_tab_t=2.5, mg_sh=10.2, m_mg=0.055,
    # Raspberry Pi 5: 85 x 56, delik O2.7 58 x 49; Active Cooler 63.5 x 42.5 x 13.7 [RPi mekanik cizim]
    pi_l=85.0, pi_w=56.0, m_pi=0.046 + 0.012,
    # Camera Module 3: 25 x 23.86 x 1.12, lens blogu 10.8, toplam 11.3 [RPi cizim]
    cam_l=25.0, cam_w=23.86, m_cam=0.004,
    # Waveshare 7" HDMI LCD: kulaklarla 164.9 x 124.25, PCB 148.9 x 107.02, aktif 154.21 x 85.92, ~15 kalin [Waveshare]
    lcd_l=164.9, lcd_h=100.0, lcd_ear_h=124.25, lcd_t=15.0, lcd_al=154.21, lcd_ah=85.92, m_lcd=0.23,
    # ESP32 DOIT 30 pin ~52 x 28
    esp_l=52.0, esp_w=28.0, m_esp=0.010,
    # BTS7960: 50 x 50 x 43
    bts_l=50.0, bts_w=50.0, bts_h=43.0, m_bts=0.066,
    # PCA9685 (Adafruit): 62.2 x 25.4
    pca_l=62.2, pca_w=25.4, m_pca=0.009,
    # LiFePO4 12.8V 20Ah (Landport LFP12-20): 181 x 77 x 167, 2.8 kg
    bat_l=181.0, bat_w=77.0, bat_h=167.0, m_bat=2.8,
    # 40x40 agir sigma, kanal 10.2, merkez O9, kose delik O5.1 @30.2, 1.99 kg/m [Robolink cizim, sigmaprofil.com.tr]
    sg=40.0, sg_slot=10.2, sg_lip=4.3, sg_cav_w=20.0, sg_cav_d=7.5, sg_bore=9.0, sg_kgm=1.99,
    # Emas B200E60: mantar O60, panel onu 28, arkasi 48, arka govde 42 x 30, delik O22.4
    es_cap=60.0, es_front=28.0, es_back=48.0, m_es=0.085,
    # HC-SR04: 45 x 20 x 15, transduser O16
    us_l=45.0, us_w=20.0, us_td=16.0, us_th=12.0, m_us=0.009,
    # XL4016 tek sogutuculu: 65 x 47 x 23.5
    xl_l=65.0, xl_w=47.0, xl_h=23.5, m_xl=0.060,
    # BNO055 (Adafruit): 27 x 20
    bno_l=27.0, bno_w=20.0, m_bno=0.003,
    # MAX98357A (Adafruit) 19.4 x 17.8; hoparlor O40 x 20, 27 g
    amp_l=19.4, amp_w=17.8, m_amp=0.002, spk_d=40.0, spk_h=20.0, m_spk=0.027,
    # Emes 50 mm tablali PVC sarhos teker: H74, tabla 50 x 50, delik 38 x 38
    cs_h=74.0, cs_plate=50.0, m_cs=0.075,
)
RHO = dict(al=2.70, petg=1.27, steel=7.85, ply=0.68)

# =====================================================================
# 2) ROBOT YERLESIM PARAMETRELERI (varsayilan = "Onerilen")
# =====================================================================
W0 = 340.0          # sase disten genislik (X)
L0 = 500.0          # sase disten derinlik (Z)
H0 = 1150.0         # toplam boy
ARM0 = 306.0        # omuz ekseni -> el ucu
AX = D['wh_d'] / 2  # aks yuksekligi
BR_UP = 29.0        # braket flansi ust yuzu, mil ekseninin ustunde
PL_T = 3.0
Y_PL = AX + BR_UP                 # alt plaka alt yuzu (91.5)
Y_RAIL0 = Y_PL + PL_T             # ray alti (94.5)
Y_RAIL1 = Y_RAIL0 + 40            # ray ustu (134.5)
Y_DECK0 = Y_RAIL1 + 40            # ust kat alti (174.5)
Y_DECK1 = Y_DECK0 + 5.0           # ust kat ustu (179.5)
Y_COV0, COV_H = 90.0, 172.0       # taban kapagi
Y_COV1 = Y_COV0 + COV_H           # 262
HEAD_UP = 275.0                   # traversin ust yuzunden kafa tepesine
S0 = H0 - 20 - HEAD_UP            # omuz ekseni yuksekligi (855)
X_SH = 150.0                      # omuz ekseni (horn yuzu) X konumu
X_BR = W0 / 2 - 2                 # motor braketi dikey plakasi ic yuzu (168)
X_WH = X_BR + 2 + 14 + D['wh_w'] / 2   # teker merkezi (213)
Z_WH = L0 / 2 - 65                # 4 motorlu yerlesimde teker Z (185)
Z_BAT = -121.5

# =====================================================================
# 3) YARDIMCILAR
# =====================================================================
def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))

def cyl(r, p, d, h):
    return cq.Solid.makeCylinder(r, h, V(*p), V(*d))

def rbox(w, h, d, r, c=(0, 0, 0), sel="|Y", r2=0, sel2=None):
    wp = cq.Workplane("XY").box(w, h, d)
    if r > 0:
        wp = wp.edges(sel).fillet(r)
    if r2 > 0 and sel2:
        wp = wp.edges(sel2).fillet(r2)
    return wp.findSolid().translate(V(*c))

def Rx(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def Ry(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def Rz(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

I3 = np.eye(3)
# servo yerel: mil = +Y, govde uzunlugu = +Z. Asagidaki matrisler mil ve govde yonunu cevirir.
R_SHAFT_X_BODY_DOWN = np.array([[0, 1, 0], [0, 0, -1], [-1, 0, 0]])   # mil +X, govde -Y
R_SHAFT_Z_BODY_DOWN = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])    # mil +Z, govde -Y  (Rx(90))

def mat4(R, t):
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = t
    return M

def xform(shape, M):
    from OCP.gp import gp_Trsf
    R = np.array(M[:3, :3], float)
    R[np.abs(R) < 1e-9] = 0.0
    R[np.abs(np.abs(R) - 1) < 1e-9] = np.sign(R[np.abs(np.abs(R) - 1) < 1e-9])
    t = gp_Trsf()
    t.SetValues(*[float(v) for row in np.hstack([R, M[:3, 3:4]]) for v in row])
    return cq.Shape.cast(cq.occ_impl.shapes.BRepBuilderAPI_Transform(shape.wrapped, t, True).Shape())

# =====================================================================
# 4) PARCA MODELLERI (yerel koordinatlar)
# =====================================================================
PARTS = {}

def part(key, name, bodies, mass=None, rho=None, model="", dims="", qty_note=""):
    PARTS[key] = dict(key=key, name=name, bodies=bodies, mass=mass, rho=rho, model=model, dims=dims)

# ---- 40x40 sigma profil
def sigma(L, axis="z", centered=True):
    s = rbox(D['sg'], D['sg'], L, 1.5, c=(0, 0, L / 2), sel="|Z")
    for ang in (0, 90, 180, 270):
        slot = box(-D['sg_slot'] / 2, D['sg_slot'] / 2, 20 - D['sg_lip'], 21, -1, L + 1)
        cav = box(-D['sg_cav_w'] / 2, D['sg_cav_w'] / 2, 20 - D['sg_lip'] - D['sg_cav_d'], 20 - D['sg_lip'] + 0.01, -1, L + 1)
        s = s.cut(slot.fuse(cav).rotate(V(0, 0, 0), V(0, 0, 1), ang))
    s = s.cut(cyl(D['sg_bore'] / 2, (0, 0, -1), (0, 0, 1), L + 2))
    for (cx, cy) in ((15.1, 15.1), (-15.1, 15.1), (15.1, -15.1), (-15.1, -15.1)):
        s = s.cut(cyl(2.55, (cx, cy, -1), (0, 0, 1), L + 2))
    if centered:
        s = s.translate(V(0, 0, -L / 2))
    if axis == "x":
        s = s.rotate(V(0, 0, 0), V(0, 1, 0), 90)
    elif axis == "y":
        s = s.rotate(V(0, 0, 0), V(1, 0, 0), -90)
    return s

def add_sigma(key, name, L, axis, centered):
    part(key, name, [(sigma(L, axis, centered), 'alu')], mass=D['sg_kgm'] * L / 1000,
         model="40x40 agir sigma profil, kanal 10", dims=f"40 x 40 x {L:.0f}")

# ---- JGB37-520 motor: mil +X, mil kok = orijin, govde ekseni y=+sh_off
def jgb37():
    e = D['sh_off']
    gb = cyl(D['gb_d'] / 2, (-D['gb_l'], e, 0), (1, 0, 0), D['gb_l'])
    for i in range(6):
        a = math.radians(30 + 60 * i)
        gb = gb.cut(cyl(1.5, (-4, e + D['gb_pcd'] / 2 * math.sin(a), D['gb_pcd'] / 2 * math.cos(a)), (1, 0, 0), 5))
    boss = cyl(6, (0, 0, 0), (1, 0, 0), 2.0)
    x0 = -D['gb_l'] - D['mot_l']
    can = cyl(D['mot_d'] / 2, (x0, e, 0), (1, 0, 0), D['mot_l'])
    enc = cyl(D['enc_d'] / 2, (x0 - D['enc_l'], e, 0), (1, 0, 0), D['enc_l'])
    conn = box(x0 - D['enc_l'] + 3, x0 - 3, e - 6, e + 6, -D['enc_d'] / 2 - 5, -D['enc_d'] / 2 + 1)
    sh = cyl(D['sh_d'] / 2, (0, 0, 0), (1, 0, 0), D['sh_l']).cut(box(3, D['sh_l'] + 1, 2.5, 4, -4, 4))
    return [(gb, 'steel'), (boss.fuse(sh), 'steel'), (can, 'alu_dark'), (enc, 'black'), (conn, 'white')]

part('jgb37', "JGB37-520 enkoderli motor (60 dev/dk)", jgb37(), mass=D['m_motor'],
     model="JGB37-520 12V, enkoderli", dims=f"O{D['gb_d']:.0f} redüktör, toplam ~{D['gb_l']+D['mot_l']+D['enc_l']:.0f} + {D['sh_l']:.0f} mil")

def jgb_bracket():
    t = 1.5
    v = box(0, t, -21, BR_UP, -21, 21).cut(cyl(6.5, (-1, 0, 0), (1, 0, 0), t + 2))
    for dz in (-12, 12):
        v = v.cut(cyl(1.6, (-1, D['sh_off'] + 12, dz), (1, 0, 0), t + 2))
    f = box(-32, t, BR_UP - t, BR_UP, -21, 21)
    for dx in (-24, -10):
        for dz in (-13, 13):
            f = f.cut(cyl(1.7, (dx, BR_UP - t - 1, dz), (0, 1, 0), t + 2))
    return [(v.fuse(f), 'steel')]

part('jgb_br', "JGB37 L montaj braketi", jgb_bracket(), mass=0.030, model="37 mm motor L braketi (JGB37 delik duzeni kontrol!)", dims="46 x 42 x 40, 1,5 mm")

def coupling():
    pl = cq.Plane(origin=(3.5, 0, 0), xDir=(0, 1, 0), normal=(1, 0, 0))
    hx = cq.Workplane(pl).polygon(6, D['cp_hex'] / math.cos(math.pi / 6)).extrude(D['cp_l']).findSolid()
    return [(hx.cut(cyl(3.05, (0, 0, 0), (1, 0, 0), 40)), 'gold')]

part('coup', "12 mm altıgen kaplin (6 mm mil)", coupling(), mass=D['m_cp'], model="12 mm altıgen pirinç kaplin, O6 delik", dims="12 AA x 30")

def wheel():
    R, w = D['wh_d'] / 2, D['wh_w']
    tire = cq.Workplane("YZ").circle(R).extrude(w).translate((-w / 2, 0, 0)).edges().fillet(9).findSolid()
    tire = tire.cut(cyl(42, (-w, 0, 0), (1, 0, 0), 2 * w))
    for i in range(20):
        g = box(-w / 2 - 1, w / 2 + 1, R - 5, R + 2, -3.5, 3.5)
        if i % 2:
            g = box(-w / 2 - 1, -2, R - 5, R + 2, -3.5, 3.5).fuse(box(2, w / 2 + 1, R - 5, R + 2, -3.5, 3.5))
        tire = tire.cut(g.rotate(V(0, 0, 0), V(1, 0, 0), i * 18 + 9))
    rim = cyl(42, (-25, 0, 0), (1, 0, 0), 50).cut(cyl(36, (-26, 0, 0), (1, 0, 0), 52))
    disk = cyl(38, (-3, 0, 0), (1, 0, 0), 6)
    for i in range(6):
        a = math.radians(60 * i)
        disk = disk.cut(cyl(7, (-5, 24 * math.sin(a), 24 * math.cos(a)), (1, 0, 0), 10))
    hub = cyl(13, (-15, 0, 0), (1, 0, 0), 30).cut(cyl(3.2, (-16, 0, 0), (1, 0, 0), 32))
    return [(tire, 'rubber'), (rim.fuse(disk).fuse(hub), 'rim_blue')]

part('wheel', "125 x 58 mm arazi tekerleği", wheel(), mass=D['m_wheel'], model="Büyük arazi tekerleği 125x58 (mavi jant)", dims="O125 x 58")

def caster():
    pl = box(-25, 25, -2.5, 0, -25, 25)
    fork = box(-14, 14, -44, -2.5, -8, 8).cut(box(-11, 11, -45, -6, -9, 9))
    wh = cyl(25, (-10, -D['cs_h'] + 25, -14), (1, 0, 0), 20)
    spacer = box(-25, 25, 0, Y_PL - D['cs_h'], -25, 25)
    return [(pl.fuse(fork), 'steel'), (wh, 'petg_dark'), (spacer, 'petg')]

part('caster', "50 mm tablalı sarhoş teker + ara blok", caster(), mass=D['m_cs'] + 0.02,
     model="Emes 50 mm PVC tablalı döner teker", dims=f"yükseklik {D['cs_h']:.0f} + {Y_PL - D['cs_h']:.1f} blok")

# ---- servo: mil ekseni +Y, orijin govde ust yuzunde mil merkezi; govde z in [-sh, l-sh]
def servo(l, w, h, tab, tab_top, tab_t, sh, horn=True):
    body = rbox(w, h, l, 1.0, c=(0, -h / 2, l / 2 - sh), sel="|Y")
    ext = (tab - l) / 2
    tabs = box(-w / 2, w / 2, -tab_top - tab_t, -tab_top, -sh - ext, l - sh + ext)
    for z in (l / 2 - sh - 24.75, l / 2 - sh + 24.75):
        for x in (-5, 5):
            tabs = tabs.cut(cyl(2.3, (x, -tab_top - tab_t - 1, z), (0, 1, 0), tab_t + 2))
    dome = cyl(6.5, (0, 0, 0), (0, 1, 0), 2.0).fuse(cyl(4.5, (0, 0, 10), (0, 1, 0), 1.5))
    spline = cyl(2.9, (0, 2, 0), (0, 1, 0), 4.0)
    cable = box(-3, 3, -h + 2, -h + 7, -sh - 3, -sh)
    b = [(body.fuse(tabs), 'black'), (dome, 'black'), (spline, 'gold'), (cable, 'copper')]
    if horn:
        b.append((cyl(12.5, (0, 6, 0), (0, 1, 0), 3.0).cut(cyl(1.6, (7, 5, 7), (0, 1, 0), 5)), 'alu'))
    return b

part('ds3218', "DS3218MG servo (20 kg·cm)", servo(D['ds_l'], D['ds_w'], D['ds_h'], D['ds_tab'], D['ds_tab_top'], D['ds_tab_t'], D['ds_sh']),
     mass=D['m_ds'], model="DS3218MG + alüminyum disk horn", dims=f"{D['ds_l']} x {D['ds_w']} x {D['ds_h']}")
part('mg996r', "MG996R servo (≈10 kg·cm)", servo(D['mg_l'], D['mg_w'], D['mg_h'], D['mg_tab'], D['mg_tab_top'], D['mg_tab_t'], D['mg_sh']),
     mass=D['m_mg'], model="MG996R + disk horn", dims=f"{D['mg_l']} x {D['mg_w']} x {D['mg_h']}")

def servo_holder():
    # servo kizagi: govdeyi alttan ve yanlardan saran 2 mm aluminyum U
    t = 2
    base = box(-12, 12, -42.5, -40.5, -12, 32)
    s1 = box(-12, -10, -42.5, -12, -12, 32)
    s2 = box(10, 12, -42.5, -12, -12, 32)
    return [(base.fuse(s1).fuse(s2), 'alu')]

part('holder', "Servo kızağı (2 mm alüminyum)", servo_holder(), rho=RHO['al'], model="20 kg servo için çok amaçlı braket", dims="24 x 44 x 30")

# ---- elektronik kartlar (alt yuzey y=0)
def board(l, w, t, col, comps=()):
    b = [(box(-l / 2, l / 2, 0, t, -w / 2, w / 2), col)]
    for (x0, x1, z0, z1, h, c) in comps:
        b.append((box(x0, x1, t, t + h, z0, z1), c))
    return b

def pi5():
    l, w = D['pi_l'], D['pi_w']
    pcb = box(-l / 2, l / 2, 0, 1.6, -w / 2, w / 2)
    for (x, z) in ((-l / 2 + 3.5, -w / 2 + 3.5), (-l / 2 + 61.5, -w / 2 + 3.5), (-l / 2 + 3.5, w / 2 - 3.5), (-l / 2 + 61.5, w / 2 - 3.5)):
        pcb = pcb.cut(cyl(1.35, (x, -1, z), (0, 1, 0), 4))
    usb1 = box(l / 2 - 17, l / 2 + 2, 1.6, 17.6, -w / 2 + 2, -w / 2 + 16)
    usb2 = box(l / 2 - 17, l / 2 + 2, 1.6, 17.6, -w / 2 + 20, -w / 2 + 34)
    eth = box(l / 2 - 21, l / 2 + 2, 1.6, 15.1, w / 2 - 18, w / 2 - 2)
    cool = box(-l / 2 + 6, -l / 2 + 6 + 63.5, 1.6, 1.6 + 9.0, -21.25, 21.25)
    fan = cyl(14, (-l / 2 + 38, 10.6, 0), (0, 1, 0), 0.6)
    hdr = box(-l / 2 + 7, -l / 2 + 58, 1.6, 10.1, w / 2 - 6, w / 2 - 1)
    return [(pcb, 'pcb_green'), (usb1.fuse(usb2).fuse(eth), 'steel'), (cool, 'petg_dark'), (fan, 'black'), (hdr, 'black')]

part('pi5', "Raspberry Pi 5 8GB + Active Cooler", pi5(), mass=D['m_pi'], model="Raspberry Pi 5 8GB", dims="85 x 56 x ~18")
part('esp32', "ESP32-WROOM-32D DevKit", board(D['esp_l'], D['esp_w'], 1.6, 'pcb_black',
     [(-D['esp_l'] / 2 + 1, -D['esp_l'] / 2 + 19, -8, 8, 3.2, 'steel'), (-22, 24, -14, -11.5, 8.5, 'black'), (-22, 24, 11.5, 14, 8.5, 'black')]),
     mass=D['m_esp'], model="ESP32 DevKit 30 pin", dims=f"{D['esp_l']} x {D['esp_w']}")
part('pca', "PCA9685 16 kanal servo sürücü", board(D['pca_l'], D['pca_w'], 1.6, 'pcb_blue',
     [(-24, 24, -12, -4, 11, 'black'), (-6, 6, 2, 10, 1.5, 'black'), (26, 31, -8, 8, 9, 'pcb_green')]),
     mass=D['m_pca'], model="PCA9685 (Adafruit tipi)", dims=f"{D['pca_l']} x {D['pca_w']}")
part('bts', "BTS7960 43A motor sürücü", board(D['bts_l'], D['bts_w'], 1.6, 'pcb_red',
     [(-20, 20, -20, 20, 24, 'alu'), (-24, -14, 14, 24, 10, 'pcb_blue'), (18, 24, -18, 18, 9, 'black')]),
     mass=D['m_bts'], model="BTS7960B modülü", dims=f"{D['bts_l']} x {D['bts_w']} x {D['bts_h']}")
part('xl4016', "XL4016 DC-DC düşürücü", board(D['xl_l'], D['xl_w'], 1.6, 'pcb_blue',
     [(-26, -6, -20, 20, 23, 'alu_dark'), (4, 20, 4, 20, 14, 'black'), (22, 28, -22, 22, 10, 'pcb_green')]),
     mass=D['m_xl'], model="XL4016 8A modül", dims=f"{D['xl_l']} x {D['xl_w']} x {D['xl_h']}")
part('bno', "BNO055 IMU kartı", board(D['bno_l'], D['bno_w'], 1.6, 'pcb_blue', [(-4, 4, -4, 4, 1.2, 'black')]),
     mass=D['m_bno'], model="BNO055", dims=f"{D['bno_l']} x {D['bno_w']}")
part('amp', "MAX98357A I2S amfi", board(D['amp_l'], D['amp_w'], 1.6, 'pcb_blue', [(-3, 3, -3, 3, 1, 'black')]),
     mass=D['m_amp'], model="MAX98357A", dims=f"{D['amp_l']} x {D['amp_w']}")

def battery():
    l, w, h = D['bat_l'], D['bat_w'], D['bat_h']
    b = rbox(l, w, h, 4, c=(0, w / 2, 0), sel="|Y")
    t1 = cyl(5, (-l / 2 + 25, w / 2, h / 2), (0, 0, 1), 9)
    t2 = cyl(5, (l / 2 - 25, w / 2, h / 2), (0, 0, 1), 9)
    lab = box(-l / 2 + 20, l / 2 - 20, w - 0.2, w + 0.4, -h / 2 + 25, h / 2 - 25)
    return [(b, 'batt'), (t1, 'red'), (t2, 'black'), (lab, 'white')]

part('battery', "LiFePO4 12,8 V 20 Ah akü (yatık)", battery(), mass=D['m_bat'], model="LiFePO4 12.8V 20Ah, BMS'li", dims=f"{D['bat_l']:.0f} x {D['bat_h']:.0f} x {D['bat_w']:.0f}")

def sonar():
    pcb = box(-D['us_l'] / 2, D['us_l'] / 2, -D['us_w'] / 2, D['us_w'] / 2, -1.6, 0)
    t1 = cyl(D['us_td'] / 2, (-13, 0, 0), (0, 0, 1), D['us_th'])
    t2 = cyl(D['us_td'] / 2, (13, 0, 0), (0, 0, 1), D['us_th'])
    return [(pcb, 'pcb_blue'), (t1.fuse(t2), 'steel')]

part('sonar', "HC-SR04 ultrasonik sensör", sonar(), mass=D['m_us'], model="HC-SR04", dims="45 x 20 x 15")

def estop():
    cap = cyl(D['es_cap'] / 2, (0, D['es_front'] - 12, 0), (0, 1, 0), 12)
    cap = cap.fuse(cyl(14, (0, 6, 0), (0, 1, 0), D['es_front'] - 12 - 6 + 0.5))
    ring = cyl(16, (0, 0, 0), (0, 1, 0), 6)
    neck = cyl(11, (0, -12, 0), (0, 1, 0), 12)
    body = box(-21, 21, -D['es_back'], -12, -15, 15)
    return [(cap, 'red'), (ring, 'yellow'), (neck.fuse(body), 'black')]

part('estop', "22 mm mantar acil stop butonu", estop(), mass=D['m_es'], model="Emas B200E60 (O60 mantar, kalıcı)", dims="O60, ön 28, arka 48")

def speaker():
    fr = cyl(D['spk_d'] / 2, (0, 0, -D['spk_h']), (0, 0, 1), 3).fuse(cyl(13, (0, 0, -D['spk_h'] + 3), (0, 0, 1), 12))
    cone = cyl(D['spk_d'] / 2 - 3, (0, 0, -3), (0, 0, 1), 3)
    return [(fr, 'steel'), (cone, 'black')]

part('speaker', "40 mm 3 W hoparlör", speaker(), mass=D['m_spk'], model="40 mm 4 ohm 3 W", dims="O40 x 18")

def lcd():
    l, h, t = D['lcd_l'], D['lcd_h'], D['lcd_t']
    panel = box(-l / 2, l / 2, -h / 2, h / 2, -3.5, 0)
    scr = box(-D['lcd_al'] / 2, D['lcd_al'] / 2, -D['lcd_ah'] / 2 + 2, D['lcd_ah'] / 2 + 2, 0, 0.3)
    eh = D['lcd_ear_h']
    back = box(-148.9 / 2, 148.9 / 2, -107.02 / 2, 107.02 / 2, -5.1, -3.5)
    ears = box(-l / 2, l / 2, -eh / 2, -eh / 2 + 9, -5.1, -3.5).fuse(box(-l / 2, l / 2, eh / 2 - 9, eh / 2, -5.1, -3.5))
    for x in (-156.9 / 2, 156.9 / 2):
        for y in (-114.96 / 2, 114.96 / 2):
            ears = ears.cut(cyl(1.6, (x, y, -6), (0, 0, 1), 3))
    hdmi = box(l / 2 - 30, l / 2 - 10, -25, 15, -t, -5.1).fuse(box(-40, 30, -30, 20, -9, -5.1))
    back = back.fuse(ears)
    return [(panel, 'black'), (scr, 'screen'), (back, 'pcb_green'), (hdmi, 'steel')]

part('lcd', "7\" HDMI LCD 1024x600", lcd(), mass=D['m_lcd'], model="Waveshare 7inch HDMI LCD (C) muadili", dims=f"{D['lcd_l']} x {D['lcd_ear_h']} x ~{D['lcd_t']:.0f}")

def camera():
    pcb = box(-D['cam_l'] / 2, D['cam_l'] / 2, -D['cam_w'] / 2, D['cam_w'] / 2, -1.12, 0)
    ly = -D['cam_w'] / 2 + 14.4
    lens = box(-5.4, 5.4, ly - 5.4, ly + 5.4, 0, 6.0).fuse(cyl(3.6, (0, ly, 6.0), (0, 0, 1), 4.2))
    glass = cyl(2.875, (0, ly, 10.2), (0, 0, 1), 0.3)
    return [(pcb, 'pcb_green'), (lens, 'black'), (glass, 'screen')]

part('camera', "Raspberry Pi Camera Module 3", camera(), mass=D['m_cam'], model="Camera Module 3 (12 MP)", dims="25 x 24 x 11,5")

# ---- ozel imalat parcalari
def plate(w, d, t, holes=(), cutouts=()):
    p = rbox(w, t, d, 10, c=(0, t / 2, 0), sel="|Y")
    for (x, z, r) in holes:
        p = p.cut(cyl(r, (x, -1, z), (0, 1, 0), t + 2))
    for (x0, x1, z0, z1) in cutouts:
        p = p.cut(box(x0, x1, -1, t + 1, z0, z1))
    return p

holes_bot = [(x, z, 20) for x in (-70, 70) for z in (60, 140)]
part('plate_bot', "Alt plaka, 3 mm alüminyum (lazer kesim)", [(plate(W0, L0, PL_T, holes_bot), 'alu_dark')], rho=RHO['al'],
     model="3 mm Al 5754, lazer kesim", dims=f"{W0:.0f} x {L0:.0f} x 3")
deck_cut = [(-22, 22, -22, 22), (-60, 60, 150, 175), (-60, 60, -225, -200)]
DECK_T = 5.0
part('plate_deck', "Elektronik katı, 5 mm kontrplak (lazer kesim)", [(plate(W0, L0, DECK_T, [(x, z, 14) for x in (-110, 110) for z in (60, 150)], deck_cut), 'ply')],
     rho=RHO['ply'], model="5 mm huş kontrplak, lazer kesim", dims=f"{W0:.0f} x {L0:.0f} x 5")

def standoff():
    pl = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
    return [(cq.Workplane(pl).polygon(6, 9.2).extrude(40).findSolid(), 'gold')]

part('standoff', "M5 x 40 mesafe burcu", standoff(), mass=0.012, model="M5 x 40 pirinç burç", dims="M5 x 40")

def corner_br():
    a = box(0, 37, 0, 4, -18.85, 18.85).fuse(box(0, 4, 0, 37, -18.85, 18.85))
    gus = cq.Workplane("XY").polyline([(4, 4), (33, 4), (4, 33)]).close().extrude(4).translate((0, 0, -2)).findSolid()
    a = a.fuse(gus)
    a = a.cut(cyl(3.3, (22, -1, -9), (0, 1, 0), 6)).cut(cyl(3.3, (22, -1, 9), (0, 1, 0), 6))
    a = a.cut(cyl(3.3, (-1, 22, -9), (1, 0, 0), 6)).cut(cyl(3.3, (-1, 22, 9), (1, 0, 0), 6))
    return [(a, 'alu')]

part('corner', "40x40 geniş köşe bağlantı", corner_br(), mass=0.075, model="40x40 geniş köşe bağlantı + T somun", dims="37 x 37 x 37,7")

def base_cover():
    w, h, d, t = W0 + 20, COV_H, L0 + 20, 2.5
    o = rbox(w, h, d, 45, c=(0, h / 2, 0), sel="|Y", r2=10, sel2=">Y")
    i = rbox(w - 2 * t, h, d - 2 * t, 45 - t, c=(0, h / 2 - t, 0), sel="|Y", r2=10 - t, sel2=">Y")
    c = o.cut(i)
    c = c.cut(box(-24, 24, h - 5, h + 5, -24, 24))                     # direk
    c = c.cut(cyl(11.5, (W0 / 2 - 70 - 0, h - 5, -(L0 / 2 - 50)), (0, 1, 0), 10))  # acil stop
    for x in (-100, 0, 100):                                            # sonar
        for dx in (-13, 13):
            c = c.cut(cyl(8.5, (x + dx, 100, d / 2 - 5), (0, 0, 1), 10))
    return [(c, 'petg')]

part('cover', "Taban kapağı, PETG 3D baskı (4 parça)", base_cover(), rho=RHO['petg'], model="PETG, 2,5 mm duvar", dims=f"{W0+20:.0f} x {COV_H:.0f} x {L0+20:.0f}")

def torso_shell(y0, y1):
    h = y1 - y0
    def loft(a0, b0, a1, b1, a2, b2, ext=0):
        pl = cq.Plane(origin=(0, -ext, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
        return (cq.Workplane(pl).ellipse(a0, b0).workplane(offset=h * 0.55 + ext).ellipse(a1, b1)
                .workplane(offset=h * 0.45 + ext).ellipse(a2, b2).loft(combine=True).findSolid())
    o = loft(112, 82, 132, 88, 152, 78)
    i = loft(109.5, 79.5, 129.5, 85.5, 149.5, 75.5, ext=1)
    s = o.cut(i)
    gy = (S0 - 175) - y0 - 14
    for k in range(5):
        s = s.cut(box(-16, 16, gy + k * 7, gy + k * 7 + 3, 55, 100))       # hoparlor izgarasi
    return [(s, 'petg')]

TORSO_Y0 = Y_COV1
TORSO_Y1 = S0 + 30
part('torso', "Gövde kabuğu, PETG 3D baskı (6 parça)", torso_shell(TORSO_Y0, TORSO_Y1), rho=RHO['petg'],
     model="PETG, 2,5 mm duvar", dims=f"285 x {TORSO_Y1-TORSO_Y0:.0f} x 175")

def head_shell():
    w, h, d, t = 210, 180, 150, 2.5
    o = rbox(w, h, d, 28, c=(0, h / 2, 10), sel="|Z", r2=12, sel2="|X")
    i = rbox(w - 2 * t, h - 2 * t, d - 2 * t, 28 - t, c=(0, h / 2, 10), sel="|Z", r2=12 - t, sel2="|X")
    s = o.cut(i)
    s = s.cut(box(-D['lcd_al'] / 2 - 1, D['lcd_al'] / 2 + 1, h / 2 - D['lcd_ah'] / 2 - 4, h / 2 + D['lcd_ah'] / 2 - 4, 60, 100))
    s = s.cut(cyl(4.5, (0, h - 28, 60), (0, 0, 1), 40))
    s = s.cut(cyl(28, (0, -1, 0), (0, 1, 0), 10))
    for sx in (-1, 1):
        for k in range(4):
            s = s.cut(box(sx * 104 - 3, sx * 104 + 3, 60 + k * 9, 64 + k * 9, -20, 30))
    return [(s, 'petg')]

part('head', "Kafa kabuğu, PETG 3D baskı (2 parça)", head_shell(), rho=RHO['petg'], model="PETG, 2,5 mm duvar", dims="210 x 180 x 150")

def neck_plate():
    p = rbox(70, 3, 70, 6, c=(0, 1.5, 10), sel="|Y")
    for x in (-25, 25):
        for z in (-15, 35):
            p = p.cut(cyl(2.7, (x, -1, z), (0, 1, 0), 5))
    return [(p, 'alu')]

part('neckplate', "Boyun plakası, 3 mm alüminyum", neck_plate(), rho=RHO['al'], model="3 mm Al", dims="70 x 70 x 3")

def u_bracket(span=46, depth=24, leg=46, t=2):
    base = box(-span / 2 - t, span / 2 + t, 0, t, -depth / 2, depth / 2)
    l1 = box(-span / 2 - t, -span / 2, 0, leg, -depth / 2, depth / 2)
    l2 = box(span / 2, span / 2 + t, 0, leg, -depth / 2, depth / 2)
    return base.fuse(l1).fuse(l2)

part('ubr_tilt', "Kafa eğme U braketi, 2 mm Al", [(u_bracket(46, 24, 48), 'alu')], rho=RHO['al'], model="Uzun U servo braketi", dims="50 x 48 x 24")

def head_mount():
    return [(rbox(120, 4, 90, 8, c=(0, 2, 10), sel="|Y").fuse(box(-30, 30, -18, 0, -6, 6)), 'petg_dark')]

part('headmount', "Kafa taşıyıcı plaka, PETG", head_mount(), mass=0.040, model="PETG, %40 doluluk", dims="120 x 90 x 4")

# ---- kol parcalari (sag kol, yerel: orijin omuz ekseni horn yuzu, kol -Y yonunde asili)
AX_ARM = 16.0   # kol tupu ekseni X
def tube(od, y0, y1, t=2.5):
    return cyl(od / 2, (AX_ARM, y1, 0), (0, 1, 0), y0 - y1).cut(cyl(od / 2 - t, (AX_ARM, y1 - 1, 0), (0, 1, 0), y0 - y1 + 2))

part('sh_plate', "Omuz bağlantı plakası, 2 mm Al", [(box(3, 5, -62, 14, -15, 15), 'alu')], rho=RHO['al'], model="2 mm Al", dims="76 x 30 x 2")
def shoulder_cap():
    o = cq.Workplane("XY").sphere(38).findSolid().translate(V(AX_ARM, -28, 0))
    i = cq.Workplane("XY").sphere(35.5).findSolid().translate(V(AX_ARM, -28, 0))
    s = o.cut(i).cut(box(-60, 5.5, -80, 20, -60, 60)).cut(cyl(24, (AX_ARM, -80, 0), (0, 1, 0), 20))
    return [(s, 'petg')]
part('sh_cap', "Omuz kapağı, PETG", shoulder_cap(), rho=RHO['petg'], model="PETG", dims="O76")
UP_Y0, UP_Y1 = -60.0, -140.0
FA_Y0, FA_Y1 = -168.0, -243.0
part('tube_up', "Üst kol tüpü, PETG", [(tube(56, UP_Y0, UP_Y1), 'petg')], rho=RHO['petg'], model="PETG", dims="O56 x 80")
part('elbow_cap', "Dirsek kapağı, PETG", [(cyl(28, (AX_ARM - 28, -154, 0), (1, 0, 0), 56).cut(cyl(25.5, (AX_ARM - 27, -154, 0), (1, 0, 0), 54)), 'petg')],
     rho=RHO['petg'], model="PETG", dims="O56 x 56")
part('tube_fa', "Ön kol tüpü, PETG", [(tube(60, FA_Y0, FA_Y1), 'petg')], rho=RHO['petg'], model="PETG", dims="O60 x 75")
def hand():
    palm = rbox(26, 62, 50, 10, c=(AX_ARM, -275, 0), sel="|X")
    thumb = cyl(7, (AX_ARM, -258, 20), (0, -0.5, 0.87), 26)
    return [(palm.fuse(thumb), 'petg_dark')]
part('hand', "El, PETG (sabit, %30 doluluk)", hand(), mass=0.035, model="PETG, %30 doluluk", dims="26 x 62 x 50")
part('link', "Kol bağlantı plakası, 2 mm Al", [(box(AX_ARM - 12, AX_ARM + 12, -66, -58, -16, 16), 'alu')], rho=RHO['al'], model="2 mm Al", dims="24 x 32 x 8")

# =====================================================================
# 5) YERLESIM (varsayilan) + parametre kurallari (demo icin)
# =====================================================================
INST = []   # taban + govde
HEAD = []   # kafa grubu (yerel: traversin ust yuzu, y=0)
ARM = []    # sag kol (yerel: omuz ekseni)

def put(lst, key, pos, R=I3, **kw):
    d = dict(key=key, pos=[float(p) for p in pos], R=np.asarray(R, float).tolist())
    d.update(kw)
    lst.append(d)

# --- sase
for sx in (-1, 1):
    put(INST, 'rail_l', (sx * (W0 / 2 - 20), Y_RAIL0 + 20, 0), grp='base', st=1, xm='s', sz='L', ex=[sx * 30, 0, 0])
for z, zm in ((-(L0 / 2 - 20), 's'), (0, ''), (L0 / 2 - 20, 's')):
    put(INST, 'rail_c', (0, Y_RAIL0 + 20, z), grp='base', st=1, zm=zm, sx='Win', ex=[0, 0, (z / 230) * 30 if z else 0])
add_sigma('rail_l', "Şase uzun rayı", L0, 'z', True)
add_sigma('rail_c', "Şase ara rayı", W0 - 80, 'x', True)
put(INST, 'plate_bot', (0, Y_PL, 0), grp='base', st=1, sx='W', sz='L', ex=[0, -70, 0])
put(INST, 'plate_deck', (0, Y_DECK0, 0), grp='base', st=1, sx='W', sz='L', ex=[0, 160, 0])
for sx in (-1, 1):
    for sz in (-1, 1):
        put(INST, 'standoff', (sx * (W0 / 2 - 20), Y_RAIL1, sz * (L0 / 2 - 20)), grp='base', st=1, xm='s', zm='s', ex=[0, 80, 0])
# --- tahrik (4 motor = m4, 2 motor = m2)
for vis, zs in (('m4', (-Z_WH, Z_WH)), ('m2', (0,))):
    for z in zs:
        for sx in (-1, 1):
            R = I3 if sx > 0 else Ry(180)
            zm = 's' if z else ''
            put(INST, 'jgb37', (sx * X_BR, AX, z), R, grp='base', st=1, xm='s', zm=zm, vis=vis, ex=[sx * 60, 0, 0])
            put(INST, 'jgb_br', (sx * X_BR, AX, z), R, grp='base', st=1, xm='s', zm=zm, vis=vis, ex=[sx * 45, 0, 0])
            put(INST, 'coup', (sx * X_BR, AX, z), R, grp='base', st=1, xm='s', zm=zm, vis=vis, ex=[sx * 90, 0, 0])
            put(INST, 'wheel', (sx * X_WH, AX, z), grp='base', st=1, xm='s', zm=zm, vis=vis, ex=[sx * 130, 0, 0], contact=1)
for sz in (-1, 1):
    put(INST, 'caster', (0, D['cs_h'], sz * (L0 / 2 - 35)), grp='base', st=1, zm='s', vis='m2', ex=[0, -60, 0], contact=2)
# --- aku ve guc
put(INST, 'battery', (0, Y_RAIL0, Z_BAT), grp='base', st=1, ym='B', zm='p', ex=[0, 0, -330])
for x in (-85, 85):
    put(INST, 'bts', (x, Y_RAIL0, 165), grp='base', st=1, xm='p', zm='p', ex=[0, 40, 90])
for (x, z) in ((-62, 75), (62, 75), (0, 170)):
    put(INST, 'xl4016', (x, Y_RAIL0, z), grp='base', st=1, xm='p', zm='p', ex=[0, 40, 90])
# --- elektronik kati
put(INST, 'pi5', (-75, Y_DECK1 + 6, -120), grp='base', st=1, xm='p', zm='p', ex=[0, 230, 0])
put(INST, 'esp32', (65, Y_DECK1 + 6, -135), grp='base', st=1, xm='p', zm='p', ex=[0, 230, 0])
put(INST, 'pca', (65, Y_DECK1 + 6, -65), grp='base', st=1, xm='p', zm='p', ex=[0, 230, 0])
put(INST, 'bno', (0, Y_DECK1 + 6, 60), grp='base', st=1, xm='p', zm='p', ex=[0, 230, 0])
put(INST, 'amp', (-65, Y_DECK1 + 6, 40), grp='base', st=1, xm='p', zm='p', ex=[0, 230, 0])
# --- kapak, sensor, acil stop
put(INST, 'cover', (0, Y_COV0, 0), grp='base', st=1, sx='Wc', sz='Lc', ex=[0, 420, 0], shell=1)
for x in (-100, 0, 100):
    put(INST, 'sonar', (x, Y_COV0 + 100, L0 / 2 + 10 - 2.5 - 3), grp='base', st=1, xm='p', zm='s', ex=[0, 420, 0])
put(INST, 'estop', (W0 / 2 - 70, Y_COV1, -(L0 / 2 - 50)), grp='base', st=1, xm='p', zm='s', ex=[0, 470, 0])
# --- govde
COL_L0 = (S0 - 20) - Y_RAIL1
add_sigma('column', "Gövde direği", COL_L0, 'y', False)
put(INST, 'column', (0, Y_RAIL1, 0), grp='torso', st=2, sy='col', ex=[0, 0, 0])
for k in (0, 2):
    R = Ry(90 * k)
    put(INST, 'corner', tuple((R @ np.array([20, 0, 0])) + np.array([0, Y_RAIL1, 0])), R, grp='torso', st=2, ex=[0, 0, 0])
add_sigma('crossbar', "Omuz traversi", 200, 'x', True)
put(INST, 'crossbar', (0, S0, 0), grp='torso', st=2, ym='S', ex=[0, 90, 0])
for sx in (-1, 1):
    put(INST, 'corner', (sx * 20, S0 - 20, 0), (Rx(180) if sx > 0 else Rz(180)), grp='torso', st=2, ym='S', ex=[0, 90, 0])
put(INST, 'torso', (0, TORSO_Y0, 0), grp='torso', st=2, sy='torso', ex=[0, 0, 300], shell=1)
put(INST, 'speaker', (0, S0 - 175, 76), grp='torso', st=2, ym='S', ex=[0, 0, 360])
for sx in (-1, 1):
    Rs = R_SHAFT_X_BODY_DOWN if sx > 0 else Ry(180) @ R_SHAFT_X_BODY_DOWN
    put(INST, 'ds3218', (sx * (X_SH - 6), S0, 0), Rs, grp='torso', st=4, ym='S', ex=[sx * 150, 90, 0], role='pitch')
    put(INST, 'holder', (sx * (X_SH - 6), S0, 0), Rs, grp='torso', st=4, ym='S', ex=[sx * 150, 90, 0])
# --- kafa grubu (y=0: traversin ust yuzu)
put(HEAD, 'neckplate', (0, 0, 0), ex=[0, 0, 0])
MG_TOP = 3 + D['mg_h']
put(HEAD, 'mg996r', (0, MG_TOP, 0), ex=[0, 40, 0], role='pan')
put(HEAD, 'ubr_tilt', (0, MG_TOP + 9, 0), ex=[0, 80, 0])
put(HEAD, 'mg996r', (D['mg_h'] / 2, MG_TOP + 33, 0), Rz(-90), ex=[0, 100, 0], role='tilt')
put(HEAD, 'headmount', (0, 91, 0), ex=[0, 150, 0])
put(HEAD, 'head', (0, 95, 0), ex=[0, 230, 60], shell=1)
put(HEAD, 'lcd', (0, 95 + 84, 82.5), ex=[0, 230, 170])
put(HEAD, 'camera', (0, 95 + 180 - 28 - 2.5, 81.5), ex=[0, 250, 170])
# --- sag kol (orijin: omuz ekseni horn yuzu; seg: 0 sabit, 1 ust tup, 2 dirsek, 3 on kol, 4 el)
put(ARM, 'sh_plate', (0, 0, 0), seg=0)
put(ARM, 'ds3218', (AX_ARM + 6, -35, 20), R_SHAFT_Z_BODY_DOWN, seg=0, role='roll')
put(ARM, 'sh_cap', (0, 0, 0), seg=0, shell=2)
put(ARM, 'link', (0, 0, 0), seg=0)
put(ARM, 'tube_up', (0, 0, 0), seg=1, shell=2)
put(ARM, 'mg996r', (AX_ARM + 21, -154, 0), R_SHAFT_X_BODY_DOWN, seg=2, role='elbow')
put(ARM, 'elbow_cap', (0, 0, 0), seg=2, shell=2)
put(ARM, 'tube_fa', (0, 0, 0), seg=3, shell=2)
put(ARM, 'mg996r', (AX_ARM, -238, 10.15), Rx(180), seg=4, role='wrist')
put(ARM, 'hand', (0, 0, 0), seg=4)

# =====================================================================
# 6) KUTLE, AGIRLIK MERKEZI, STEP, JSON, CSV
# =====================================================================
def body_union(key):
    shapes = [b[0] for b in PARTS[key]['bodies']]
    return cq.Compound.makeCompound(shapes)

for k, p in PARTS.items():
    comp = body_union(k)
    vol = sum(s.Volume() for s, _ in p['bodies'])
    p['volume'] = vol
    if p['mass'] is None:
        p['mass'] = vol * p['rho'] / 1e6
    # agirlik merkezi: hacim agirlikli
    num = np.zeros(3); den = 0.0
    for s, _ in p['bodies']:
        v = s.Volume(); c = cq.Shape.centerOfMass(s)
        num += v * np.array([c.x, c.y, c.z]); den += v
    p['com'] = (num / den).tolist() if den > 0 else [0, 0, 0]

def world_list():
    """Varsayilan yapilandirmanin (4 motor, kol asagida) dunya donusumleri."""
    out = []
    for d in INST:
        if d.get('vis') == 'm2':
            continue
        out.append((d, mat4(np.array(d['R']), d['pos']), 'Taban' if d['grp'] == 'base' else 'Govde', False))
    Mh = mat4(I3, (0, S0 + 20, 0))
    for d in HEAD:
        out.append((d, Mh @ mat4(np.array(d['R']), d['pos']), 'Kafa', False))
    Ma = mat4(I3, (X_SH, S0, 0))
    for d in ARM:
        M = Ma @ mat4(np.array(d['R']), d['pos'])
        out.append((d, M, 'Sag_Kol', False))
        out.append((d, M, 'Sol_Kol', True))
    return out

WL = world_list()
Mtot = 0.0; mc = np.zeros(3)
for d, M, g, mir in WL:
    p = PARTS[d['key']]
    c = M[:3, :3] @ np.array(p['com']) + M[:3, 3]
    if mir:
        c[0] = -c[0]
    Mtot += p['mass']; mc += p['mass'] * c
EXTRA = 0.6  # vida, somun, kablo, T-somun payi (kg) - tabanda
mc += EXTRA * np.array([0, 120, 0]); Mtot += EXTRA
COM = mc / Mtot
print(f"Toplam kutle: {Mtot:.2f} kg   Agirlik merkezi (mm): x={COM[0]:.1f} y={COM[1]:.1f} z={COM[2]:.1f}")

# --- STEP
def safe(s):
    tr = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return "".join(ch if ch.isalnum() else "_" for ch in s.translate(tr)).strip("_")[:48]

def rgb(ck):
    h = COL[ck][0].lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

COL = {
    'alu': ('#c9cdd3', 0.75, 0.32), 'alu_dark': ('#a3a9b1', 0.7, 0.38), 'steel': ('#b9bdc2', 0.85, 0.28),
    'black': ('#1c1d1f', 0.05, 0.55), 'rubber': ('#161718', 0.0, 0.95), 'rim_blue': ('#2f6fd0', 0.1, 0.45),
    'pcb_green': ('#1f6b3c', 0.05, 0.6), 'pcb_red': ('#b3262a', 0.05, 0.55), 'pcb_blue': ('#1f4fa8', 0.05, 0.55),
    'pcb_black': ('#222428', 0.05, 0.6), 'petg': ('#ecebe6', 0.0, 0.5), 'petg_dark': ('#3b3f46', 0.0, 0.55),
    'batt': ('#2c3a4f', 0.1, 0.6), 'red': ('#d22b2b', 0.1, 0.45), 'yellow': ('#f2c21b', 0.1, 0.5),
    'screen': ('#0b1426', 0.3, 0.12), 'gold': ('#c9a45c', 0.85, 0.35), 'white': ('#f4f4f4', 0.0, 0.5),
    'copper': ('#b87333', 0.8, 0.35), 'ply': ('#d9b98a', 0.0, 0.8),
}

assy = cq.Assembly(name="Humanoid_Robot")
subs = {}
counter = {}
for d, M, g, mir in WL:
    p = PARTS[d['key']]
    if g not in subs:
        subs[g] = cq.Assembly(name=g)
    n = counter.get((g, d['key']), 0) + 1
    counter[(g, d['key'])] = n
    shapes = []
    for s, ck in p['bodies']:
        w = xform(s, M)
        if mir:
            w = w.mirror("YZ")
        shapes.append((w, ck))
    comp = cq.Compound.makeCompound([s for s, _ in shapes])
    child = cq.Assembly(comp, name=f"{safe(p['name'])}_{n}", color=cq.Color(*rgb(shapes[0][1])))
    for s, ck in shapes[1:]:
        try:
            child.addSubshape(s, color=cq.Color(*rgb(ck)))
        except Exception:
            pass
    subs[g].add(child)
for g in ('Taban', 'Govde', 'Kafa', 'Sag_Kol', 'Sol_Kol'):
    assy.add(subs[g])
step_path = os.path.join(OUT, "Humanoid-Robot-Montaj.step")
try:
    assy.export(step_path)
except Exception:
    assy.save(step_path)
print("STEP:", step_path, os.path.getsize(step_path) // 1024, "KB")

# --- JSON (demo)
TOL, ATOL = 0.3, 0.35
def enc(shape):
    vs, tris = shape.tessellate(TOL, ATOL)
    P = np.array([[v.x, v.y, v.z] for v in vs], dtype=np.float64)
    q = np.round(P * 10).astype(np.int16)
    I = np.array(tris, dtype=np.uint32).ravel()
    big = len(vs) >= 65535
    I = I.astype(np.uint32 if big else np.uint16)
    return dict(v=base64.b64encode(q.tobytes()).decode(), i=base64.b64encode(I.tobytes()).decode(), it=('u32' if big else 'u16'),
                nt=len(tris))

model = dict(units="mm", C=dict(W0=W0, L0=L0, H0=H0, S0=S0, ARM0=ARM0, AX=AX, X_SH=X_SH, Y_RAIL1=Y_RAIL1, Y_COV1=Y_COV1,
                                TORSO_Y0=TORSO_Y0, HEAD_UP=HEAD_UP, UP=[UP_Y0, UP_Y1], FA=[FA_Y0, FA_Y1], EXTRA=EXTRA,
                                BAT_Y0=Y_RAIL0, BAT_H=D['bat_w'], WH_R=D['wh_d'] / 2),
             col={k: v for k, v in COL.items()}, parts={}, inst=INST, head=HEAD, arm=ARM,
             check=dict(mass=Mtot, com=COM.tolist()))
ntri = 0
for k, p in PARTS.items():
    bodies = []
    for s, ck in p['bodies']:
        e = enc(s); ntri += e['nt']; e['c'] = ck; bodies.append(e)
    model['parts'][k] = dict(name=p['name'], model=p['model'], dims=p['dims'], mass=p['mass'], com=p['com'], b=bodies)
with open(MODEL_JSON, "w", encoding="utf-8") as f:
    json.dump(model, f, ensure_ascii=False, separators=(",", ":"))
print("model.json:", os.path.getsize(MODEL_JSON) // 1024, "KB, ucgen:", ntri)

# --- parca listesi
rows = {}
for d, M, g, mir in WL:
    k = d['key']
    rows.setdefault(k, 0)
    rows[k] += 1
with open(os.path.join(OUT, "parca-listesi.csv"), "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Parça", "Model / malzeme", "Ölçü (mm)", "Adet", "Birim kütle (g)", "Toplam (g)"])
    for k, n in sorted(rows.items(), key=lambda kv: -PARTS[kv[0]]['mass'] * kv[1]):
        p = PARTS[k]
        w.writerow([p['name'], p['model'], p['dims'], n, round(p['mass'] * 1000), round(p['mass'] * 1000 * n)])
    w.writerow(["Vida, somun, T-somun, kablo payı", "tahmini", "", 1, round(EXTRA * 1000), round(EXTRA * 1000)])
    w.writerow(["TOPLAM", "", "", "", "", round(Mtot * 1000)])
print("parca-listesi.csv yazildi")

# --- cakisma kontrolu (secili ciftler)
def wshape(d, M, mir=False):
    p = PARTS[d['key']]
    s = cq.Compound.makeCompound([xform(b, M) for b, _ in p['bodies']])
    return s.mirror("YZ") if mir else s
checks = []
base = [(d, M) for d, M, g, mir in WL if g in ('Taban', 'Govde') and not mir]
keys_a = {'battery', 'bts', 'xl4016', 'jgb37', 'wheel', 'pi5', 'esp32', 'pca', 'column', 'sonar', 'estop'}
keys_b = {'rail_l', 'rail_c', 'plate_bot', 'plate_deck', 'standoff', 'cover', 'column', 'corner', 'jgb37', 'wheel', 'battery', 'torso'}
for i, (da, Ma_) in enumerate(base):
    if da['key'] not in keys_a:
        continue
    sa = wshape(da, Ma_)
    ba = sa.BoundingBox()
    for j, (db, Mb) in enumerate(base):
        if j == i or db['key'] not in keys_b or (db['key'] in keys_a and j < i):
            continue
        sb = wshape(db, Mb)
        bb = sb.BoundingBox()
        if ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin:
            continue
        try:
            v = sa.intersect(sb).Volume()
        except Exception:
            v = -1
        if v > 5:
            checks.append((da['key'], db['key'], round(v)))
print("Cakismalar (mm3 > 5):", checks if checks else "yok")

# --- tarayici demosunu uret (viewer-template.html + model.json + planlama/maliyet.json -> ../Robot-Tasarim-Demosu.html)
import demo_uret
demo_uret.build(MODEL_JSON)
