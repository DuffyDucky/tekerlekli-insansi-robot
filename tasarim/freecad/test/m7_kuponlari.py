# M7 test kuponlari (FreeCAD 1.1, Part): duzeltme plani M7 (4. adim, 15 Ekim 2026).
# Cikti: test/stl/kupon-c..e*.stl + test/m7-kuponlari.step + test/m7-kupon-sonuc.json. Baski koordinati: Z yukari (tabla z = 0), mm.
# Mevcut tolerans_kuponu.py (kupon A, B) degismez; bu betik onlari tamamlar. Olculer arayuz.py'den yalniz OKUNUR.
#
# Kupon C  Isil gomme somun deligi, derinlik L + 1 (arayuz.INSERT boy + 1), M3 ve M5; dikey ve YATAY basilmis (M4 bulgusu:
#          omuz yuvasi M3 x 4 ve gobek M5 yatay basiliyor, kupon B'nin delikleri dikey). Her boyda: 1 dikey (nominal O),
#          1 yatay yuvarlak (nominal), 3 yatay damla (45 derece sivri ust; M3 -0,1/0/+0,1, M5 -0,2/0/+0,2).
# Kupon D1 Dirsek sikma bilezigi, KESIKSIZ: dirsek catalinin y -148...-115 dilimi (alin kapagi + kopru bandi + pim + yarikli
#          bilezik + kulaklar + 2 x M3 delik), arayuz.DIRSEK / GECME / TUP_PIM_R + dirsek_parcalar.py:97-127 ile birebir.
#          Dogrulama: dirsek/dirsek-montaj.FCStd'deki "Dirsek catali" ayni dilimle kesilip hacim / simetrik fark karsilastirilir.
# Kupon D2 Ayni bilezik, KOKTE BOSALTMALI (K-kontrol onerisi: bilezik kapaktan ~270 derece ayrilsin). Desteksiz basilsin diye
#          ayrilma yatay degil DIK bir halka yarigidir: kapakta r 28,1...29,3, teta -225...45 (teta: tup ekseni etrafinda -Z'den
#          +X'e). Bagli kalan 90 derece +X kopru bandinda (gercek catalda dis kol / horn yuk yolu kopru uzerinden pime gider,
#          kesilemez). Bu sektorde tup alin yuvasinin V olugu yerine pimden disa yukselen 45 derece koni tavan (askida kenar kalmasin).
# Kupon E  Ust kol tupu halkasi: r 25,65...28 (arayuz: TUP_PIM_R + GECME['tup_pim'] ... DIRSEK['tup_ro']), boy 36 (25 bilezige
#          girer), disarida kalan uca O6 kol deligi (burulma testi). Gercek tup gibi dik, uc tablada basilir.
# Test proseduru ve kabul olcutleri: test/README.md.
import os, sys, math, json
import FreeCAD as App
import Part
import MeshPart

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (UST, os.path.join(UST, "dirsek")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
from ortak_lib import box, cyl, V   # noqa
import arayuz as A

SONUC = dict(betik="test/m7_kuponlari.py", arayuz=dict(INSERT=A.INSERT, INSERT_DELIK=A.INSERT_DELIK, GECME=A.GECME,
                                                      TUP_PIM_R=A.TUP_PIM_R, DIRSEK={k: A.DIRSEK[k] for k in (
                                                          "tup_x", "tup_z", "tup_uc_y", "tup_ro", "tup_ri", "bilezik_ri",
                                                          "bilezik_yarik", "bilezik_on_yuk_min")}))


def koni(r0, r1, p0, p1):
    p0, p1 = V(*p0), V(*p1)
    d = p1 - p0
    return Part.makeCone(r0, r1, d.Length, p0, d.normalize())


def prizma_xy(pts, z0, z1):
    """(x, y) cokgeni z0..z1 boyunca."""
    P = [V(a, b, z0) for (a, b) in pts]
    return Part.Face(Part.makePolygon(P + [P[0]])).extrude(V(0, 0, z1 - z0))


def prizma_xz(pts, y0, y1):
    """(x, z) cokgeni y0..y1 boyunca."""
    P = [V(a, y0, b) for (a, b) in pts]
    return Part.Face(Part.makePolygon(P + [P[0]])).extrude(V(0, y1 - y0, 0))


def noktalar(n, x, y, z_ust, aralik=2.6, yon=(1, 0)):
    """Ust yuzde n adet O1,6 x 0,6 cukur (sira etiketi)."""
    s = None
    for i in range(n):
        px, py = x + i * aralik * yon[0], y + i * aralik * yon[1]
        c = cyl(0.8, (px, py, z_ust - 0.6), (px, py, z_ust + 1))
        s = c if s is None else s.fuse(c)
    return s


def damla_delik(r, p0, eksen, L, sivri=True):
    """Yatay delik: O2r silindir + +Z yonunde 45 derece sivri uc (damla). eksen: (ex, ey, 0) yatay birim vektor."""
    ex, ey = eksen[0], eksen[1]
    c = cyl(r, p0, (p0[0] + ex * L, p0[1] + ey * L, p0[2]))
    if not sivri:
        return c
    # kesit duzlemi: yan yon u = (-ey, ex, 0), ust = Z
    u = V(-ey, ex, 0)
    s2 = math.sqrt(0.5)
    pts = [V(*p0) + u * (r * s2) + V(0, 0, r * s2), V(*p0) + V(0, 0, r * math.sqrt(2.0)), V(*p0) - u * (r * s2) + V(0, 0, r * s2),
           V(*p0)]
    f = Part.Face(Part.makePolygon(pts + [pts[0]]))
    return c.fuse(f.extrude(V(ex * L, ey * L, 0))).removeSplitter()


# ====================================================================== Kupon C: isil gomme somun, L + 1, dikey + yatay
PAY = 1.0                                                     # derinlik = L + 1 (kupon B: L + 0,5)
L3 = A.INSERT[3][1] + PAY                                     # 6,7
L5 = A.INSERT[5][1] + PAY                                     # 8,0
D3, D5 = A.INSERT_DELIK[3], A.INSERT_DELIK[5]                 # 4,0 / 6,4 (nominal)
DUVAR = 2.5                                                   # M3 ve M5 delik diplerinin arasindaki ortak arka duvar
Y_TOP = L3 + DUVAR + L5                                       # 17,2
H3, H5 = 11.0, 14.0                                           # blok yukseklikleri
Z3, Z5 = 5.0, 6.5                                             # yatay delik eksen yukseklikleri
X3 = [4.5 + 9.0 * i for i in range(4)]                        # M3 yatay delikler (adim 9: O4,6 somun arasi 4,4 et)
X5 = [6.0 + 12.0 * i for i in range(4)]                       # M5 yatay delikler (adim 12: O7 somun arasi 5 et)
LX3, LX5 = 46.0, 61.0
c3 = box(0, LX3, 0, L3 + DUVAR, 0, H3)                        # M3 bolumu: delik agzi -Y yuzunde
c5 = box(0, LX5, L3, Y_TOP, 0, H5)                            # M5 bolumu: delik agzi +Y yuzunde
kc = c3.fuse(c5).removeSplitter()
C_DELIK = []
# yatay: [yuvarlak nominal, damla -, damla nominal, damla +]
v3 = [(D3, False), (D3 - 0.1, True), (D3, True), (D3 + 0.1, True)]
v5 = [(D5, False), (D5 - 0.2, True), (D5, True), (D5 + 0.2, True)]
for i, (d, sv) in enumerate(v3):
    kc = kc.cut(damla_delik(d / 2, (X3[i], -1.0, Z3), (0, 1, 0), L3 + 1.0, sv))
    kc = kc.cut(noktalar(i + 1, X3[i] - 3.9, 1.3, H3))
    C_DELIK.append(dict(boy="M3", yon="yatay", bicim="damla" if sv else "yuvarlak", cap=round(d, 2), derinlik=L3, nokta=i + 1,
                        agiz="-Y yuzu", x=X3[i], z=Z3))
for i, (d, sv) in enumerate(v5):
    kc = kc.cut(damla_delik(d / 2, (X5[i], Y_TOP + 1.0, Z5), (0, -1, 0), L5 + 1.0, sv))
    kc = kc.cut(noktalar(i + 1, X5[i] - 3.9, Y_TOP - 1.3, H5))
    C_DELIK.append(dict(boy="M5", yon="yatay", bicim="damla" if sv else "yuvarlak", cap=round(d, 2), derinlik=L5, nokta=i + 1,
                        agiz="+Y yuzu", x=X5[i], z=Z5))
# dikey (nominal, L + 1): M3 bolumunun ucunda ustten, M5 bolumunun ucunda ustten
XV3, YV3 = 40.5, (L3 + DUVAR) / 2 - 0.3
XV5, YV5 = 54.5, (L3 + Y_TOP) / 2
kc = kc.cut(cyl(D3 / 2, (XV3, YV3, H3 - L3), (XV3, YV3, H3 + 1)))
kc = kc.cut(cyl(D5 / 2, (XV5, YV5, H5 - L5), (XV5, YV5, H5 + 1)))
C_DELIK.append(dict(boy="M3", yon="dikey", bicim="yuvarlak", cap=D3, derinlik=L3, nokta=0, agiz="ust yuz", x=XV3, z=H3))
C_DELIK.append(dict(boy="M5", yon="dikey", bicim="yuvarlak", cap=D5, derinlik=L5, nokta=0, agiz="ust yuz", x=XV5, z=H5))
kupon_c = kc.removeSplitter()

# ====================================================================== Kupon D: dirsek sikma bilezigi (dirsek yerel koordinati)
D = A.DIRSEK
TX, TZ, TUC = D["tup_x"], D["tup_z"], D["tup_uc_y"]           # 185 / -1,25 / -140
R_PIM = A.TUP_PIM_R                                           # 25,4
R_TUP_IC = D["tup_ri"]                                        # 25,65 (= R_PIM + GECME tup_pim)
R_TUP_DIS = D["tup_ro"]                                       # 28,0
R_BIL_IC = D["bilezik_ri"]                                    # 28,25 (= tup_ro + GECME tup_bilezik)
YARIK_W = D["bilezik_yarik"]                                  # 4,0
# dirsek_parcalar.py'de sabit olan (arayuzde olmayan) olculer: oradaki satirlarla ayni (FCStd dilimiyle dogrulanir)
R_BIL_DIS = 31.0                                              # bilezik / alin kapagi dis yaricapi
Y_KAPAK = -148.0                                              # KOPRU_Y[0]: kapak + kopru ust siniri (kollarin basladigi yuz)
Y_TABLA = -115.0                                              # pim ve bilezik ucu (ters baskida tabla)
IC_KOL0, DIS_KOL1 = 156.0, 224.9                              # kopru x (IC_KOL[0], DIS_KOL[1])
KELEPCE_Y, KELEPCE_Z = (-121.0, -132.0), TZ - 36.0
KO = A.KOL_KABLO["catal_oluk"]


def bilezik_kesiti(bosaltma):
    c = cyl(R_PIM, (TX, TUC, TZ), (TX, Y_TABLA, TZ))
    c = c.fuse(cyl(R_BIL_DIS, (TX, TUC, TZ), (TX, Y_TABLA, TZ)))
    c = c.fuse(box(178.0, 192.0, -138.0, Y_TABLA, TZ - 41.0, TZ - 30.0))                       # sikma kulaklari
    c = c.fuse(cyl(R_BIL_DIS, (TX, Y_KAPAK, TZ), (TX, TUC, TZ)))                                # alin kapagi
    c = c.fuse(box(IC_KOL0, DIS_KOL1, Y_KAPAK, TUC, TZ - 16.0, TZ + 16.0))                      # kopru bandi
    c = c.fuse(prizma_xy([(213.0, -128.0), (DIS_KOL1, -139.9), (DIS_KOL1, TUC), (213.0, TUC)], TZ - 16.0, TZ + 16.0))
    c = c.cut(cyl(R_BIL_IC, (TX, TUC, TZ), (TX, -114.0, TZ)).cut(cyl(R_PIM, (TX, TUC - 1, TZ), (TX, -113.0, TZ))))
    if not bosaltma:                                                                           # gercek: 45 derece V oluk
        om, od = 0.5 * (R_TUP_IC + R_TUP_DIS), 0.5 * (R_TUP_DIS - R_TUP_IC)
        oluk = Part.Face(Part.makePolygon([V(TX + R_TUP_IC, TUC, TZ), V(TX + R_TUP_DIS, TUC, TZ), V(TX + om, TUC - od, TZ),
                                           V(TX + R_TUP_IC, TUC, TZ)]))
        c = c.cut(oluk.revolve(V(TX, 0, TZ), V(0, 1, 0), 360))
    pah = box(140.0, 240.0, Y_KAPAK - 0.1, TUC + 0.01, TZ + 16.0, TZ + 40.0).cut(
        koni(31.0, 23.0, (TX, TUC + 0.01, TZ), (TX, Y_KAPAK - 0.01, TZ)))
    c = c.cut(pah)
    c = c.cut(cyl(21.9, (TX, -114.0, TZ), (TX, -122.0, TZ)))                                    # pim ici bos
    c = c.cut(koni(21.9, 5.0, (TX, -122.0, TZ), (TX, -138.9, TZ)))                              # 45 der. tavan
    c = c.cut(cyl(5.0, (TX, -138.0, TZ), (TX, Y_KAPAK - 1.0, TZ)))                              # kablo deligi
    c = c.cut(box(KO["x"][0], KO["x"][1], KO["y"][0] - 0.01, KO["y"][1], KO["z"][0], KO["z"][1]))   # M1 kablo olugu
    c = c.cut(box(TX - YARIK_W / 2, TX + YARIK_W / 2, TUC, -114.0, TZ - 45.0, TZ - 27.5))       # yarik
    for yb in KELEPCE_Y:
        c = c.cut(cyl(A.CLEAR[3] / 2, (177.0, yb, KELEPCE_Z), (193.0, yb, KELEPCE_Z)))
    if bosaltma:
        B = BOSALTMA
        r0, r1 = B["r"]
        # pimden disa yukselen 45 derece koni tavan (r R_PIM -> r0), 360 derece
        tavan = Part.Face(Part.makePolygon([V(TX + R_PIM, TUC + 0.01, TZ), V(TX + r0, TUC + 0.01, TZ), V(TX + r0, TUC - (r0 - R_PIM), TZ),
                                            V(TX + R_PIM, TUC + 0.01, TZ)]))
        c = c.cut(tavan.revolve(V(TX, 0, TZ), V(0, 1, 0), 360))
        # dik halka yarigi: kapak boyunca (TUC -> Y_KAPAK), serbest sektorde
        hal = cyl(r1, (TX, TUC + 0.01, TZ), (TX, Y_KAPAK - 0.1, TZ)).cut(cyl(r0, (TX, TUC + 0.1, TZ), (TX, Y_KAPAK - 0.2, TZ)))
        t0, t1 = B["teta"]
        n = int((t1 - t0) / 5) + 1
        pts = [(TX, TZ)] + [(TX + 80 * math.sin(math.radians(t0 + (t1 - t0) * k / (n - 1))),
                             TZ - 80 * math.cos(math.radians(t0 + (t1 - t0) * k / (n - 1)))) for k in range(n)]
        c = c.cut(hal.common(prizma_xz(pts, TUC + 1.0, Y_KAPAK - 1.0)))
        # yarigin kapak bolumu: dis halka da yarilmali (ic disk r < r0 kesilmez)
        c = c.cut(box(TX - YARIK_W / 2, TX + YARIK_W / 2, Y_KAPAK - 0.1, TUC + 0.01, TZ - 45.0, TZ - B["yarik_kapak_z"]))
    return c.removeSplitter()


BOSALTMA = dict(r=(28.1, 29.3), teta=(-225.0, 45.0), yarik_kapak_z=28.8,
                not_="dik halka yarigi 1,2 mm, serbest 270 derece; bagli sektor teta 45...135 (+X kopru bandi teta 59...121 icinde)")
SONUC["bosaltma"] = BOSALTMA
d1_yerel = bilezik_kesiti(False)
d2_yerel = bilezik_kesiti(True)

# --- dogrulama: FCStd'deki gercek catalin ayni dilimi
dog = dict()
try:
    fc = os.path.join(UST, "dirsek", "dirsek-montaj.FCStd")
    doc_d = App.openDocument(fc)
    obj = [o for o in doc_d.Objects if o.Label == "Dirsek catali" and hasattr(o, "Shape") and o.Shape.Volume > 1]
    gercek = obj[0].Shape.copy()
    dilim = box(100, 300, Y_KAPAK, Y_TABLA, -100, 100)
    g = gercek.common(dilim)
    fark1 = g.cut(d1_yerel).Volume
    fark2 = d1_yerel.cut(g).Volume
    dog = dict(dosya="dirsek/dirsek-montaj.FCStd", parca="Dirsek catali", gercek_bb=[round(v, 2) for v in (
        gercek.BoundBox.XMin, gercek.BoundBox.XMax, gercek.BoundBox.YMin, gercek.BoundBox.YMax, gercek.BoundBox.ZMin, gercek.BoundBox.ZMax)],
        dilim_hacim_mm3=round(g.Volume, 2), d1_hacim_mm3=round(d1_yerel.Volume, 2),
        gercekte_var_d1de_yok_mm3=round(fark1, 3), d1de_var_gercekte_yok_mm3=round(fark2, 3), ok=bool(fark1 < 1.0 and fark2 < 1.0))
    App.closeDocument(doc_d.Name)
except Exception as e:   # noqa
    dog = dict(hata=repr(e), ok=False)
SONUC["d1_fcstd_dogrulama"] = dog
print("D1 ~ FCStd dilimi:", dog)


def yarik_olc(s, y):
    """Yarik genisligi: y kesitinde, bilezik duvari ortasinda (r 29,6) x boyunca bosluk."""
    zc = TZ - 29.6
    ser = s.common(box(TX - 10, TX + 10, y - 0.05, y + 0.05, zc - 0.05, zc + 0.05))
    xs = sorted([(so.BoundBox.XMin, so.BoundBox.XMax) for so in ser.Solids])
    if len(xs) < 2:
        return None
    sol = max(a[1] for a in xs if a[1] <= TX + 0.01)
    sag = min(a[0] for a in xs if a[0] >= TX - 0.01)
    return round(sag - sol, 3)


# ölçümler: yarik (uc, kok), bagli sektor, tup halkasi ile bosluklar
TUP_BOY, TUP_GIRIS = 36.0, 25.0


def tup_yerel(y_uc):
    t = cyl(R_TUP_DIS, (TX, y_uc, TZ), (TX, y_uc + TUP_BOY, TZ)).cut(cyl(R_TUP_IC, (TX, y_uc - 1, TZ), (TX, y_uc + TUP_BOY + 1, TZ)))
    yk = y_uc + TUP_GIRIS + (TUP_BOY - TUP_GIRIS) / 2                                       # O6 kol deligi: disarida kalan bolumun ortasi
    return t.cut(cyl(3.0, (TX - 40, yk, TZ), (TX + 40, yk, TZ))), yk


OLC = {}
for ad, s in (("D1", d1_yerel), ("D2", d2_yerel)):
    t, _ = tup_yerel(TUC + 0.02)
    cak = t.common(s).Volume
    # radyal bosluklar: tup ile pim (ic) ve bilezik (dis), uc ve kok kesitlerinde
    ol = dict(yarik_uc_mm=yarik_olc(s, -116.0), yarik_kok_mm=yarik_olc(s, -139.5), tup_cakisma_mm3=round(cak, 4))
    if ad == "D2":
        # bagli sektor: kapak icinde r 28,7'de (yarik ortasi) aci boyunca dolu mu
        dolu = []
        for tt in range(-180, 181, 5):
            x = TX + 28.7 * math.sin(math.radians(tt))
            z = TZ - 28.7 * math.cos(math.radians(tt))
            if s.isInside(V(x, -144.0, z), 0.01, True):
                dolu.append(tt)
        ol["kapakta_r28.7_dolu_teta"] = [min(dolu), max(dolu)] if dolu else None
        # tupun oturdugu derinlik (koni tavan): tup ic kenari r 25,65'te tavan y'si
        ol["tup_oturma_y"] = round(TUC - (R_TUP_IC - R_PIM), 3)
    OLC[ad] = ol
OLC["radyal_bosluk_mm"] = dict(tup_pim=round(R_TUP_IC - R_PIM, 3), tup_bilezik=round(R_BIL_IC - R_TUP_DIS, 3),
                               toplam=round(R_TUP_IC - R_PIM + R_BIL_IC - R_TUP_DIS, 3),
                               yarik_kapaninca_r_dususu=round(YARIK_W / (2 * math.pi), 3),
                               ideal_on_yuk=round(YARIK_W / (2 * math.pi) - (R_TUP_IC - R_PIM + R_BIL_IC - R_TUP_DIS), 3))
SONUC["olcum"] = OLC
print("olcum:", OLC)


# --- baski koordinatina: ters (pim/bilezik ucu y -115 tablada, kapak ustte). (x, y, z) yerel -> (x - TX, z - TZ, -(y + 115))
def ters_bas(s):
    s = s.copy()
    m = App.Matrix()
    m.A11, m.A12, m.A13, m.A14 = 1, 0, 0, -TX
    m.A21, m.A22, m.A23, m.A24 = 0, 0, 1, -TZ
    m.A31, m.A32, m.A33, m.A34 = 0, -1, 0, Y_TABLA           # -(y - Y_TABLA) = -y - 115
    s.transformShape(m)
    return s


kupon_d1 = ters_bas(d1_yerel)
kupon_d2 = ters_bas(d2_yerel)
tup_y, YK = tup_yerel(0.0)
# tup: uc (bilezige giren) tablada, eksen Z
mt = App.Matrix()
mt.A11, mt.A12, mt.A13, mt.A14 = 1, 0, 0, -TX
mt.A21, mt.A22, mt.A23, mt.A24 = 0, 0, -1, TZ    # sag el: (x - TX, -(z - TZ), y)
mt.A31, mt.A32, mt.A33, mt.A34 = 0, 1, 0, 0
kupon_e = tup_y.copy()
kupon_e.transformShape(mt)
SONUC["tup"] = dict(r_ic=R_TUP_IC, r_dis=R_TUP_DIS, boy=TUP_BOY, giris=TUP_GIRIS, kol_deligi=dict(d=6.0, z=YK))


# ====================================================================== baski kontrolu (mesh): 45 derece ustu asagi bakan yuz
def baski_kontrol(s, ad):
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.02, AngularDeflection=0.2)
    alan, bolge = 0.0, []
    for f in m.Facets:
        n = f.Normal
        zc = sum(p[2] for p in f.Points) / 3
        if n.z < -math.cos(math.radians(44.0)) and zc > 0.05:       # 46 derece ustu (normal -Z ile 44 dereceden dar); tam 45 derece yuzler (koni, V oluk) tessellation payiyla haric
            alan += f.Area
            bolge.append((round(zc, 1), f.Area))
    # buyuk yatay tavanlar (n.z ~ -1, 0,5 mm2 ustu alanlar, z'ye gore grupla)
    gr = {}
    for zc, a in bolge:
        gr[zc] = gr.get(zc, 0.0) + a
    en = sorted(gr.items(), key=lambda kv: -kv[1])[:6]
    yatay = sum(f.Area for f in m.Facets if f.Normal.z < -0.98 and sum(p[2] for p in f.Points) / 3 > 0.05)
    return dict(cikinti_46ustu_mm2=round(alan, 1), yatay_tavan_mm2=round(yatay, 1), en_buyuk_z_mm2=[(z, round(a, 1)) for z, a in en])


# ====================================================================== cikti
os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
KUPON = [("kupon-c-isil-gomme-L1", kupon_c, "PETG-CF ve PETG (iki kez; kabuk PETG, omuz PETG-CF)", 0.0),
         ("kupon-d1-kelepce-kesiksiz", kupon_d1, "catalin malzemesi (dirsek_parcalar: PETG; D6 degistirirse o)", 0.0),
         ("kupon-d2-kelepce-bosaltmali", kupon_d2, "D1 ile ayni", 0.0),
         ("kupon-e-tup-halkasi", kupon_e, "ust kol tupunun malzemesi (beyaz PETG)", 0.0)]
RHO = A.PETG_RHO
HIZ = A.PETG_HACIM_HIZI
SONUC["kuponlar"] = []
for ad, s, malz, _ in KUPON:
    bb = s.BoundBox
    assert s.isValid() and len(s.Solids) == 1, ad
    assert abs(bb.ZMin) < 1e-6, (ad, bb.ZMin)
    MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.1).write(os.path.join(HERE, "stl", ad + ".stl"))
    # dilimleyici benzeri tahmin: 4 cevre (1,6 mm kabuk) + %25 dolgu (tahmini)
    kab = min(s.Volume, s.Area * 1.6 * 0.5)          # alanin yarisi kadar kabuk (ic/dis yuzler ortak; kaba tahmin)
    v_eff = kab + 0.25 * max(0.0, s.Volume - kab)
    taban = s.common(box(bb.XMin - 1, bb.XMax + 1, bb.YMin - 1, bb.YMax + 1, -0.01, 0.2)).Volume / 0.21
    k = dict(ad=ad, stl="test/stl/%s.stl" % ad, malzeme=malz,
             olcu_mm=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
             hacim_cm3=round(s.Volume / 1000, 2), kutle_100_g=round(s.Volume / 1000 * RHO, 1),
             kutle_tahmini_g=round(v_eff / 1000 * RHO, 1), sure_tahmini_dk=round(v_eff / HIZ / 60 * 1.3, 0),
             tabla_temas_mm2=round(taban, 0), baski=baski_kontrol(s, ad))
    SONUC["kuponlar"].append(k)
    print(k)
SONUC["kupon_c_delikler"] = C_DELIK
SONUC["toplam"] = dict(kutle_100_g=round(sum(k["kutle_100_g"] for k in SONUC["kuponlar"]), 1),
                       kutle_tahmini_g=round(sum(k["kutle_tahmini_g"] for k in SONUC["kuponlar"]), 1),
                       sure_tahmini_dk=round(sum(k["sure_tahmini_dk"] for k in SONUC["kuponlar"]), 0),
                       not_="tahmini: 4 cevre + %25 dolgu, 10 mm3/s ortalama debi (arayuz.PETG_HACIM_HIZI) x 1,3 hareket payi; "
                            "kupon C iki malzemede basilirsa iki kez sayilir")
doc = App.newDocument("m7kupon")
for ad, s, _, _ in KUPON:
    doc.addObject("Part::Feature", ad.replace("-", "_")).Shape = s
Part.export(list(doc.Objects), os.path.join(HERE, "m7-kuponlari.step"))
with open(os.path.join(HERE, "m7-kupon-sonuc.json"), "w", encoding="utf-8") as f:
    json.dump(SONUC, f, ensure_ascii=False, indent=1)
print("toplam:", SONUC["toplam"])
print("bitti")
