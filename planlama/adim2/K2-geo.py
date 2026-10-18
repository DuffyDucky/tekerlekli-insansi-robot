# K2 kontrolu 2: geometri, taramalar, civata / isil gomme, baski cikintisi, montaj erisimi, kutle + tork. Yalniz okur (FCStd gecici
# kopya). K2_ADIM = tambur | kaset_kol | gobek | civata | baski | montaj | tork (bos: hepsi). Cikti: K2-geo-<adim>.json
# Calistir: K2_ADIM=<adim> FC_SCRIPT=<bu dosya> "$LOCALAPPDATA/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
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
JS = "K2-geo-%s.json" % ADIM
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"), adim=ADIM)


def calis(ad):
    return ADIM in ("hepsi", ad)


OMU = O.ac("omuz/omuz-montaj.FCStd")
KABG = O.ac("kabuk/kabuk-montaj.FCStd")
KAB = O.kabuk_yerel(KABG)
DIR = O.ac("dirsek/dirsek-montaj.FCStd")
log("acildi %.1fs" % (time.time() - t0))


def sec(P, kosul):
    return [(p["ad"], p["shape"]) for p in P if kosul(p)]


GOV = sec(OMU, lambda p: p["grup"] == "Govde" and p["tur"] != "Referans")
GOB = sec(OMU, lambda p: p["grup"] == "Gobek")
TAMBUR = [s for a, s in GOB if a == "S1 kablo tamburu"][0]
KOL = sec(OMU, lambda p: p["grup"] == "Kol") + sec(DIR, lambda p: p["grup"] == "UstKol")
ONK = sec(DIR, lambda p: p["grup"] in ("OnKol", "El"))
KASET = sec(KAB, lambda p: p["ad"].startswith("S1 kaset") or p["ad"].startswith("Kaset civatasi"))
BANT = sec(KAB, lambda p: p["ad"].startswith("Omuz bandi") or p["ad"].startswith("Gogus bandi") or "S1 kaseti" in p["ad"])
KG = dict(KASET)
S1 = A.KOL_KABLO["s1"]
CAPB = [(a, s) for a, s in GOV if a.startswith("Kapak civatasi")]


def nokta_bulutu(sh, defl=0.1):
    P = []
    for f in sh.Faces:
        try:
            pts, _ = f.tessellate(defl)
            P += [(p.x, p.y, p.z) for p in pts]
        except Exception:
            pass
    for e in sh.Edges:
        try:
            P += [(p.x, p.y, p.z) for p in e.discretize(Deflection=0.02)]
        except Exception:
            pass
    return np.array(P)


def kaydet():
    OUT["sure_s"] = round(time.time() - t0, 1)
    O.kaydet(JS, OUT)


# ============================================================ tambur, kaset olculeri, tambur taramalari
if calis("tambur"):
    T = {}
    # C halka kapsami: x 155,9, r 38'de psi orneklemesi (gobek cercevesi = S1 0)
    xc = 0.5 * sum(S1["kanal_x"])
    dolu = []
    for i in range(720):
        ps = i * 0.5
        y, z = O.psi_yz(ps, 38.0)
        dolu.append(TAMBUR.isInside(V(xc, y, z), 1e-4, True))
    dolu = np.array(dolu)
    bos = [i * 0.5 for i in range(720) if not dolu[i]]
    # bos yay(lar)i
    T["halka_bos_psi"] = [min(bos), max(bos)] if bos else None
    T["halka_dolu_oran"] = float(dolu.mean())
    # yaricaplar
    PB = nokta_bulutu(TAMBUR, 0.05)
    r = np.hypot(PB[:, 1], PB[:, 2])
    T["tambur_x"] = [float(PB[:, 0].min()), float(PB[:, 0].max())]
    T["tambur_r_max"] = float(r.max())
    m = (PB[:, 0] > 154.0) & (PB[:, 0] < 157.8)
    rr = r[m]
    T["halka_r_ic_kanal_bolgesi"] = float(rr[rr > 36.0].min())
    T["halka_r_dis_kanal_bolgesi"] = float(rr[rr < 40.5].max())
    md = (PB[:, 0] < 153.6)
    T["dudak_eksi_x"] = [float(PB[md, 0].min()), float(PB[md, 0].max()), float(r[md].max())]
    mp = (PB[:, 0] > 158.2) & (r > 37.5)
    T["dudak_arti_x"] = [float(PB[mp, 0].min()), float(PB[mp, 0].max()), float(r[mp].max())]
    # kapak civata baslari (sabit)
    cb = []
    for a, s in CAPB:
        Q = nokta_bulutu(s, 0.05)
        rq = np.hypot(Q[:, 1], Q[:, 2])
        cb.append(dict(ad=a, x_max=float(Q[:, 0].max()), r_min=float(rq.min()), r_max=float(rq.max()),
                       psi=O.yz_psi(float(Q[:, 1].mean()), float(Q[:, 2].mean()))[0]))
    T["kapak_civata"] = cb
    # tambur <-> sabit (kapak civatasi, rulman kapagi, govde, bant, kaset) S1 -60...180
    sat = []
    SABIT = GOV + BANT + KASET
    for phi in np.arange(-60, 180.01, 2.5):
        tb = tasi(TAMBUR, O.Pp(float(phi)))
        d, _, b = O.enaz([("t", tb)], SABIT, pay=5)
        dc, _, bc = O.enaz([("t", tb)], CAPB, pay=5)
        sat.append((float(phi), round(d, 3), b, round(dc, 3), bc))
    T["tambur_sabit"] = sat
    ic = [q for q in sat if -45 <= q[0] <= 135]
    T["tambur_sabit_min_aralik"] = min(ic, key=lambda q: q[1])
    T["tambur_civata_min_aralik"] = min(ic, key=lambda q: q[3])
    T["tambur_sabit_min_geometri"] = min(sat, key=lambda q: q[1])
    log("tambur sabit min", T["tambur_sabit_min_aralik"], T["tambur_civata_min_aralik"])
    # tambur <-> kol (yalniz S2'ye bagli)
    tk = []
    for th in [0.0, 2.0, 3.0, 3.5, 3.8, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 10.0] + list(np.arange(12.5, 120.01, 2.5)):
        kz = [(a, tasi(s, O.Pr(float(th)))) for a, s in KOL]
        d, _, b = O.enaz([("t", TAMBUR)], kz, pay=5)
        h = 0.0
        if d < 1e-6:
            h = sum(TAMBUR.common(s).Volume for a, s in kz if s.BoundBox.intersect(TAMBUR.BoundBox))
        tk.append((float(th), round(d, 3), b, round(h, 2)))
    T["tambur_kol"] = tk
    T["tambur_kol_min_aralik"] = min([q for q in tk if q[0] >= A.OMUZ["yana_aralik"][0]], key=lambda q: q[1])
    log("tambur kol", tk[:12])
    # kaset olculeri
    gv = KG["S1 kaset govdesi sag"]
    kp = KG["S1 kaset kapagi sag"]
    K = {}
    for ad_, s in (("govde", gv), ("kapak", kp)):
        Q = nokta_bulutu(s, 0.1)
        rq = np.hypot(Q[:, 1], Q[:, 2])
        pq = np.degrees(np.arctan2(-Q[:, 2], Q[:, 1])) % 360
        K[ad_] = dict(x=[float(Q[:, 0].min()), float(Q[:, 0].max())], r=[float(rq.min()), float(rq.max())],
                      psi=[float(pq.min()), float(pq.max())], y_max=float(Q[:, 1].max()), z=[float(Q[:, 2].min()), float(Q[:, 2].max())],
                      hacim=round(s.Volume, 1), bb=[round(v, 2) for v in (s.BoundBox.XMin, s.BoundBox.XMax, s.BoundBox.YMin, s.BoundBox.YMax,
                                                                           s.BoundBox.ZMin, s.BoundBox.ZMax)])
    # duvar yaricapi: psi isinlari x 155,9
    duv = []
    for ps in range(185, 345):
        y, z = O.psi_yz(ps, 1.0)
        ray = Part.makeLine(V(xc, 0, 0), V(xc, 90 * y, 90 * z))
        c = gv.common(ray)
        seg = []
        for e in c.Edges:
            a_ = [math.hypot(v.Point.y, v.Point.z) for v in e.Vertexes]
            seg.append((round(min(a_), 2), round(max(a_), 2)))
        if seg:
            duv.append((ps, sorted(seg)))
    K["duvar_isin"] = duv
    dis = [s_[-1] for _, s_ in duv if s_]
    K["duvar_dis_segment_r"] = [min(q[0] for q in dis), max(q[1] for q in dis)] if dis else None
    # kabuk omuz bandinin yerel ust siniri (x 140...152) ve kasetin onun ustundeki kismi
    bant = [s for a, s in BANT if a.startswith("Omuz bandi")][0]
    Qb = nokta_bulutu(bant.common(Part.makeBox(30, 300, 400, V(125, -150, -200))), 0.3)
    K["bant_y_max_x125_155"] = float(Qb[:, 1].max()) if len(Qb) else None
    Qg = nokta_bulutu(gv, 0.2)
    K["kaset_y_max"] = float(Qg[:, 1].max())
    K["kasetin_bant_ustu_mm"] = K["kaset_y_max"] - K["bant_y_max_x125_155"] if len(Qb) else None
    # kabuga yaslanan arka yuz: gv x=152 yuzunun bant x 152 duz yuzuyle ortusen alani
    arka = [f for f in gv.Faces if "Plane" in f.Surface.TypeId and abs(f.CenterOfMass.x - 152.0) < 0.01]
    if arka:
        fa = arka[0]
        ort = fa.extrude(V(-0.3, 0, 0)).common(bant)
        K["arka_yuz_alan"] = round(fa.Area, 1)
        K["arka_yuz_banta_dayanan_alan"] = round(ort.Volume / 0.3, 1)
    OUT["tambur"] = T
    OUT["kaset"] = K
    kaydet()

# ============================================================ kaset <-> kol zinciri (S1 x S2), on kol / el kaba
if calis("kaset_kol"):
    def kk(phi, th, al=None):
        inv = O.Pp(phi).multiply(O.Pr(th)).inverse()
        ks = [(a, tasi(s, inv)) for a, s in KASET]
        hed = list(KOL)
        if al is not None:
            hed += [(a, tasi(s, O.Pe(al))) for a, s in ONK]
        return O.enaz(ks, hed, pay=5)
    sat = []
    PH = list(range(-45, 136, 5))
    TH = [5.0, 5.5, 6.0, 7.0, 8.0, 10.0] + list(range(15, 121, 5))
    for phi in PH:
        for th in TH:
            d, a, b = kk(float(phi), float(th))
            sat.append((phi, th, round(d, 3), a, b))
        log("kaset-kol phi %d min %.3f  %.0fs" % (phi, min(q[2] for q in sat if q[0] == phi), time.time() - t0))
    m = min(sat, key=lambda q: q[2])
    ince = []
    for phi in np.arange(m[0] - 5, m[0] + 5.01, 1.0):
        if not (-45 <= phi <= 135):
            continue
        for th in (5.0, 5.25, 5.5, 6.0):
            d, a, b = kk(float(phi), th)
            ince.append((float(phi), th, round(d, 3), a, b))
    m2 = min(ince, key=lambda q: q[2])
    onk = []
    for phi in range(-45, 136, 15):
        for th in (5.0, 20.0, 45.0, 90.0, 120.0):
            for al in (0.0, 52.5, 105.0):
                d, a, b = kk(float(phi), th, al)
                onk.append((phi, th, al, round(d, 3), a, b))
    OUT["kaset_kol"] = dict(izgara=sat, en_az=m, ince=ince, ince_en_az=m2, onkol_el=min(onk, key=lambda q: q[3]),
                            izgara_tanim="S1 -45...135 (5), S2 5,5.5,6,7,8,10,15...120 (5); ince S1 +-5 (1) x S2 5...6")
    log("kaset-kol", m, m2, OUT["kaset_kol"]["onkol_el"])
    kaydet()

# ============================================================ gobek (tum parcalar) <-> kaset / bant / isil gomme (S1)
if calis("gobek"):
    sat = []
    for phi in np.arange(-60, 180.01, 2.5):
        gb = [(a, tasi(s, O.Pp(float(phi)))) for a, s in GOB if a != "S1 kablo tamburu"]
        d, a, b = O.enaz(gb, KASET + BANT, pay=5)
        sat.append((float(phi), round(d, 3), a, b))
    OUT["gobek_kaset_bant"] = dict(satir=sat, min_aralik=min([q for q in sat if -45 <= q[0] <= 135], key=lambda q: q[1]),
                                   min_geometri=min(sat, key=lambda q: q[1]))
    # kabuk bant (yeni boss / yarik) <-> omuz govde (sabit)
    d, a, b = O.enaz(BANT + KASET, GOV, pay=5)
    OUT["bant_kaset_govde"] = (round(d, 3), a, b)
    log("gobek", OUT["gobek_kaset_bant"]["min_aralik"], OUT["bant_kaset_govde"])
    kaydet()

# ============================================================ kaset civatalari ve isil gomme etleri
if calis("civata"):
    bant = [p["shape"] for p in KAB if p["ad"] == "Omuz bandi sag"][0]
    gv, kp = KG["S1 kaset govdesi sag"], KG["S1 kaset kapagi sag"]
    out = []
    for p in KAB:
        if not p["ad"].startswith("Kaset civatasi"):
            continue
        sc = p["shape"]
        psi_ = p["ad"].split("psi")[1].strip(" )")
        ins = [q["shape"] for q in KAB if q["ad"].startswith("Isil gomme somun M3 (S1 kaseti sag psi %s" % psi_)][0]
        c = sc.BoundBox.Center
        x_uc, x_bas = sc.BoundBox.XMin, sc.BoundBox.XMax
        ib = ins.BoundBox
        # isil gomme et: deligin cevresinde t kalinlikta kovan -> bantta olmayan oran
        rd = A.INSERT_DELIK[3] / 2
        x_dis = 152.0
        et = []
        for t in (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0):
            kov = Part.makeCylinder(rd + t, ib.XLength, V(ib.XMin, c.y, c.z), V(1, 0, 0)).cut(
                Part.makeCylinder(rd, ib.XLength + 1, V(ib.XMin - 0.5, c.y, c.z), V(1, 0, 0)))
            eksik = kov.cut(bant).Volume / kov.Volume
            et.append((t, round(eksik, 4)))
        # delik dibi: insert altinda t kalinlikta disk
        dip = []
        for t in (0.5, 1.0, 1.5, 2.0):
            dsk = Part.makeCylinder(rd, t, V(ib.XMin - 0.5 - t, c.y, c.z), V(1, 0, 0))
            dip.append((t, round(dsk.cut(bant).Volume / dsk.Volume, 4)))
        ps, rr = O.yz_psi(c.y, c.z)
        out.append(dict(ad=p["ad"], psi=round(ps, 2), r=round(rr, 2), vida_x=[round(x_uc, 3), round(x_bas, 3)],
                        insert_x=[round(ib.XMin, 3), round(ib.XMax, 3)], insert_cap=round(ib.YLength, 2),
                        kavrama_insert_icinde=round(min(ib.XMax, x_bas) - max(ib.XMin, x_uc), 3),
                        bas_kapak=round(sc.distToShape(kp)[0], 4), bas_kapak_giris=round(sc.common(kp).Volume, 3),
                        vida_govde_giris=round(sc.common(gv).Volume, 3), vida_bant_giris=round(sc.common(bant).Volume, 3),
                        insert_bant=round(ins.distToShape(bant)[0], 4), govde_bant=round(gv.distToShape(bant)[0], 4),
                        govde_bant_giris=round(gv.common(bant).Volume, 3), kapak_govde=round(kp.distToShape(gv)[0], 4),
                        kapak_govde_giris=round(kp.common(gv).Volume, 3), et_eksik_oran=et, dip_eksik_oran=dip))
        log("civata", out[-1])
    OUT["kaset_civata"] = out
    # isil gomme deliginin ped kenarina uzakligi (bant x 147...152 yan duvari): x 150'de dilim, insert merkezinden dis kenara
    kenar = []
    for v in out:
        y, z = O.psi_yz(v["psi"], v["r"])
        for xk in (148.0, 150.0, 151.5):
            ws = bant.slice(V(1, 0, 0), xk)
            m = min((w.distToShape(Part.Vertex(V(xk, y, z)))[0] for w in ws), default=None)
            kenar.append((v["ad"], xk, round(m, 3) if m is not None else None))
    OUT["insert_kenar"] = kenar
    kaydet()

# ============================================================ baski cikintisi (bagimsiz)
if calis("baski"):
    def cikinti(sh, yukari, ad, aci=45.0):
        yukari = V(*yukari)
        yukari.normalize()
        h0 = min(v.Point.dot(yukari) for v in sh.Vertexes)
        esik = -math.sin(math.radians(aci))
        top, yuzler = 0.0, []
        for i, f in enumerate(sh.Faces):
            try:
                pts, tri = f.tessellate(0.05)
            except Exception:
                continue
            a_f = 0.0
            for (i0, i1, i2) in tri:
                p0, p1, p2 = pts[i0], pts[i1], pts[i2]
                c = (p0 + p1 + p2) * (1.0 / 3)
                nn = (p1 - p0).cross(p2 - p0)
                ar = nn.Length / 2
                if ar < 1e-9:
                    continue
                try:
                    u, v = f.Surface.parameter(c)
                    n = f.normalAt(u, v)
                except Exception:
                    continue
                if c.dot(yukari) - h0 < 0.15:
                    continue
                if n.dot(yukari) < esik:
                    a_f += ar
            if a_f > 0.01:
                bb = f.BoundBox
                yuzler.append(dict(yuz=i, alan=round(a_f, 2), tip=f.Surface.TypeId.split("::")[-1],
                                   yukseklik=round(f.CenterOfMass.dot(yukari) - h0, 2),
                                   bb=[round(q, 2) for q in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)]))
                top += a_f
        return dict(parca=ad, yukari=[yukari.x, yukari.y, yukari.z], cikinti_alan_mm2=round(top, 2),
                    yuzler=sorted(yuzler, key=lambda q: -q["alan"])[:12], yukseklik=round(max(v.Point.dot(yukari) for v in sh.Vertexes) - h0, 2),
                    hacim=round(sh.Volume, 1))
    res = []
    res.append(cikinti(KG["S1 kaset govdesi sag"], (1, 0, 0), "S1 kaset govdesi sag (arka yuz x 152 tablada)"))
    res.append(cikinti(KG["S1 kaset kapagi sag"], (-1, 0, 0), "S1 kaset kapagi sag (flans x 159,5 tablada)"))
    res.append(cikinti(TAMBUR, (1, 0, 0), "S1 kablo tamburu (+X: -x dudak tablada)"))
    res.append(cikinti(TAMBUR, (-1, 0, 0), "S1 kablo tamburu (-X: +x dudak tablada)"))
    for r in res:
        log("baski", r["parca"], r["cikinti_alan_mm2"], r["yuzler"][:4])
    OUT["baski"] = res
    kaydet()

# ============================================================ montaj: kaset +x'ten kaydirma, civata alet erisimi, tambur kablo bagi kayisi
if calis("montaj"):
    M = {}
    kas2 = [(a, s) for a, s in KASET if a.startswith("S1 kaset")]
    # 1) kaset (govde + kapak) +x yonunden kaydirilirken gobek + kol (S1 phi, S2 th) ile ilk temas
    kay = []
    for phi in (-45.0, 0.0, 45.0, 90.0, 135.0):
        for th in (5.0, 45.0, 90.0):
            hed = [(a, tasi(s, O.Pp(phi))) for a, s in GOB] + [(a, tasi(s, O.Pp(phi).multiply(O.Pr(th)))) for a, s in KOL]
            ilk = None
            for t in np.arange(0.0, 120.01, 1.0):
                ks = []
                for a, s in kas2:
                    s2 = s.copy()
                    s2.translate(V(float(t), 0, 0))
                    ks.append((a, s2))
                hit = []
                for a, s in ks:
                    for b, q in hed:
                        if s.BoundBox.intersect(q.BoundBox):
                            v = s.common(q).Volume
                            if v > 0.01:
                                hit.append((a, b, round(v, 2)))
                if hit and t > 0:
                    ilk = (ilk or []) + [(float(t), hit[:2])]
            kay.append(dict(phi=phi, th=th, carpan_t=[q[0] for q in ilk] if ilk else [], ornek=ilk[:2] if ilk else None))
            log("kaydirma", kay[-1])
    M["kaydirma"] = kay
    # 2) kaset civatasi alet erisimi: basin ekseninde +x dogrultusunda x 160 -> 330 dogru parcasi; gobek + kol en yakin mesafe
    eris = []
    vidalar = [(a, s) for a, s in KASET if a.startswith("Kaset civatasi")]
    for a, s in vidalar:
        c = s.BoundBox.Center
        line = Part.makeLine(V(s.BoundBox.XMax, c.y, c.z), V(330.0, c.y, c.z))
        for phi in range(-45, 136, 5):
            for th in (5.0, 45.0, 90.0):
                hed = [(b, tasi(q, O.Pp(float(phi)))) for b, q in GOB] + [(b, tasi(q, O.Pp(float(phi)).multiply(O.Pr(th)))) for b, q in KOL]
                d, _, b = O.enaz([("l", line)], hed, pay=10)
                eris.append((a, phi, th, round(d, 2), b))
    M["civata_erisim"] = eris
    # 3) tambur kablo bagi kayisi: halkanin altindan (r 36...37) iki yarik arasinda gecen 1,0 mm kalin, 2,5 mm genis kayis
    TB = S1["tambur"]
    bag = TB["bag_psi"]
    kay_s = None
    try:
        sys.path.insert(0, os.path.join(O.R, "omuz"))
        def sektor(r0, r1, x0, x1, p0, p1):
            n = 40
            dis = [V(x0, *O.psi_yz(p0 + (p1 - p0) * i / n, r1)) for i in range(n + 1)]
            ic = [V(x0, *O.psi_yz(p1 - (p1 - p0) * i / n, r0)) for i in range(n + 1)]
            f = Part.Face(Part.makePolygon(dis + ic + [dis[0]]))
            return f.extrude(V(x1 - x0, 0, 0))
        xm = (154.4 + 157.4) / 2
        kay_s = sektor(TB["r"][0] - 1.0, TB["r"][0], xm - 1.25, xm + 1.25, bag + 3.0 - 1.25, bag + 11.0 + 1.25)
        tb_c = kay_s.common(TAMBUR).Volume
        sat = []
        for phi in np.arange(-45, 135.01, 1.0):
            ks = tasi(kay_s, O.Pp(float(phi)))
            d, _, b = O.enaz([("k", ks)], CAPB + [(a, s) for a, s in GOV if a == "Rulman kapagi"], pay=5)
            sat.append((float(phi), round(d, 3), b))
        M["kayis"] = dict(model="r %.1f...%.1f, x %.2f...%.2f, psi_g %.2f...%.2f (gobek)" % (TB["r"][0] - 1, TB["r"][0], xm - 1.25, xm + 1.25,
                                                                                       bag + 1.75, bag + 12.25),
                          tambura_giris_mm3=round(tb_c, 3), en_az=min(sat, key=lambda q: q[1]),
                          temas_phi=[q[0] for q in sat if q[1] < 1e-6], satir=sat)
        log("kayis", M["kayis"]["en_az"], M["kayis"]["temas_phi"][:5], len(M["kayis"]["temas_phi"]))
    except Exception as e:
        M["kayis"] = dict(hata=str(e))
    OUT["montaj"] = M
    kaydet()

# ============================================================ kutle + tork (bagimsiz)
if calis("tork"):
    RHO = {"PETG-CF": 1.27 * 0.9, "Aluminyum": 2.70, "Aluminyum 6063": 2.70, "Celik": 7.85, "Celik 8.8": 7.85, "Pirinc": 8.50}

    def kutle(p, modul):
        if p["kod"] == "DS3218MG servo":
            return 60.0
        if p["kod"] == "MG996R servo":
            return 55.0
        if p["tur"] == "Referans" or p["kod"] in ("(servo ile)",):
            return 0.0
        if p["malzeme"] == "PETG":
            # omuz: ust kol tupu ve tambur PETG 1,27 x 0,8; dirsek PETG 1,27 x 0,8 (dirsek_parcalar DOLULUK)
            return p["shape"].Volume / 1000 * 1.27 * 0.8
        if p["malzeme"] not in RHO:
            return None
        return p["shape"].Volume / 1000 * RHO[p["malzeme"]]

    def merkez(s):
        sol = s.Solids
        if not sol:
            return s.BoundBox.Center
        vt = sum(q.Volume for q in sol)
        c = V(0, 0, 0)
        for q in sol:
            c = c + q.CenterOfMass * (q.Volume / vt)
        return c
    GR = {}
    bilinmeyen = []
    karsi = {}
    for modul, P, gruplar in (("omuz", OMU, ("Gobek", "Kol")), ("dirsek", DIR, ("UstKol", "OnKol", "El"))):
        for g in gruplar:
            m_t, c_t, prop = 0.0, V(0, 0, 0), 0.0
            for p in P:
                if p["grup"] != g:
                    continue
                m = kutle(p, modul)
                if m is None:
                    bilinmeyen.append((modul, p["ad"], p["malzeme"]))
                    continue
                c = merkez(p["shape"])
                c_t = c_t + c * m
                m_t += m
                prop += p["kutle_prop"] or 0.0
            GR[modul + "_" + g] = (m_t, c_t * (1.0 / m_t))
            karsi[modul + "_" + g] = dict(benim=round(m_t, 2), fcstd_kutle_g=round(prop, 2))
    OUT["kutle"] = dict(grup=karsi, bilinmeyen=bilinmeyen)
    log("kutle", karsi, bilinmeyen)
    uc = V(*A.DIRSEK["el_ucu"])
    YUK = A.DIRSEK["yuk_g"]
    ya, oa, da, ba = A.OMUZ["yana_aralik"], A.OMUZ["one_arka_aralik"], A.DIRSEK["aralik"], A.DIRSEK["bilek_aralik"]
    PH = list(np.arange(oa[0], oa[1] + 0.01, 5.0))
    TH = sorted(set([ya[0]] + list(np.arange(10.0, ya[1] + 0.01, 5.0))))
    AL = list(np.arange(da[0], da[1] + 0.01, 5.0))
    BE = [-90.0, 0.0, 90.0]
    best = {"S1": [], "S2": []}
    for phi in PH:
        Tg = O.Pp(phi)
        ax1 = V(1, 0, 0)
        for th in TH:
            Tk = Tg.multiply(O.Pr(th))
            ax2 = Tg.Rotation.multVec(V(0, 0, 1))
            p2 = Tg.multVec(V(O.XR, 0, 0))
            for al in AL:
                To = Tk.multiply(O.Pe(al))
                for be in BE:
                    Te = To.multiply(O.Pb(be))
                    pts = [(GR["omuz_Gobek"], Tg, False), (GR["omuz_Kol"], Tk, True), (GR["dirsek_UstKol"], Tk, True),
                           (GR["dirsek_OnKol"], To, True), (GR["dirsek_El"], Te, True)]
                    t1, t2 = 0.0, 0.0
                    for (m, c), Tm, s2 in pts:
                        cc = Tm.multVec(c)
                        F = V(0, -m, 0)
                        t1 += cc.cross(F).dot(ax1)
                        if s2:
                            t2 += (cc - p2).cross(F).dot(ax2)
                    cu = Te.multVec(uc)
                    F1 = V(0, -1.0, 0)
                    u1 = cu.cross(F1).dot(ax1)
                    u2 = (cu - p2).cross(F1).dot(ax2)
                    best["S1"].append((t1, u1, (phi, th, al, be)))
                    best["S2"].append((t2, u2, (phi, th, al, be)))
    ST = 20.0
    res = {}
    for k in ("S1", "S2"):
        arr = best[k]
        t0_ = max(arr, key=lambda q: abs(q[0]))
        ty = max(arr, key=lambda q: abs(q[0] + YUK * q[1]))
        lo, hi = 0.0, 3000.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if max(abs(q[0] + mid * q[1]) for q in arr) / 1e4 <= ST / 2:
                lo = mid
            else:
                hi = mid
        res[k] = dict(yuksuz_kgcm=round(abs(t0_[0]) / 1e4, 3), yuksuz_poz=t0_[2], yuksuz_pay=round(ST / (abs(t0_[0]) / 1e4), 3),
                      yuklu_kgcm=round(abs(ty[0] + YUK * ty[1]) / 1e4, 3), yuklu_poz=ty[2], yuklu_pay=round(ST / (abs(ty[0] + YUK * ty[1]) / 1e4), 3),
                      izinli_yuk_2x_g=round(lo, 1), kol_mm=round(abs(max(arr, key=lambda q: abs(q[1]))[1]), 1))
    OUT["tork"] = dict(sonuc=res, stall=ST, yuk_g=YUK, el_ucu=list(A.DIRSEK["el_ucu"]), poz_sayisi=len(best["S1"]))
    log("tork", res)
    kaydet()

kaydet()
log("bitti %.0fs" % (time.time() - t0))
