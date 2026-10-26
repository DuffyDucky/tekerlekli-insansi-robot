# -*- coding: utf-8 -*-
"""Raspberry Pi 5 koruyucu kutu: parametrik, iki parça (taban + kapak), 4 köşe vidası (alttan M2.5).

Ölçüler Raspberry Pi 5 resmi mekanik çiziminden (datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf):
kart 85 x 56 mm, köşe R3, delikler Ø2.7 @ (3.5, 3.5) (61.5, 3.5) (3.5, 52.5) (61.5, 52.5);
alt uzun kenarda USB-C x=11.2, micro-HDMI x=25.8 ve 39.2; sağ kısa kenarda Ethernet y≈10.2, USB yığınları y=29.1 ve 47.

Koordinat: X kartın uzun kenarı (0..85), Y kısa kenarı (0..56), Z yukarı. Kart alt yüzü z=Z_PCB.
Çalıştır:  py -3 pi5_kutu.py   → aynı klasöre 3 STL + onizleme.png
Gerekli: pip install numpy manifold3d trimesh pillow
"""
import math, os, sys
import numpy as np
import manifold3d as mf
from manifold3d import Manifold, CrossSection, JoinType
import trimesh

mf.set_circular_segments(48)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------- parametreler (mm) ----------------
PCB_X, PCB_Y, PCB_T = 85.0, 56.0, 1.6
HOLES = [(3.5, 3.5), (61.5, 3.5), (3.5, 52.5), (61.5, 52.5)]
BOSLUK = 1.5          # kart kenarı ile iç duvar arası
DUVAR = 3.0           # duvar kalınlığı (köşe vidası için)
TABAN_T = 2.5         # zemin kalınlığı
KAPAK_T = 2.5         # kapak üst kalınlığı
STANDOFF_H = 5.0      # kart altı boşluk (microSD yuvası ve alt bileşenler ~3 mm)
STANDOFF_D = 6.0
STANDOFF_DELIK = 2.2  # M2.5 kendinden diş açan vida (PETG/PLA)
KOSE_VIDA_DELIK_KAPAK = 2.2   # kapaktaki köşe deliği (vida diş açar)
KOSE_VIDA_DELIK_TABAN = 2.8   # tabandaki köşe deliği (vida serbest geçer)
KOSE_BOSS_R = 3.0
DIS_KOSE_R = 3.0
AYIRMA = 4.0          # ayırma düzlemi: kart üstünden bu kadar yukarıda
DUDAK_H, DUDAK_T, DUDAK_TOL = 3.0, 1.0, 0.2
KAPAK_BOSLUK = {"standart": 17.0, "fanli": 24.0}   # kart üstü ile kapak içi arası
GPIO_YUVA = True      # şerit kablo için kapakta çentik

# türetilenler
IC_X, IC_Y = PCB_X + 2 * BOSLUK, PCB_Y + 2 * BOSLUK          # iç boşluk 88 x 59
DIS_X, DIS_Y = IC_X + 2 * DUVAR, IC_Y + 2 * DUVAR            # dış 94 x 65
Z_PCB = TABAN_T + STANDOFF_H                                  # kart alt yüzü
Z_PCB_UST = Z_PCB + PCB_T
Z_AYIR = Z_PCB_UST + AYIRMA

# kart koordinatından kutu koordinatına kaydırma: kart (0,0) → (DUVAR+BOSLUK, DUVAR+BOSLUK)
OX = OY = DUVAR + BOSLUK

def kutu(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def yuvarlak_dikdortgen(x, y, r, h):
    cs = CrossSection.square([x - 2 * r, y - 2 * r], True).offset(r, JoinType.Round)
    return cs.extrude(h).translate([x / 2, y / 2, 0])

def silindir(d, h, x, y, z):
    return Manifold.cylinder(h, d / 2, d / 2).translate([x, y, z])

def kabuk(z_ust):
    """Dış gövde eksi iç boşluk, köşe bosları dahil (zemin ve kapak üstü dahil)."""
    dis = yuvarlak_dikdortgen(DIS_X, DIS_Y, DIS_KOSE_R, z_ust)
    ic = kutu(DUVAR, DUVAR + IC_X, DUVAR, DUVAR + IC_Y, TABAN_T, z_ust - KAPAK_T)
    k = dis - ic
    for (cx, cy) in [(DUVAR, DUVAR), (DUVAR + IC_X, DUVAR), (DUVAR, DUVAR + IC_Y), (DUVAR + IC_X, DUVAR + IC_Y)]:
        k = k + silindir(2 * KOSE_BOSS_R, z_ust - TABAN_T - KAPAK_T, cx, cy, TABAN_T)
    return k

def port_kesikleri(z_ust):
    """Duvar çentikleri; hepsi kart altından başlar, ayırma düzlemini geçer (taban çentiği üstten açık, kapak çentiği alttan açık)."""
    c = []
    zb = Z_PCB - 1.0
    # alt uzun kenar (y=0 duvarı): USB-C ve iki micro-HDMI (fiş gövdeleri için geniş)
    for (x0, x1, h) in [(11.2 - 6.5, 11.2 + 6.5, 8.0), (25.8 - 6.5, 39.2 + 6.5, 8.0)]:
        c.append(kutu(OX + x0, OX + x1, -1, DUVAR + 1, zb, Z_PCB_UST + h))
    # sağ kısa kenar (x=85 duvarı): Ethernet, USB yığını ×2 (USB yığını ~16 mm; kapak üstüne taşmasın)
    usb_h = min(18.0, (z_ust - KAPAK_T) - Z_PCB_UST - 0.5)
    for (y0, y1, h) in [(1.5, 19.5, 15.0), (21.5, 37.0, usb_h), (39.5, 55.0, usb_h)]:
        c.append(kutu(OX + PCB_X - 1, DIS_X + 1, OY + y0, OY + y1, zb, Z_PCB_UST + h))
    # sol kısa kenar (x=0 duvarı): microSD (alt yüz), güç düğmesi, UART/RTC erişimi
    c.append(kutu(-1, DUVAR + 1, OY + 8.0, OY + 40.0, TABAN_T + 1.5, Z_PCB_UST + 3.0))
    # üst uzun kenar (y=56 duvarı): GPIO şerit kablo çentiği, yalnız kapakta (ayırma düzleminden yukarı)
    if GPIO_YUVA:
        c.append(kutu(OX + 5.0, OX + 60.0, OY + PCB_Y - 1, DIS_Y + 1, Z_AYIR - 0.01, Z_PCB_UST + 15.0))
    return c

def havalandirma(z_ust, fanli):
    """Kapak üstünde yarıklar; fanlı kapakta SoC üstünde daire ızgara."""
    v = []
    # kapak üstü yarıklar: x 18..70, y 8..50 bölgesi, 2 mm yarık, 5 mm adım (Y yönünde uzun)
    x = 18.0
    while x <= 70.0:
        yarik = kutu(OX + x, OX + x + 2.0, OY + 8.0, OY + 50.0, z_ust - KAPAK_T - 1, z_ust + 1)
        if fanli:   # fan ızgarası bölgesine yarık girmesin (adacık oluşmasın)
            yarik = yarik - silindir(2 * 16.5, KAPAK_T + 4, OX + 40.0, OY + 30.0, z_ust - KAPAK_T - 2)
        v.append(yarik)
        x += 5.0
    # üst uzun duvar (y=56 tarafı) ve alt uzun duvarda birkaç yarık (çapraz hava akışı)
    for x in (62.0, 68.0, 74.0, 80.0):
        v.append(kutu(OX + x, OX + x + 2.0, OY + PCB_Y - 1, DIS_Y + 1, Z_AYIR + 3, z_ust - KAPAK_T - 2))
    for x in (55.0, 61.0, 67.0, 73.0, 79.0):
        v.append(kutu(OX + x, OX + x + 2.0, -1, DUVAR + 1, Z_AYIR + 3, z_ust - KAPAK_T - 2))
    return v

def uret(ad, bosluk):
    fanli = ad == "fanli"
    z_ust = Z_PCB_UST + bosluk + KAPAK_T
    govde = kabuk(z_ust)
    for k in port_kesikleri(z_ust):
        govde = govde - k
    for v in havalandirma(z_ust, fanli):
        govde = govde - v
    # ---- taban
    alt = kutu(-1, DIS_X + 1, -1, DIS_Y + 1, -1, Z_AYIR)
    taban = govde ^ alt
    for (hx, hy) in HOLES:
        taban = taban + silindir(STANDOFF_D, STANDOFF_H, OX + hx, OY + hy, TABAN_T)
        taban = taban - silindir(STANDOFF_DELIK, STANDOFF_H + 2.5, OX + hx, OY + hy, TABAN_T - 1.5)   # 6,5 mm kör delik, zemin 1 mm kalır
    for (cx, cy) in [(DUVAR, DUVAR), (DUVAR + IC_X, DUVAR), (DUVAR, DUVAR + IC_Y), (DUVAR + IC_X, DUVAR + IC_Y)]:
        taban = taban - silindir(KOSE_VIDA_DELIK_TABAN, Z_AYIR + 2, cx, cy, -1)
        taban = taban - silindir(5.5, 2.0, cx, cy, -1)          # alttan havşa/ counterbore (vida başı gömülür)
    # ---- kapak
    ust = kutu(-1, DIS_X + 1, -1, DIS_Y + 1, Z_AYIR, z_ust + 1)
    kapak = govde ^ ust
    # iç dudak: iç duvara 0.2 mm payla oturur, 3 mm aşağı sarkar, kart üstüne 1 mm kala biter
    dx0, dy0 = DUVAR + DUDAK_TOL, DUVAR + DUDAK_TOL
    dudak = kutu(dx0, DUVAR + IC_X - DUDAK_TOL, dy0, DUVAR + IC_Y - DUDAK_TOL, Z_AYIR - DUDAK_H, Z_AYIR + 0.5) \
          - kutu(dx0 + DUDAK_T, DUVAR + IC_X - DUDAK_TOL - DUDAK_T, dy0 + DUDAK_T, DUVAR + IC_Y - DUDAK_TOL - DUDAK_T, Z_AYIR - DUDAK_H - 1, Z_AYIR + 1)
    # yaka: dudağı kapak duvarına bağlar (ayırma düzleminin 2 mm üstünde, duvar içine 1 mm girer)
    dudak = dudak + (kutu(DUVAR - 1.0, DUVAR + IC_X + 1.0, DUVAR - 1.0, DUVAR + IC_Y + 1.0, Z_AYIR, Z_AYIR + 2.0)
                     - kutu(dx0 + DUDAK_T, DUVAR + IC_X - DUDAK_TOL - DUDAK_T, dy0 + DUDAK_T, DUVAR + IC_Y - DUDAK_TOL - DUDAK_T, Z_AYIR - 1, Z_AYIR + 3))
    # dudak, port çentiklerinden ve köşe boslarından geçmesin
    for k in port_kesikleri(z_ust):
        dudak = dudak - k
    for (cx, cy) in [(DUVAR, DUVAR), (DUVAR + IC_X, DUVAR), (DUVAR, DUVAR + IC_Y), (DUVAR + IC_X, DUVAR + IC_Y)]:
        dudak = dudak - silindir(2 * KOSE_BOSS_R + 0.6, DUDAK_H + 2, cx, cy, Z_AYIR - DUDAK_H - 1)
    kapak = kapak + dudak
    for (cx, cy) in [(DUVAR, DUVAR), (DUVAR + IC_X, DUVAR), (DUVAR, DUVAR + IC_Y), (DUVAR + IC_X, DUVAR + IC_Y)]:
        kapak = kapak - silindir(KOSE_VIDA_DELIK_KAPAK, 9.0, cx, cy, Z_AYIR - 1)   # 8 mm diş boyu
    # fanlı kapakta SoC üstüne daire ızgara (merkez kart x≈40, y≈30; 30 mm çap)
    if fanli:
        cx, cy = OX + 40.0, OY + 30.0
        for r in (6.0, 10.0, 14.0):
            halka = silindir(2 * r + 1.6, KAPAK_T + 2, cx, cy, z_ust - KAPAK_T - 1) - silindir(2 * r - 1.6, KAPAK_T + 4, cx, cy, z_ust - KAPAK_T - 2)
            # 4 köprü kalsın (halkalar birbirine bağlı dursun)
            halka = halka - kutu(cx - 1.2, cx + 1.2, cy - 20, cy + 20, z_ust - KAPAK_T - 3, z_ust + 3)
            halka = halka - kutu(cx - 20, cx + 20, cy - 1.2, cy + 1.2, z_ust - KAPAK_T - 3, z_ust + 3)
            kapak = kapak - halka
    return taban, kapak, z_ust

def kaydet(m, yol):
    mesh = m.simplify(0.002).to_mesh()   # sıfır alanlı kıymık üçgenleri at (STL'de manifold olmayan kenar bırakır)
    tm = trimesh.Trimesh(vertices=np.asarray(mesh.vert_properties)[:, :3], faces=np.asarray(mesh.tri_verts), process=False)
    tm.export(yol)
    return tm

def onizleme(parcalar, yol, flip=()):
    """Basit izometrik çizim (PIL): kamera +x, -y, +z tarafından bakar; ressam sıralaması + arka yüz eleme.
    flip içindeki parçalar ters çevrilerek (baskı yönü) çizilir."""
    from PIL import Image, ImageDraw
    W, H, S = 1500, 760, 5.0
    img = Image.new("RGB", (W, H), (248, 248, 246)); dr = ImageDraw.Draw(img)
    V = np.array([1.0, -1.0, 1.0]); V /= np.linalg.norm(V)
    e1 = np.array([1.0, 1.0, 0.0]); e1 /= np.linalg.norm(e1)
    e2 = np.cross(V, e1); e2 /= np.linalg.norm(e2)
    light = np.array([0.3, -0.8, 0.9]); light /= np.linalg.norm(light)
    for i, (ad, tm) in enumerate(parcalar):
        v = tm.vertices.copy(); f = tm.faces
        if ad in flip:
            v[:, 2] = -v[:, 2]; v[:, 1] = -v[:, 1]
        v = v - v.mean(axis=0)
        n = tm.face_normals.copy()
        if ad in flip:
            n[:, 2] = -n[:, 2]; n[:, 1] = -n[:, 1]
        ox, oy = 250 + i * 500, 420
        depth = v[f].mean(axis=1) @ V
        for t in np.argsort(depth):
            nn = n[t]
            if nn @ V <= 0: continue
            sh = 0.35 + 0.65 * max(0.0, float(nn @ light))
            col = tuple(int(c * sh) for c in (125, 165, 205))
            pts = [(ox + (p @ e1) * S, oy - (p @ e2) * S) for p in v[f[t]]]
            dr.polygon(pts, fill=col)
        dr.text((ox - 80, 700), ad + (" (baskı yönü: ters)" if ad in flip else ""), fill=(40, 40, 40))
    img.save(yol)

if __name__ == "__main__":
    sonuc = []
    for ad, bosluk in KAPAK_BOSLUK.items():
        taban, kapak, z_ust = uret(ad, bosluk)
        if ad == "standart":
            tb = kaydet(taban, os.path.join(HERE, "pi5-kutu-taban.stl"))
            sonuc.append(("taban", tb))
            print("taban: %.0f x %.0f x %.1f mm, hacim %.1f cm3, kapalı: %s, parça: %d" % (DIS_X, DIS_Y, Z_AYIR, taban.volume() / 1000, tb.is_watertight, len(taban.decompose())))
        kp = kaydet(kapak, os.path.join(HERE, "pi5-kutu-kapak-%s.stl" % ad))
        sonuc.append(("kapak-" + ad, kp))
        print("kapak-%s: %.0f x %.0f x %.1f mm (toplam yükseklik %.1f), hacim %.1f cm3, kapalı: %s, parça: %d" % (ad, DIS_X, DIS_Y, z_ust - Z_AYIR, z_ust, kapak.volume() / 1000, kp.is_watertight, len(kapak.decompose())))
    onizleme(sonuc, os.path.join(HERE, "onizleme.png"))
    onizleme(sonuc, os.path.join(HERE, "onizleme-baski-yonu.png"), flip=("kapak-standart", "kapak-fanli"))
    print("iç boşluk %.0f x %.0f, kart alt yüzü z=%.1f, ayırma z=%.1f" % (IC_X, IC_Y, Z_PCB, Z_AYIR))
