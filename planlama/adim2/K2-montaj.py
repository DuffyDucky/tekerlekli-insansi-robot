# K2 (3. ajan, 25 Ekim 2026): S1 kaseti montaj yolu + kaset civatasi alet erisimi + tambur kablo bagi kayisi. Yalniz okur.
# K2-kaydir.json: kaset govdesi / kapagi YALNIZ +x yonunden kaydirilamiyor (gobek r <= 47 / ust kol tupu, t 1,5...10,5'te temas).
# Burada uygulanabilir yol araniyor:
#   1) kapak +x ofset t'de iken gobek + kol ile en kucuk mesafe, S1 -60...180 (5) x S2 5 / 30 / 90  -> t_gerekli (pim 3,0 mm,
#      dikme basligi x 155 > duvar ustu 158,3 icin t >= 3,3) ile karsilastirma
#   2) duzlem ici (yz) radyal yaklasma: govde x ofset 0'da, kapak x ofset t'de, sektor ortaortayi (bisektor) boyunca disaridan iceri
#      s 0...90 mm; hedef: kabuk sag parcalari (kaset ve civatalari haric; kapak icin govde dahil), gobek, kol. common hacmi.
#   3) kaset civatasi alet erisimi (+x dogrusu, bas ustu -> x 330): gobek + kol en yakin, S1 x S2
#   4) tambur kablo bagi kayisi (1,0 x 2,5 mm, halkanin altindan iki yarik arasi) <-> kapak civatalari + rulman kapagi, S1 -45...135
# Cikti: K2-montaj.json
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part

A, V, log, tasi = O.A, O.V, O.log, O.tasi
t0 = time.time()
ADIM = os.environ.get("K2_ADIM", "hepsi")
JS = "K2-montaj%s.json" % ("" if ADIM == "hepsi" else "-" + ADIM)
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
OMU = O.ac("omuz/omuz-montaj.FCStd")
KABT = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd")
GOB = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Gobek"]
GOV = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Govde" and p["tur"] != "Referans"]
KOL = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Kol"] + [(p["ad"], p["shape"]) for p in DIR if p["grup"] == "UstKol"]
KG = {p["ad"]: p["shape"] for p in KABT}
GOVDE, KAPAK = KG["S1 kaset govdesi sag"], KG["S1 kaset kapagi sag"]
KCIV = [(p["ad"], p["shape"]) for p in KABT if p["ad"].startswith("Kaset civatasi")]
KAB_D = [(p["ad"], p["shape"]) for p in KABT if not p["ad"].startswith("S1 kaset") and not p["ad"].startswith("Kaset civatasi")]


def hareketli(phi, th):
    return [(a, tasi(s, O.Pp(phi))) for a, s in GOB] + [(a, tasi(s, O.Pp(phi).multiply(O.Pr(th)))) for a, s in KOL]


def kes(sh, hed, esik=1e-3, pay=0.5):
    """common hacmi > esik olan hedefler + en kucuk mesafe."""
    bb = App.BoundBox(sh.BoundBox)
    bb.enlarge(pay)
    vol, en = [], (1e9, None)
    for a, q in hed:
        if not bb.intersect(q.BoundBox):
            continue
        d = sh.distToShape(q)[0]
        if d < en[0]:
            en = (round(d, 3), a)
        if d < 1e-6:
            v = sh.common(q).Volume
            if v > esik:
                vol.append((a, round(v, 3)))
    return vol, en


def psi_aralik(sh):
    ps = sorted(O.yz_psi(v.Y, v.Z)[0] for v in sh.Vertexes)
    return ps[0], ps[-1]


def kaydir(sh, x=0.0, d=None, s=0.0):
    q = sh.copy()
    q.translate(V(x, 0, 0) + (d * s if d is not None else V(0, 0, 0)))
    return q


# ---------------------------------------------------------------- 1) kapak x ofseti
if ADIM in ("hepsi", "ofset"):
    sat = []
    for th in (5.0, 30.0, 90.0):
        for phi in range(-60, 181, 5):
            hed = hareketli(float(phi), th)
            r = {}
            for t in (3.0, 3.3, 3.6, 4.0, 5.0):
                vol, en = kes(kaydir(KAPAK, t), hed, pay=1.0)
                r[t] = (en[0], en[1], sum(v for _, v in vol))
            sat.append(dict(phi=phi, S2=th, d=r))
        log("ofset S2", th, "%.0fs" % (time.time() - t0))
    OUT["kapak_ofset"] = sat
    # S2 basina: t 3,3 ve 3,6'da en buyuk bosluk veren S1
    oz = {}
    for th in (5.0, 30.0, 90.0):
        q = [s_ for s_ in sat if s_["S2"] == th]
        for t in (3.3, 3.6):
            b = max(q, key=lambda s_: s_["d"][t][0])
            oz["S2 %.0f t %.1f" % (th, t)] = dict(en_iyi_phi=b["phi"], bosluk=b["d"][t][0], parca=b["d"][t][1],
                                                  temiz_phi=[s_["phi"] for s_ in q if s_["d"][t][0] >= 0.3])
    OUT["kapak_ofset_ozet"] = oz
    log(oz)
    O.kaydet(JS, OUT)

# ---------------------------------------------------------------- 2) radyal yaklasma
if ADIM in ("hepsi", "radyal"):
    rad = []
    for ad_, sh, x_of, ek in (("govde", GOVDE, 0.0, []), ("kapak", KAPAK, 3.3, [("S1 kaset govdesi sag", GOVDE)]),
                              ("kapak", KAPAK, 3.6, [("S1 kaset govdesi sag", GOVDE)])):
        p0, p1 = psi_aralik(sh)
        pm = (p0 + p1) / 2
        dy, dz = O.psi_yz(pm, 1.0)
        d = V(0, dy, dz)
        for phi, th in ((-45.0, 90.0), (-20.0, 90.0), (0.0, 90.0), (-45.0, 5.0)):
            hed = KAB_D + ek + hareketli(phi, th)
            yol = []
            for s in [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 16.0, 20.0, 25.0, 30.0, 40.0, 50.0, 60.0, 75.0, 90.0]:
                vol, en = kes(kaydir(sh, x_of, d, s), hed)
                yol.append((s, en[0], en[1], vol))
            rad.append(dict(parca=ad_, x_ofset=x_of, psi=[round(p0, 1), round(p1, 1)], yon_psi=round(pm, 1), S1=phi, S2=th,
                            cakisan=[q for q in yol if q[3]], en_kucuk=min(((q[1], q[0], q[2]) for q in yol)), yol=yol))
            log(ad_, x_of, phi, th, "cakisan", [(q[0], q[3]) for q in yol if q[3]][:4], "%.0fs" % (time.time() - t0))
            OUT["radyal"] = rad
            O.kaydet(JS, OUT)
    # kapak son eksenel adim (x ofset 3,6 -> 0) radyal konumda: gobek / kol / govde
    son = []
    for phi, th in ((-45.0, 90.0), (-20.0, 90.0), (0.0, 90.0)):
        hed = [("S1 kaset govdesi sag", GOVDE)] + hareketli(phi, th) + KAB_D
        for t in (3.6, 3.0, 2.0, 1.0, 0.5, 0.0):
            vol, en = kes(kaydir(KAPAK, t), hed)
            son.append((phi, th, t, en, vol))
    OUT["kapak_eksenel_son"] = son
    log("eksenel son", [q for q in son if q[4]])
    O.kaydet(JS, OUT)

# ---------------------------------------------------------------- 3) civata erisimi
if ADIM in ("hepsi", "erisim"):
    eris = []
    for a, s in KCIV:
        c = s.BoundBox.Center
        line = Part.makeLine(V(s.BoundBox.XMax + 0.01, c.y, c.z), V(330.0, c.y, c.z))
        en_iyi = (-1, None)
        satir = []
        for th in (5.0, 45.0, 90.0):
            for phi in range(-60, 181, 5):
                dd, _, b = O.enaz([("l", line)], hareketli(float(phi), th), pay=8)
                dd = min(dd, 8.0)
                satir.append((phi, th, round(dd, 2), b))
        b = max(satir, key=lambda q: q[2])
        eris.append(dict(civata=a, psi_r=[round(v, 1) for v in O.yz_psi(c.y, c.z)], en_iyi=b,
                         acik_ge_2=[(q[0], q[1]) for q in satir if q[2] >= 2.0][:80], satir=satir))
        log("erisim", a, b, "%.0fs" % (time.time() - t0))
    OUT["civata_erisim"] = eris
    O.kaydet(JS, OUT)

# ---------------------------------------------------------------- 4) kayis
if ADIM in ("hepsi", "kayis"):
    TB = A.KOL_KABLO["s1"]["tambur"]
    bag = TB["bag_psi"]
    TAMBUR = [(a, s) for a, s in GOB if a == "S1 kablo tamburu"]

    def sektor(r0, r1, x0, x1, p0, p1):
        n = 40
        dis = [V(x0, *O.psi_yz(p0 + (p1 - p0) * i / n, r1)) for i in range(n + 1)]
        ic = [V(x0, *O.psi_yz(p1 - (p1 - p0) * i / n, r0)) for i in range(n + 1)]
        return Part.Face(Part.makePolygon(dis + ic + [dis[0]])).extrude(V(x1 - x0, 0, 0))
    xm = (154.4 + 157.4) / 2
    ks0 = sektor(TB["r"][0] - 1.0, TB["r"][0], xm - 1.25, xm + 1.25, bag + 3.0 - 1.25, bag + 11.0 + 1.25)
    tb_c = ks0.common(TAMBUR[0][1]).Volume
    CAPB = [(a, s) for a, s in GOV if a.startswith("Kapak civatasi") or a == "Rulman kapagi"]
    # yarik konumlari (tamburda bagin iki yarigi): tambur ile r 36...37 halkasinin ortak hacmi psi_g dagilimi
    sat = []
    for phi in np.arange(-45, 135.01, 1.0):
        ks = tasi(ks0, O.Pp(float(phi)))
        d, _, b = O.enaz([("k", ks)], CAPB, pay=5)
        sat.append((float(phi), round(d, 3), b))
    # tambur ic yuzu (r 37) <-> kapak civata basi / rulman kapagi tum S1'de (kayis kalinligi bu bosluga sigmali)
    ic = []
    for phi in np.arange(-45, 135.01, 2.5):
        d, _, b = O.enaz([(a, tasi(s, O.Pp(float(phi)))) for a, s in TAMBUR], CAPB, pay=5)
        ic.append((float(phi), round(d, 3), b))
    # temasli pozlarda ortak hacim + kayisin oturdugu sektorde tambur ic yuzunun (r 37) sabit parcalara bosluk (kayis kalinligi 1,0 sigmali)
    hac = []
    for phi in [q[0] for q in sat if q[1] < 1e-6]:
        ks = tasi(ks0, O.Pp(float(phi)))
        v = sum(ks.common(s).Volume for a, s in CAPB if ks.BoundBox.intersect(s.BoundBox))
        hac.append((phi, round(v, 3)))
    ks_tb = sektor(TB["r"][0] - 0.001, TB["r"][0], TB["x"][0], TB["x"][1], bag + 1.75, bag + 12.25)     # tambur ic yuzu (ince kabuk)
    bos = []
    for phi in np.arange(-45, 135.01, 1.0):
        d, _, b = O.enaz([("k", tasi(ks_tb, O.Pp(float(phi))))], CAPB, pay=5)
        bos.append((float(phi), round(d, 3), b))
    OUT["kayis_hacim"] = hac
    OUT["kayis_sektor_ic_bosluk"] = dict(en_az=min(bos, key=lambda q: q[1]), satir=bos)
    log("kayis hacim", hac, "sektor bosluk", min(bos, key=lambda q: q[1]))
    OUT["kayis"] = dict(model="r %.1f...%.1f, x %.2f...%.2f, psi_g %.2f...%.2f" % (TB["r"][0] - 1, TB["r"][0], xm - 1.25, xm + 1.25,
                                                                                    bag + 1.75, bag + 12.25),
                        tambura_giris_mm3=round(tb_c, 3), en_az=min(sat, key=lambda q: q[1]), temas_phi=[q[0] for q in sat if q[1] < 1e-6],
                        tambur_capb_en_az=min(ic, key=lambda q: q[1]), satir=sat)
    log("kayis", {k: v for k, v in OUT["kayis"].items() if k != "satir"})
    O.kaydet(JS, OUT)

O.kaydet(JS, OUT)
log("bitti %.0fs" % (time.time() - t0))
