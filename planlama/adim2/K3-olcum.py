# K3 (Y1b kontrol, 25 Ekim 2026): S1 kaseti duzeltmeleri K1-K6 bagimsiz olcum. Yalniz okur (FCStd gecici kopyadan).
# Tasarim ajaninin S1-duzeltme-kontrol.py'si KULLANILMAZ; K2 kontrol yardimcilari (K2-ortak, K2-u bagimsiz cozucu) kullanilir.
# Adimlar (K3_ADIM): ip | pah | cep | pim2 | duvarip | ev | montaj   -> K3-<adim>.json
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part

A, V, log, tasi = O.A, O.V, O.log, O.tasi
U = O.yukle("K2-u.py")
sys.path.insert(0, os.path.join(O.R, "dirsek"))
import kablo_yolu as KY
t0 = time.time()
ADIM = os.environ.get("K3_ADIM", "ip")
JS = "K3-%s.json" % ADIM
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"), adim=ADIM)
KK = A.KOL_KABLO
S1 = KK["s1"]
TB = S1["tambur"]
DU = S1["duvar"]
T = KK["serit"][1]
GEN = KK["serit"][0]
KAL = S1["serit"] * T
RI = TB["r"][1] + KAL / 2
RO = DU["r"][0] - KAL / 2
XC = 0.5 * sum(S1["kanal_x"])
L0 = S1["L"]

OMU = O.ac("omuz/omuz-montaj.FCStd", "K3")
KABT = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd", "K3"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd", "K3")


def sec(P, f):
    return [(p["ad"], p["shape"]) for p in P if f(p)]


GOV = sec(OMU, lambda p: p["grup"] == "Govde" and p["tur"] != "Referans")
GOB = sec(OMU, lambda p: p["grup"] == "Gobek")
IP = [(a, s) for a, s in GOB if a.startswith("S1 tambur baglama ipi")]
TAMBUR = [(a, s) for a, s in GOB if a == "S1 kablo tamburu"]
GOB_D = [(a, s) for a, s in GOB if a != "S1 kablo tamburu" and not a.startswith("S1 tambur baglama ipi")]
KOL = sec(OMU, lambda p: p["grup"] == "Kol") + sec(DIR, lambda p: p["grup"] == "UstKol")
KG = {p["ad"]: p["shape"] for p in KABT}
GOVDE, KAPAK = KG["S1 kaset govdesi sag"], KG["S1 kaset kapagi sag"]
KASET = sec(KABT, lambda p: p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi"))
KAB_D = sec(KABT, lambda p: not p["ad"].startswith("S1 kaset") and not p["ad"].startswith("Kaset civatasi"))
log("parca: omuz %d (ip %d), kabuk sag %d (kaset %d), dirsek %d, kol %d" % (len(OMU), len(IP), len(KABT), len(KASET), len(DIR), len(KOL)))
OUT["parca"] = dict(omuz=len(OMU), ip=[a for a, _ in IP], kabuk_sag=len(KABT), kaset=[a for a, _ in KASET], kol=[a for a, _ in KOL])


def hacim_ortak(a_list, b_list, esik=1e-3):
    out = []
    for a, s in a_list:
        for b, q in b_list:
            if s.BoundBox.intersect(q.BoundBox):
                v = s.common(q).Volume
                if v > esik:
                    out.append((a, b, round(v, 3)))
    return out


def psi_kutu(x0, x1, r0, r1, w, psi):
    """psi = 0 cercevesinde (radyal +Y, teget z) kutu, sonra -X etrafinda psi kadar dondurulur (tasarimla ayni kural)."""
    b = Part.makeBox(x1 - x0, r1 - r0, w, V(x0, r0, -w / 2))
    b.rotate(V(0, 0, 0), V(-1, 0, 0), psi)
    return b


def r_aralik(sh):
    rs = [math.hypot(v.Y, v.Z) for v in sh.Vertexes]
    return round(min(rs), 3), round(max(rs), 3)


def kaydet():
    O.kaydet(JS, OUT)


# =================================================================================================== K2: tambur baglama ipi
if ADIM == "ip":
    SAB = GOV + KASET + KAB_D
    # 1) ip geometrisi
    geo = []
    for a, s in IP:
        bb = s.BoundBox
        c = bb.Center
        geo.append(dict(ad=a, hacim=round(s.Volume, 4), x=[round(bb.XMin, 3), round(bb.XMax, 3)], r=r_aralik(s),
                        psi=round(O.yz_psi(c.y, c.z)[0], 2), kati=len(s.Solids)))
    OUT["ip_geo"] = geo
    OUT["ip_tambur_ortak"] = hacim_ortak(IP, TAMBUR, 1e-6)
    OUT["ip_gobek_diger_ortak"] = hacim_ortak(IP, GOB_D, 1e-6)
    d, a, b = O.enaz(IP, GOB_D, pay=3)
    OUT["ip_gobek_diger_enaz"] = (round(d, 3), a, b)
    # tambur ip yolu kesitleri: ring delikleri (x genislik), oluk derinligi, dudak cebi -> tamburdan dilimle
    tb = TAMBUR[0][1]
    yol = []
    for ps in TB["ip_psi"]:
        for x in (153.35, 153.6, 153.9, 155.9, 158.0, 158.3, 158.45):
            # psi yonunde radyal cizgi r 36,5...44: tambur icinde kalan parcalar
            p0, p1 = V(x, *O.psi_yz(ps, 36.5)), V(x, *O.psi_yz(ps, 44.5))
            ln = Part.makeLine(p0, p1)
            cm = ln.common(tb)
            segs = [(round(math.hypot(e.Vertexes[0].Y, e.Vertexes[0].Z), 2), round(math.hypot(e.Vertexes[-1].Y, e.Vertexes[-1].Z), 2))
                    for e in cm.Edges]
            yol.append(dict(psi=ps, x=x, tambur_dolu_r=sorted(tuple(sorted(q)) for q in segs)))
    OUT["ip_yolu_kesit"] = yol
    log("ip geo", geo, OUT["ip_tambur_ortak"], OUT["ip_gobek_diger_enaz"])
    # 2) ip <-> sabit, S1 -60...180 (1)
    sat = []
    for phi in np.arange(-60, 180.01, 1.0):
        d, a, b = O.enaz([(x, tasi(s, O.Pp(float(phi)))) for x, s in IP], SAB, pay=3)
        sat.append((float(phi), round(d, 3), a, b))
    ic = [q for q in sat if -45 <= q[0] <= 135]
    by = {}
    for q in sat:
        if q[3] not in by or q[1] < by[q[3]][0]:
            by[q[3]] = (q[1], q[0])
    OUT["ip_sabit"] = dict(en_az_aralik=min(ic, key=lambda q: q[1]), en_az_genis=min(sat, key=lambda q: q[1]),
                           parca_basina=sorted(((k,) + v for k, v in by.items()), key=lambda q: q[1])[:12], satir=sat)
    log("ip-sabit", OUT["ip_sabit"]["en_az_aralik"], OUT["ip_sabit"]["parca_basina"][:6], "%.0fs" % (time.time() - t0))
    kaydet()
    # 3) dugum modeli: 1,2 kup, demet ustunde (r 43,2...44,4), kanal ortasi; iki psi'de
    y_dm = TB["r"][1] + KAL
    DUG = [("dugum psi %.0f" % ps, psi_kutu(XC - 0.6, XC + 0.6, y_dm, y_dm + 1.2, 1.2, ps)) for ps in TB["ip_psi"]]
    sat = []
    for phi in np.arange(-60, 180.01, 1.0):
        d, a, b = O.enaz([(x, tasi(s, O.Pp(float(phi)))) for x, s in DUG], SAB, pay=3)
        sat.append((float(phi), round(d, 3), a, b))
    ic = [q for q in sat if -45 <= q[0] <= 135]
    OUT["dugum_sabit"] = dict(model="1,2 mm kup r %.1f...%.1f x %.1f...%.1f" % (y_dm, y_dm + 1.2, XC - 0.6, XC + 0.6),
                              en_az_aralik=min(ic, key=lambda q: q[1]), en_az_genis=min(sat, key=lambda q: q[1]))
    log("dugum-sabit", OUT["dugum_sabit"])
    # 4) ip + dugum <-> kol (gobek cercevesi, S2 0...120)
    sat = []
    for th in [0.0, 3.0, 4.0, 5.0] + [float(x) for x in np.arange(6, 120.01, 2.0)]:
        kol = [(a, tasi(s, O.Pr(th))) for a, s in KOL]
        d, a, b = O.enaz(IP + DUG, kol, pay=5)
        sat.append((th, round(d, 3), a, b))
    OUT["ip_kol"] = dict(en_az_aralik=min([q for q in sat if q[0] >= 5], key=lambda q: q[1]), satir=sat)
    log("ip-kol", OUT["ip_kol"]["en_az_aralik"])
    kaydet()
    # 5) ip/dugum <-> kablo yollari: S2 lopu (dirsek + bilek; K2-ek2 yontemi), gecis (G2 -> bag, son 8 mm haric), cikis (sabit)
    SL = KK["s2_lop"]
    R_C = math.hypot(GEN, 2 * T) / 2
    F, tF = V(*SL["F"]), V(*SL["F_teget"])
    onceki = None
    lop = []
    for th in [5.0, 6.0] + [float(x) for x in np.arange(9.0, 120.01, 3.0)]:
        pl = O.Pr(th)
        M, tM = pl.multVec(V(*SL["M"])), pl.Rotation.multVec(V(*SL["M_teget"]))
        a0, a1 = math.atan2(tM.y, tM.x), math.atan2(tF.y, tF.x)
        if onceki is None:
            ph, E, h, k = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150)
        else:
            k = round(((onceki[-1] - onceki[0]) + a0 - a1) / (2 * math.pi))
            ph, E, h, k = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150, th0=onceki, k=k)
        onceki = ph
        N = len(ph)
        ds = SL["L"] / N
        uv = np.vstack([[M.x, M.y], np.array([M.x, M.y]) + ds * np.cumsum(np.stack([np.cos(ph), np.sin(ph)], 1), 0)])
        s = np.linspace(0, 1, len(uv))
        s0 = 1.0 - SL["gecis"] / SL["L"]
        tt = np.clip((s - s0) / (1 - s0), 0, 1)
        w = M.z + (F.z - M.z) * tt * tt * (3 - 2 * tt)
        pts = [V(float(uv[i][0]), float(uv[i][1]), float(w[i])) for i in range(len(uv))]
        ken = Part.makePolygon(pts)
        d, a, b = O.enaz([("lop", ken)], IP + DUG, pay=20)
        lop.append((th, round(d - R_C, 3), b, round(h, 5)))
    OUT["ip_s2_lop"] = dict(r_cevrel=round(R_C, 3), en_az=min(lop, key=lambda q: q[1]), satir=lop)
    log("ip-S2 lopu", OUT["ip_s2_lop"]["en_az"])
    S1O = KY.s1_olcu(KK)
    DM = KY.demet(S1["serit"], KK["serit"])
    g1 = KY.s1_gecis(KK, S1O)
    ken_g8, _ = KY.cokgen(g1, 0.0, 8.0)
    d, a, b = O.enaz([("gecis", ken_g8)], IP + DUG, pay=20)
    OUT["ip_gecis"] = dict(bosluk=round(d - DM["r_sabit"], 3), parca=b, not_="gecis son 8 mm (bag, tasarim temasi) haric; yassi yari kalinlik")
    c1 = KY.s1_cikis(KK, S1O)
    ken_c, _ = KY.cokgen(c1, 0.0, 0.0)
    cik = []
    for phi in np.arange(-45, 135.01, 5.0):
        d, a, b = O.enaz([("cikis", ken_c)], [(x, tasi(s, O.Pp(float(phi)))) for x, s in IP + DUG], pay=20)
        cik.append((float(phi), round(d - DM["r_sabit"], 3), b))
    OUT["ip_cikis"] = min(cik, key=lambda q: q[1])
    log("ip-gecis", OUT["ip_gecis"], "ip-cikis", OUT["ip_cikis"])
    kaydet()
    # 6) dugum atma erisimi: dugum noktasindan radyal disari O4 sonda (r 45 -> 90, x XC), S2 90 ve 5; S1 -60...180 (15)
    er = []
    for th in (90.0, 5.0):
        for phi in np.arange(-60, 180.01, 15.0):
            hed = SAB + [(a, tasi(s, O.Pp(float(phi)).multiply(O.Pr(th)))) for a, s in KOL] + \
                  [(a, tasi(s, O.Pp(float(phi)))) for a, s in GOB_D]
            r_ = {}
            for ps in TB["ip_psi"]:
                pg = ps + float(phi)
                p0, p1 = V(XC, *O.psi_yz(pg, 45.0)), V(XC, *O.psi_yz(pg, 90.0))
                sonda = Part.makeCylinder(2.0, 45.0, p0, (p1 - p0).normalize())
                hv = sum(v for _, _, v in hacim_ortak([("sonda", sonda)], hed, 1e-3))
                d, _, b = O.enaz([("sonda", sonda)], hed, pay=2)
                r_[ps] = (round(hv, 2), round(d, 2), b)
            er.append(dict(S2=th, S1=float(phi), sonda=r_))
    OUT["dugum_erisim"] = dict(acik=[(q["S2"], q["S1"]) for q in er if all(v[0] == 0 for v in q["sonda"].values())], satir=er)
    log("dugum erisim acik", OUT["dugum_erisim"]["acik"])
    # 7) ip yolu baski: tambur baski yonu (omuz-baski.json)
    try:
        ob = json.load(open(os.path.join(O.R, "omuz", "omuz-baski.json"), encoding="utf-8"))
        OUT["tambur_baski"] = [q for q in (ob.get("parcalar") or ob.get("parca") or []) if "tambur" in json.dumps(q, ensure_ascii=False).lower()][:3]
    except Exception as e:
        OUT["tambur_baski"] = str(e)
    kaydet()

# =================================================================================================== K3: flans pahi + S2 lopu
if ADIM == "pah":
    # pah: kapak dilimleri, flans ic kenari yaricapi (kasetin icinde, psi 200...320)
    pah = {}
    for x in (158.32, 158.6, 158.9, 159.2, 159.48):
        rmin = 1e9
        for w in KAPAK.slice(V(1, 0, 0), x):
            for e in w.Edges:
                for p in e.discretize(200):
                    ps, r = O.yz_psi(p.y, p.z)
                    if 200 <= ps <= 320:
                        rmin = min(rmin, r)
        pah["x %.2f" % x] = round(rmin, 3)
    OUT["pah_ic_r"] = pah
    log("pah", pah)
    SL = KK["s2_lop"]
    R_C = math.hypot(GEN, 2 * T) / 2
    F, tF = V(*SL["F"]), V(*SL["F_teget"])
    THS = [5.0, 6.0] + [float(x) for x in np.arange(9.0, 114.01, 3.0)] + [115.0, 116.0, 117.0, 118.0, 119.0, 120.0]
    onceki, LOPS = None, {}
    for th in THS:
        pl = O.Pr(th)
        M, tM = pl.multVec(V(*SL["M"])), pl.Rotation.multVec(V(*SL["M_teget"]))
        a0, a1 = math.atan2(tM.y, tM.x), math.atan2(tF.y, tF.x)
        if onceki is None:
            ph, E, h, k = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150)
        else:
            k = round(((onceki[-1] - onceki[0]) + a0 - a1) / (2 * math.pi))
            ph, E, h, k = U.serbest((M.x, M.y), a0, (F.x, F.y), a1, SL["L"], N=150, th0=onceki, k=k)
        onceki = ph
        LOPS[th] = (M, ph, h)
    sat = []
    for th in [t for t in THS if t >= 99]:
        M, ph, h = LOPS[th]
        N = len(ph)
        ds = SL["L"] / N
        uv = np.vstack([[M.x, M.y], np.array([M.x, M.y]) + ds * np.cumsum(np.stack([np.cos(ph), np.sin(ph)], 1), 0)])
        s = np.linspace(0, 1, len(uv))
        s0 = 1.0 - SL["gecis"] / SL["L"]
        tt = np.clip((s - s0) / (1 - s0), 0, 1)
        w = M.z + (F.z - M.z) * tt * tt * (3 - 2 * tt)
        pts = [V(float(uv[i][0]), float(uv[i][1]), float(w[i])) for i in range(len(uv))]
        uz = np.cumsum([0] + [(b - a).Length for a, b in zip(pts[:-1], pts[1:])])
        keep = [i for i in range(len(pts)) if 4.0 <= uz[i] <= uz[-1] - 4.0]
        ken = Part.makePolygon([pts[i] for i in keep])
        for phi in (100.0, 110.0, 115.0, 118.0, 119.0, 119.5, 120.0, 122.5, 125.0, 130.0, 135.0):
            kf = tasi(ken, O.Pp(phi))
            best = (1e9, None, None)
            for a, sh in KASET:
                dd, pp, info = sh.distToShape(kf)
                if dd < best[0]:
                    best = (dd, a, pp[0])
            d, a, (p_sh, p_k) = best
            inv = O.Pp(phi).inverse()
            pk, ps_ = inv.multVec(p_k), inv.multVec(p_sh)
            j = int(np.argmin([(pts[i] - pk).Length for i in keep]))
            i = keep[j]
            tg = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
            tg.normalize()
            ez = V(0, 0, 1)
            n = tg.cross(ez)
            n.normalize()
            u = ps_ - pk
            if u.Length > 1e-9:
                u.normalize()
            destek = abs(u.dot(n)) * T + abs(u.dot(ez)) * GEN / 2
            izinli = (phi < 120.0 and th <= 120.0) or (phi >= 120.0 and th <= 117.0)
            sat.append(dict(S2=th, S1=phi, d=round(d, 3), cevrel=round(d - R_C, 3), dikdortgen=round(d - destek, 3), parca=a,
                            izinli=izinli, cozum_hata=round(h, 6)))
        log("S2", th, [(q["S1"], q["cevrel"]) for q in sat if q["S2"] == th], "%.0fs" % (time.time() - t0))
    iz = [q for q in sat if q["izinli"]]
    yas = [q for q in sat if not q["izinli"]]
    OUT["s2_lop_flans"] = dict(r_cevrel=round(R_C, 3),
                               izinli_en_az_cevrel=min(iz, key=lambda q: q["cevrel"]), izinli_en_az_dikdortgen=min(iz, key=lambda q: q["dikdortgen"]),
                               yasak_en_az_cevrel=min(yas, key=lambda q: q["cevrel"]), yasak_en_az_dikdortgen=min(yas, key=lambda q: q["dikdortgen"]),
                               satir=sat)
    log({k: v for k, v in OUT["s2_lop_flans"].items() if k != "satir"})
    kaydet()

# =================================================================================================== K4: U cebi
if ADIM == "cep":
    S1O = KY.s1_olcu(KK)

    def taban_kur(u_pay):
        """kabuk_parcalar ile ayni kural (yalniz yz duzlemi): duvar seridi (taban - 2 mm ic offset), u_pay degistirilerek."""
        S1U = KY.s1_poz(KK, A.OMUZ["one_arka_aralik"][1], S1O)
        psi_a = S1U["psi_U"] + S1O["U"]["delta"]

        def yz(psi, r):
            y, z = KY.psi_yz(psi, r)
            return V(0, y, z)

        def yay(r0, r1, p0, p1, adim=1.0):
            n = max(2, int(abs(p1 - p0) / adim) + 1)
            dis = [yz(p0 + (p1 - p0) * i / n, r1) for i in range(n + 1)]
            ic = [yz(p1 - (p1 - p0) * i / n, r0) for i in range(n + 1)]
            return Part.Face(Part.makePolygon(dis + ic + [dis[0]]))

        def daire(r, m=V(0, 0, 0)):
            return Part.Face(Part.Wire(Part.makeCircle(r, m, V(1, 0, 0))))
        dil = yay(DU["flans_r_ic"], DU["r"][1], DU["psi0"], psi_a)
        u_ = [V(0, q.y, q.z) for q in S1U["u_nokta"]]
        uy = Part.Face(Part.Wire(Part.makePolygon(u_ + [u_[0]]))).makeOffset2D(u_pay, 0)
        pm = DU["pim"]
        u2 = [(q.y, q.z) for q in S1U["u_nokta"]]
        pp = S1U["u_uc_psi"]
        while True:
            c = KY.psi_yz(pp, pm["r"])
            if min(math.hypot(c[0] - a_, c[1] - b_) for a_, b_ in u2) >= S1O["kalinlik"] / 2 + pm["bosluk"] + pm["post_r"] + 0.5:
                break
            pp += 0.5
        tb = dil.fuse([uy, daire(pm["post_r"] + 2.0, yz(pp, pm["r"]))])
        tb = tb.common(daire(DU["r"][1]).cut(daire(DU["flans_r_ic"]))).removeSplitter().Faces[0]
        ic = tb.makeOffset2D(-2.0, 0)
        ser = tb.cut(ic).cut(daire(DU["ic_kes_r"]))
        ser.translate(V(XC, 0, 0))
        tb2 = tb.copy()
        tb2.translate(V(XC, 0, 0))
        ps_all = [O.yz_psi(v.Y, v.Z)[0] for v in tb.Vertexes]
        return dict(serit=ser, taban=tb2, pim_psi=pp, psi_a=psi_a,
                    y_max=round(tb.BoundBox.YMax, 2), z_max=round(tb.BoundBox.ZMax, 2), z_min=round(tb.BoundBox.ZMin, 2),
                    alan=round(tb.Area, 1), serit_alan=round(ser.Area, 1))
    TBN = {up: taban_kur(up) for up in (4.5, 6.5, 7.0, 7.5)}
    OUT["taban"] = {str(k): {kk: v for kk, v in d.items() if kk not in ("serit", "taban")} for k, d in TBN.items()}
    log("taban", OUT["taban"])
    # dogrulama: 6,5 yeniden kurulumu FCStd govde dilimiyle (x XC) ayni mi
    gs = GOVDE.slice(V(1, 0, 0), XC)
    big = max(gs, key=lambda w: w.BoundBox.DiagonalLength)
    sap = []
    for p in big.discretize(400):
        ps, r = O.yz_psi(p.y, p.z)
        if 280 <= ps <= 345 and 50 <= r <= 77.0:            # U cebi bolgesi
            sap.append(TBN[6.5]["serit"].distToShape(Part.Vertex(p))[0])
    OUT["yeniden_kurulum_sapma_6_5"] = dict(n=len(sap), en_buyuk=round(max(sap), 4) if sap else None)
    log("yeniden kurulum sapma", OUT["yeniden_kurulum_sapma_6_5"])
    TEL = []
    for xk in (154.0, XC, 157.9):
        for a in ("S1 kaset govdesi sag", "S1 kaset kapagi sag"):
            s = KG[a]
            if s.BoundBox.XMin <= xk <= s.BoundBox.XMax:
                for w in s.slice(V(1, 0, 0), xk):
                    c = w.BoundBox.Center
                    TEL.append((xk, a, w, w.BoundBox.DiagonalLength, O.yz_psi(c.y, c.z)))

    def olc(phi, L=L0, psi_w=None, psi_d0=None):
        c = U.coz(RI, RO, (TB["bag_psi"] if psi_d0 is None else psi_d0) + phi, S1["bag_duvar_psi"] if psi_w is None else psi_w, L, N=240)
        oz = U.ozet(c)
        P2 = c["P"]
        k = np.abs(c["k"])
        jm = int(np.argmax(k))
        pos = np.where(c["k"][:jm] >= 0)[0]
        i_inf = int(pos.max()) + 1 if len(pos) else 0
        dis = np.where(c["do"][jm + 1:] < 0.02)[0]
        i_dis = jm + 1 + int(dis.min()) if len(dis) else len(P2) - 1
        n5 = int(5.0 / c["ds"])
        Ub = P2[i_inf:max(i_inf + 2, i_dis - n5)]
        r = dict(phi=phi, dL=round(L - L0, 2), R_min=round(oz["R_min"], 3), u_uc_psi=round(oz["u_uc_psi"], 2), a_ic=round(oz["a_ic"], 2),
                 a_dis=round(oz["a_dis"], 2), ic_kalkma=round(oz["ic_kalkma"], 3), hata=oz["hata"], ihlal=oz["ihlal"])
        ub = {xk: Part.makePolygon([V(xk, q[0], -q[1]) for q in Ub]) for xk in (154.0, XC, 157.9)}
        for xk, a, w, dg, pr in TEL:
            if dg > 60:
                d = w.distToShape(ub[xk])[0] - KAL / 2
                if "U_duvar" not in r or d < r["U_duvar"]:
                    r["U_duvar"] = round(d, 3)
            else:
                d = w.distToShape(Part.makePolygon([V(xk, q[0], -q[1]) for q in P2]))[0] - KAL / 2
                key = "kucuk_psi%.0f" % pr[0]
                if key not in r or d < r[key]:
                    r[key] = round(d, 3)
        for up in (6.5, 7.0, 7.5):
            r["U_cep_%.1f" % up] = round(TBN[up]["serit"].distToShape(ub[XC])[0] - KAL / 2, 3)
        return r, c
    sat = []
    for phi in [135.0, 136.0, 137.0, 138.0, 138.5, 139.0, 139.5, 140.0, 141.0, 142.0]:
        sat.append(olc(phi)[0])
        log(sat[-1], "%.0fs" % (time.time() - t0))
    OUT["cep_phi"] = sat
    kaydet()
    sat = []
    for dL in (-5.0, -2.0, 0.0, 1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0):
        sat.append(olc(135.0, L0 + dL)[0])
        log(sat[-1])
    for dL in (-5.0, 0.0):
        sat.append(olc(-45.0, L0 + dL)[0])
        log(sat[-1])
    OUT["cep_L"] = sat
    kaydet()
    # birlesik: L +2 ile S1 asimi
    sat = []
    for phi in (136.0, 137.0, 138.0):
        for dL in (1.0, 2.0):
            sat.append(olc(phi, L0 + dL)[0])
            log(sat[-1])
    OUT["cep_birlesik"] = sat
    # ip konumlari etkisi: tambur ip psi_g 156 ve duvar ip 230 temas bolgesinde mi (kalkma 0 mi)
    ipk = []
    for phi in (-45.0, -30.0, 0.0, 45.0, 90.0, 135.0):
        r, c = olc(phi)
        pu = np.degrees(np.unwrap(np.radians(c["psi"])))
        ps_g = pu - phi
        rec = dict(phi=phi)
        for ps in TB["ip_psi"]:
            i = int(np.argmin(np.abs(ps_g - ps)))
            rec["tambur_ip_%.0f_kalkma" % ps] = round(float(c["di"][i]), 3)
        for ps in DU["ip_psi"]:
            i = int(np.argmin(np.abs((pu % 360) - ps) + (np.arange(len(pu)) < len(pu) // 2) * 1e3))
            rec["duvar_ip_%.1f_kalkma" % ps] = round(float(c["do"][i]), 3)
        rec["a_ic"], rec["a_dis"] = r["a_ic"], r["a_dis"]
        ipk.append(rec)
        log("ip temas", rec)
    OUT["ip_temas"] = ipk
    kaydet()

# =================================================================================================== ikinci pim + kulak
if ADIM == "pim2":
    P2 = DU["pim2"]
    c2 = V(0, *O.psi_yz(P2["psi"], P2["r"]))
    # kulak bolgesi: psi 300 +- 8, r 75,6...84, x 151...160
    def sektor(r0, r1, x0, x1, p0, p1, n=40):
        dis = [V(x0, *O.psi_yz(p0 + (p1 - p0) * i / n, r1)) for i in range(n + 1)]
        ic = [V(x0, *O.psi_yz(p1 - (p1 - p0) * i / n, r0)) for i in range(n + 1)]
        return Part.Face(Part.makePolygon(dis + ic + [dis[0]])).extrude(V(x1 - x0, 0, 0))
    KB = sektor(DU["r"][1] + 0.01, 85.0, 150.0, 161.0, P2["psi"] - 8, P2["psi"] + 8)
    KUL = [("govde kulak", GOVDE.common(KB)), ("kapak kulak", KAPAK.common(KB))]
    OUT["kulak"] = {a: dict(hacim=round(s.Volume, 2), x=[round(s.BoundBox.XMin, 2), round(s.BoundBox.XMax, 2)], r=r_aralik(s)) for a, s in KUL}
    OUT["govde_kapak_ortak"] = round(GOVDE.common(KAPAK).Volume, 4)
    gk = GOVDE.common(KAPAK)
    OUT["govde_kapak_ortak_x"] = [round(gk.BoundBox.XMin, 3), round(gk.BoundBox.XMax, 3)] if gk.Volume > 0 else None
    OUT["kaset_kabuk_ortak"] = hacim_ortak([("govde", GOVDE), ("kapak", KAPAK)], KAB_D, 1e-4)
    OUT["kulak_kabuk_enaz"] = O.enaz(KUL, KAB_D, pay=5)[:3]
    # pim / delik
    pim = Part.makeCylinder(P2["d"] / 2 - 0.01, 2.9, V(DU["flans_x"][0] - 2.95, c2.y, c2.z), V(1, 0, 0))
    OUT["pim_kapakta"] = round(pim.common(KAPAK).Volume / pim.Volume, 4)
    delik = Part.makeCylinder(P2["d"] / 2 + 0.05, 3.0, V(DU["flans_x"][0] - 3.05, c2.y, c2.z), V(1, 0, 0))
    OUT["delik_govdede_bos"] = round(delik.common(GOVDE).Volume, 4)
    et = Part.makeCylinder(P2["post_r"] - 0.05, 3.0, V(DU["flans_x"][0] - 3.05, c2.y, c2.z), V(1, 0, 0)).cut(
        Part.makeCylinder(P2["d"] / 2 + 0.15, 3.0, V(DU["flans_x"][0] - 3.05, c2.y, c2.z), V(1, 0, 0)))
    OUT["delik_cevre_et_dolu"] = round(et.common(GOVDE).Volume / et.Volume, 4)
    OUT["delik_ic_r"] = round(P2["r"] - P2["d"] / 2 - 0.1, 3)
    log({k: v for k, v in OUT.items() if k not in ("parca",)})
    kaydet()
    # kulak <-> kol: S1 -45...135 (2,5) x S2 (5...30 / 2,5; 45...120 / 15); kol cercevesine kulak
    sat = []
    for phi in np.arange(-45, 135.01, 2.5):
        for th in [5.0, 7.5, 10.0, 12.5, 15.0, 20.0, 25.0, 30.0, 45.0, 60.0, 75.0, 90.0, 105.0, 120.0]:
            inv = O.Pp(float(phi)).multiply(O.Pr(th)).inverse()
            d, a, b = O.enaz([(x, tasi(s, inv)) for x, s in KUL], KOL, pay=5)
            sat.append((float(phi), th, round(d, 3), a, b))
    OUT["kulak_kol"] = dict(en_az=sorted(sat, key=lambda q: q[2])[:8], poz=len(sat))
    log("kulak-kol", OUT["kulak_kol"]["en_az"][:3], "%.0fs" % (time.time() - t0))
    # kulak <-> gobek (S1 -60...180)
    sat = []
    for phi in np.arange(-60, 180.01, 2.0):
        d, a, b = O.enaz(KUL, [(x, tasi(s, O.Pp(float(phi)))) for x, s in GOB], pay=5)
        sat.append((float(phi), round(d, 3), a, b))
    OUT["kulak_gobek"] = min(sat, key=lambda q: q[1])
    log("kulak-gobek", OUT["kulak_gobek"])
    kaydet()

# =================================================================================================== duvar bagi ipi
if ADIM == "duvarip":
    I = DU["ip"]
    sat = []
    for ps in DU["ip_psi"]:
        rec = dict(psi=ps)
        for ad_, x in (("arka", 0.5 * sum(I["arka_x"])), ("ust", 0.5 * (I["ust_x"][0] + DU["flans_x"][0]))):
            for r in (75.4, 76.2, 77.0):
                p = V(x, *O.psi_yz(ps, r))
                rec["%s r%.1f bos" % (ad_, r)] = not GOVDE.isInside(p, 1e-4, True)
            for dps in (-1.5, 1.5):
                p = V(x, *O.psi_yz(ps + dps, 76.2))
                rec["%s psi%+.1f duvar" % (ad_, dps)] = GOVDE.isInside(p, 1e-4, True)
        # duvar disi: r 77,2 -> 82 sonda (x 153,4 ve 157,9), kabuk / kapak / kol (S1 0, S2 5 ev) en yakin
        for x in (153.4, 157.9):
            p0 = V(x, *O.psi_yz(ps, 77.25))
            d, _, b = O.enaz([("p", Part.Vertex(p0))], KAB_D + [("kapak", KAPAK)], pay=10)
            rec["dis x%.1f en_yakin" % x] = (round(d, 3), b)
        # erisim: duvar disindan radyal O4 sonda (r 77,4 -> 110) x 155,9 / 157,5; kabuk + kapak ortak hacmi ve en yakin
        for x in (153.6, 155.9, 157.5):
            p0, p1 = V(x, *O.psi_yz(ps, 77.4)), V(x, *O.psi_yz(ps, 110.0))
            sonda = Part.makeCylinder(2.0, 32.6, p0, (p1 - p0).normalize())
            rec["sonda x%.1f ortak" % x] = hacim_ortak([("sonda", sonda)], KAB_D, 1e-3)
            rec["sonda x%.1f en_yakin" % x] = O.enaz([("sonda", sonda)], KAB_D, pay=3)[:3]
            rec["radyal bosluk x%.1f" % x] = O.enaz([("p", Part.Vertex(p0))], KAB_D, pay=10)[:3]
        sat.append(rec)
        log(rec)
    OUT["delik"] = sat
    # ip ilmegi modeli (psi = 0 cercevesi): dis (r 77,2...77,6) / ic (demet ici yuzu r 70,6...71,0) / -x radyal (x 153,2...153,6) /
    # +x radyal (x 157,9...158,3 centikte); demet r 71,0...75,2 x 153,8...158,0 (kanal ortasi XC +- 2,1)
    d_ = 0.4
    xa0, xa1 = 153.2, 153.6
    xu0, xu1 = DU["flans_x"][0] - d_, DU["flans_x"][0]
    r_ic = DU["r"][0] - KAL
    seg = [(xa0, xu1, DU["r"][1], DU["r"][1] + d_), (xa0, xu1, r_ic - d_, r_ic), (xa0, xa1, r_ic - d_, DU["r"][1] + d_),
           (xu0, xu1, r_ic - d_, DU["r"][1] + d_)]
    ILM, DEM = [], []
    for ps in DU["ip_psi"]:
        s_ = None
        for (x0, x1, r0, r1) in seg:
            b = psi_kutu(x0, x1, r0, r1, d_, ps)
            s_ = b if s_ is None else s_.fuse(b)
        ILM.append(("duvar ipi %.1f" % ps, s_.removeSplitter()))
        DEM.append(("demet %.1f" % ps, psi_kutu(XC - GEN / 2, XC + GEN / 2, r_ic, DU["r"][0], 3.0, ps)))
    OUT["ilmek_ortak"] = dict(govde=hacim_ortak(ILM, [("govde", GOVDE)], 1e-4), kapak=hacim_ortak(ILM, [("kapak", KAPAK)], 1e-4),
                              kabuk=hacim_ortak(ILM, KAB_D, 1e-4), demet=hacim_ortak(ILM, DEM, 1e-4))
    OUT["ilmek_enaz"] = dict(kapak=O.enaz(ILM, [("kapak", KAPAK)], pay=3)[:3], kabuk=O.enaz(ILM, KAB_D, pay=5)[:3])
    OUT["eksenel_pay"] = dict(arka_plaka_demet=round(XC - GEN / 2 - (DU["x0"] + DU["arka_t"]), 3), demet_flans=round(DU["flans_x"][0] - XC - GEN / 2, 3),
                              ip_ihtiyac=2 * d_, toplam=round(DU["flans_x"][0] - (DU["x0"] + DU["arka_t"]) - GEN, 3))
    log("ilmek", OUT["ilmek_ortak"], OUT["ilmek_enaz"], OUT["eksenel_pay"])
    # ilmek <-> hareketli (gobek + kol), S1 -60...180 / S2 5, 30, 90
    sat = []
    for th in (5.0, 30.0, 90.0):
        for phi in np.arange(-60, 180.01, 5.0):
            hed = [(a, tasi(s, O.Pp(float(phi)))) for a, s in GOB] + [(a, tasi(s, O.Pp(float(phi)).multiply(O.Pr(th)))) for a, s in KOL]
            d, a, b = O.enaz(ILM, hed, pay=5)
            sat.append((th, float(phi), round(d, 3), a, b))
    OUT["ilmek_hareketli"] = min(sat, key=lambda q: q[2])
    log("ilmek-hareketli", OUT["ilmek_hareketli"])
    kaydet()

# =================================================================================================== K6 ev pozu (bagimsiz)
if ADIM == "ev":
    KOLZ = sec(OMU, lambda p: p["grup"] == "Kol") + sec(DIR, lambda p: p["grup"] in ("UstKol", "OnKol", "El"))
    D = A.DIRSEK
    SAB = GOB + GOV + KASET + KAB_D
    sat = []
    for th in (0.0, 3.0, 3.5, 3.75, 4.0, 5.0, 6.0):
        kol = [(a, tasi(s, O.Pr(th))) for a, s in KOLZ]
        cak = hacim_ortak(kol, SAB, 1e-3)
        d, a, b = O.enaz(kol, [(x, s) for x, s in SAB if not x.startswith("S2 servo")], pay=3)
        sat.append(dict(S2=th, cakisma=cak, en_kucuk_servo_haric=(round(d, 3), a, b)))
        log(sat[-1], "%.0fs" % (time.time() - t0))
    OUT["ev_125"] = sat
    kaydet()

# =================================================================================================== K5 radyal montaj
if ADIM == "montaj":
    def hareketli(phi, th):
        return [(a, tasi(s, O.Pp(phi))) for a, s in GOB] + [(a, tasi(s, O.Pp(phi).multiply(O.Pr(th)))) for a, s in KOL]

    def kes(sh, hed, esik=1e-3):
        bb = App.BoundBox(sh.BoundBox)
        bb.enlarge(0.5)
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

    def psi_ort(sh):
        ps = np.radians([O.yz_psi(v.Y, v.Z)[0] for v in sh.Vertexes])
        return math.degrees(math.atan2(np.sin(ps).mean(), np.cos(ps).mean())) % 360
    rad = []
    for ad_, sh, x_of, ek in (("govde", GOVDE, 0.0, []), ("kapak", KAPAK, 3.3, [("govde", GOVDE)]), ("kapak", KAPAK, 3.5, [("govde", GOVDE)])):
        pm = psi_ort(sh)
        for dps in (0.0, -15.0, 15.0):
            dy, dz = O.psi_yz(pm + dps, 1.0)
            dvec = V(0, dy, dz)
            for phi, th in ((-45.0, 90.0), (-20.0, 90.0), (0.0, 90.0), (-45.0, 5.0), (0.0, 30.0)):
                hed = KAB_D + ek + hareketli(phi, th)
                yol = []
                for s in [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 40.0, 50.0, 70.0, 90.0]:
                    q = sh.copy()
                    q.translate(V(x_of, 0, 0) + dvec * s)
                    vol, en = kes(q, hed)
                    yol.append((s, en[0], en[1], vol))
                rad.append(dict(parca=ad_, x_ofset=x_of, yon_psi=round(pm + dps, 1), S1=phi, S2=th, cakisan=[q for q in yol if q[3]],
                                en_kucuk=min((q[1], q[0], q[2]) for q in yol)))
                log(ad_, x_of, round(pm + dps, 1), phi, th, "cakisan", [(q[0], q[3]) for q in yol if q[3]][:3], "%.0fs" % (time.time() - t0))
            OUT["radyal"] = rad
            kaydet()
    son = []
    for phi, th in ((-45.0, 90.0), (-20.0, 90.0), (0.0, 90.0), (0.0, 30.0)):
        hed = [("govde", GOVDE)] + hareketli(phi, th) + KAB_D
        for t in (3.5, 3.0, 2.0, 1.0, 0.5, 0.0):
            q = KAPAK.copy()
            q.translate(V(t, 0, 0))
            vol, en = kes(q, hed)
            son.append((phi, th, t, en, vol))
    OUT["kapak_eksenel_son"] = son
    log("eksenel son", [q for q in son if q[4]])
    kaydet()

kaydet()
log("bitti %.0fs" % (time.time() - t0))
