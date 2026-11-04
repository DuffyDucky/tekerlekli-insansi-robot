# Lale 1,58 m - ikinci CAD ajaninin bagimsiz olcumleri (freecadcmd). Tasarim betiklerinin kod yolunu kullanmaz: tam modeli robot-montaj.FCStd'den okur,
# kol / kafa pozlarini moduller.py kinematigiyle kurar. Dosya degistirmez; sonucu ikinci-kontrol.json'a bolum bolum yazar.
# FC_SCRIPT=<bu dosya> IK_BOLUM=model,kol,kafa,tilt freecadcmd run_fc.py   (model: boy + ekran + kabuk ici/iskelet + baski; kol: kol x govde ince izgara; kafa: kafa x kol tilt +-13/+-15; tilt: 1 derece ilk cakisma + moment)
import os, sys, json, time, itertools
import numpy as np
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(UST, "montaj"), UST]
import moduller as MD
from moduller import A

V = App.Vector
BOLUM = (os.environ.get("IK_BOLUM") or "model").split(",")
CIKTI = os.environ.get("IK_CIKTI") or os.path.join(HERE, "ikinci-kontrol.json")
t0 = time.time()
TOL = 0.5


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


def kaydet(ad, veri):
    v = dict(json.load(open(CIKTI, encoding="utf-8"))) if os.path.exists(CIKTI) else {}
    v[ad] = veri
    json.dump(v, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)


# ====================================================================== model: tam robot, FCStd
def b_model():
    doc = App.openDocument(os.path.join(UST, "montaj", "robot-montaj.FCStd"))
    P = []
    for o in doc.Objects:
        if o.TypeId == "Part::Feature" and hasattr(o, "Tur"):
            s = o.Shape.copy()
            s.Placement = o.getGlobalPlacement()
            s = s.copy()
            ust = o.getParentGeoFeatureGroup() if hasattr(o, "getParentGeoFeatureGroup") else None
            P.append(dict(ad=o.Label, tur=o.Tur, sh=s, bb=s.BoundBox, grup=ust.Name if ust else "", kutle=getattr(o, "Kutle_g", 0.0), obb=s.optimalBoundingBox()))
    log("parca", len(P))
    out = dict(parca=len(P), kutle_g=round(sum(p["kutle"] for p in P), 1))
    # ---- 1) boy: tum parcalarda optimalBoundingBox
    ust_p = max(P, key=lambda p: p["obb"].YMax)
    alt_p = min(P, key=lambda p: p["obb"].YMin)
    bb_ust = max(P, key=lambda p: p["bb"].YMax)
    bb_alt = min(P, key=lambda p: p["bb"].YMin)
    out["boy"] = dict(zemin_y=round(alt_p["obb"].YMin, 3), zemin_parca=alt_p["ad"], tepe_y=round(ust_p["obb"].YMax, 3), tepe_parca=ust_p["ad"],
                      boy_mm=round(ust_p["obb"].YMax - alt_p["obb"].YMin, 3), boundbox_tepe=round(bb_ust["bb"].YMax, 3), boundbox_zemin=round(bb_alt["bb"].YMin, 3),
                      not_="tum parcalarda optimalBoundingBox; BoundBox karsilastirma icin")
    log("boy", out["boy"])
    # ---- 7) ekran: kasa, cerceve, tasiyici, vidalar x tum robot
    ON = ("Gogus ekrani", "Cerceve civatasi", "Isil gomme somun M3 (gogus", "VESA", "Tasiyici", "Cekic somun M6 (direk on")
    EK = [p for p in P if p["ad"].startswith(ON)]
    BA = [p for p in P if p not in EK]
    kasa = next(p for p in P if p["ad"].startswith("Gogus ekrani 11,6"))
    direk = next(p for p in P if p["ad"] == "Govde diregi")
    cak, temas, kontrol = [], [], 0
    for a in EK:
        for b in BA:
            if a["obb"].intersect(b["obb"]):
                kontrol += 1
                v = a["sh"].common(b["sh"]).Volume
                if v > TOL:
                    cak.append((a["ad"], b["ad"], round(v, 3)))
                elif a["sh"].distToShape(b["sh"])[0] < 1e-3:
                    temas.append((a["ad"], b["ad"], round(v, 4)))
    ic = []
    for a, b in itertools.combinations(EK, 2):
        if a["obb"].intersect(b["obb"]):
            v = a["sh"].common(b["sh"]).Volume
            if v > TOL:
                ic.append((a["ad"], b["ad"], round(v, 3)))
    # kasa local cerceve: 15 derece yatik. Yerel eksenlerde kasa kutusu ve bant boslugu
    pl = App.Placement(V(0, A.GOGUS_EKRAN_Y, A.gogus_z(A.GOGUS_EKRAN_Y)), App.Rotation(V(1, 0, 0), -A.GOGUS_EGIM))
    kl = kasa["sh"].copy()
    kl.transformShape(pl.inverse().toMatrix(), True)
    kb = kl.optimalBoundingBox()
    out["ekran"] = dict(
        ekran_parca=[p["ad"] for p in EK], cift_kontrol=kontrol, cakisma=cak, ic_cakisma=ic, temas=temas,
        kasa_direk_mm=round(kasa["sh"].distToShape(direk["sh"])[0], 3),
        kasa_bant={p["ad"]: round(kasa["sh"].distToShape(p["sh"])[0], 3) for p in P if p["ad"].startswith(("Gogus bandi", "Omuz bandi", "Govde orta bandi"))},
        kasa_yerel=dict(x=[round(kb.XMin, 3), round(kb.XMax, 3)], y=[round(kb.YMin, 3), round(kb.YMax, 3)], z=[round(kb.ZMin, 3), round(kb.ZMax, 3)],
                        cep=list(A.GOGUS_EKRAN["cep"]), kasa_arayuz=list(A.GOGUS_EKRAN["kasa"])),
        kutle_g=kasa["kutle"], kutle_arayuz=A.GOGUS_EKRAN["kutle_g"])
    log("ekran", out["ekran"]["cakisma"], out["ekran"]["kasa_direk_mm"], out["ekran"]["kasa_bant"])
    # ---- kabuk ici ve kabuk x iskelet, modul bilgisi montaj-analiz'den degil grup adindan
    grp = {}
    for p in P:
        grp.setdefault(p["grup"], []).append(p)
    out["gruplar"] = {g: len(v) for g, v in grp.items()}
    kab = [p for p in P if p["grup"].lower().startswith("kabuk")]
    isk = [p for p in P if p["grup"].lower().startswith("iskelet")]
    c_ic, n_ic = [], 0
    for a, b in itertools.combinations(kab, 2):
        if a["obb"].intersect(b["obb"]):
            n_ic += 1
            v = a["sh"].common(b["sh"]).Volume
            if v > TOL:
                c_ic.append((a["ad"], b["ad"], round(v, 3)))
    c_is, n_is = [], 0
    for a in kab:
        for b in isk:
            if a["obb"].intersect(b["obb"]):
                n_is += 1
                v = a["sh"].common(b["sh"]).Volume
                if v > TOL:
                    c_is.append((a["ad"], b["ad"], round(v, 3)))
    out["kabuk"] = dict(parca=len(kab), iskelet_parca=len(isk), ic_cift=n_ic, ic_cakisma=c_ic, iskelet_cift=n_is, iskelet_cakisma=c_is, bolge_sayisi=len(A.BOLGELER))
    log("kabuk ic", len(c_ic), "/", n_ic, "kabuk x iskelet", len(c_is), "/", n_is)
    # ---- 8) baski: Tur == Baski tum parcalar, sirali olcu yazici kullanilabilir hacmine (yonden bagimsiz, model duruşunda AABB + ozel yon gerekmez)
    UX, UY, UZ = A.YAZICI["kullanilabilir"]
    tab, sig = [], []
    for p in P:
        if p["tur"] != "Baski":
            continue
        d = sorted((p["obb"].XLength, p["obb"].YLength, p["obb"].ZLength), reverse=True)
        tab.append((p["ad"], p["grup"], [round(x, 1) for x in d]))
        if d[0] > max(UX, UY, UZ) or d[1] > 246.0 or d[2] > 246.0:
            sig.append(tab[-1])
    out["baski"] = dict(adet=len(tab), tabla=[UX, UY, UZ], sigmayan_model_durusu=sig, en_buyuk=sorted(tab, key=lambda r: -r[2][0])[:12], liste=tab,
                        not_="AABB model durusunda; egik duran parca burada oldugundan buyuk gorunur, sigmayan cikarsa baski yonunde ayrica bakilir")
    log("baski", len(tab), "sigmayan (model durusu)", [s[0] for s in sig])
    kaydet("model", out)
    App.closeDocument(doc.Name)


# ====================================================================== ortak: modul yukle + poz
def yukle(adlar):
    M = {}
    for ad in adlar:
        d = MD.yukle(ad)
        d["P"] = []
        for p in d["parcalar"]:
            if p["haric"] or p["tur"] == "Referans" or p["grup"] == "Referans":
                continue
            g = MD.global_sekil(p["shape"], ad)
            bb = g.optimalBoundingBox()
            d["P"].append(dict(ad=p["ad"], grup=p["grup"], g=g, bb=bb, kose=np.array([[x, y, z, 1.0] for x in (bb.XMin, bb.XMax) for y in (bb.YMin, bb.YMax) for z in (bb.ZMin, bb.ZMax)])))
        M[ad] = d
        log("modul", ad, len(d["P"]))
    return M


def mat(M, ad, grup, poz):
    q = M[ad]["beklenen"](poz, grup)
    return MD.global_poz(ad, q)


def npm(pl):
    m = pl.toMatrix()
    return np.array([[m.A11, m.A12, m.A13, m.A14], [m.A21, m.A22, m.A23, m.A24], [m.A31, m.A32, m.A33, m.A34], [0, 0, 0, 1.0]])


def aabb(p, Mn):
    c = (Mn @ p["kose"].T).T[:, :3]
    return c.min(axis=0), c.max(axis=0)


def gap(a0, a1, b0, b1):
    d = np.maximum(np.maximum(b0 - a1, a0 - b1), 0.0)
    return float(np.linalg.norm(d))


def tasi(p, pl):
    s = p["g"].copy()
    s.transformShape(pl.toMatrix(), True)
    return s


# ====================================================================== kol: S2 ince izgara x govde bandlari + ekran. carpisma.py kaba izgarasindan bagimsiz
def b_kol():
    sonuc = {}
    M = yukle(["kabuk", "omuz_sag", "dirsek_sag", "omuz_sol", "dirsek_sol"])
    for taraf in ("sag", "sol"):
        H = M["kabuk"]["P"]          # tum kabuk (bant, ekran, kaset, braket civatalari); AABB suzgeci 12 mm
        H0 = np.array([[p["bb"].XMin, p["bb"].YMin, p["bb"].ZMin] for p in H])
        H1 = np.array([[p["bb"].XMax, p["bb"].YMax, p["bb"].ZMax] for p in H])
        om = [dict(p, mod="omuz_" + taraf) for p in M["omuz_" + taraf]["P"] if p["grup"] == "Kol"]
        dr = [dict(p, mod="dirsek_" + taraf) for p in M["dirsek_" + taraf]["P"]]
        har = om + dr
        en = {}          # (S2, hareketli, hedef) -> (mm, poz)
        cak = []
        n_olc = 0
        S2 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0]
        for s2, s1, de, bi in itertools.product(S2, range(-45, 136, 15), (0, 35, 70, 105), (-90, 0, 90)):
            poz = dict(one_arka=float(s1), yana=s2, dirsek=float(de), bilek=float(bi), pan=0.0, tilt=0.0)
            cache = {}
            for p in har:
                k = (p["mod"], p["grup"])
                if k not in cache:
                    pl = mat(M, p["mod"], p["grup"], poz)
                    cache[k] = (pl, npm(pl))
                pl, Mn = cache[k]
                a0, a1 = aabb(p, Mn)
                g = np.linalg.norm(np.maximum(np.maximum(H0 - a1, a0 - H1), 0.0), axis=1)
                for j in np.nonzero(g < 12.0)[0]:
                    q = H[j]
                    s = tasi(p, pl)
                    d = s.distToShape(q["g"])[0]
                    n_olc += 1
                    key = (s2, p["ad"], q["ad"])
                    if key not in en or d < en[key][0]:
                        en[key] = (round(d, 3), (s1, s2, de, bi))
                    if d < 1e-3:
                        v = s.common(q["g"]).Volume
                        if v > TOL:
                            cak.append((p["ad"], q["ad"], s1, s2, de, bi, round(v, 2)))
        s2_ozet = {}
        for (s2, a, b), (d, pz) in en.items():
            r = s2_ozet.setdefault(str(s2), dict(min_mm=1e9))
            if d < r["min_mm"]:
                r.update(min_mm=d, hareketli=a, hedef=b, poz=pz)
        catal = {str(s2): min(((d, a, b, pz) for (s, a, b), (d, pz) in en.items() if s == s2 and ("atal" in a or "ilezi" in a)), default=None) for s2 in S2}
        sonuc[taraf] = dict(olcum=n_olc, s2_en_kucuk=s2_ozet, dirsek_catali_s2=catal, cakisma=cak[:80], cakisma_sayisi=len(cak), en_kucuk_20=sorted(((d, s2, a, b, pz) for (s2, a, b), (d, pz) in en.items()), key=lambda r: r[0])[:20])
        log("kol", taraf, "olcum", n_olc, "cakisma", len(cak), {k: v["min_mm"] for k, v in s2_ozet.items()})
    kaydet("kol", dict(izgara="S2 0,1,2,3,4,5,6,8,10,15 x S1 -45...135/15 x dirsek 0,35,70,105 x bilek -90,0,90; hareketli omuz Kol + dirsek; hedef tum kabuk modulu", sonuc=sonuc))


# ====================================================================== catal: dirsek catali + bilezik (UstKol) x tum kabuk, S1 5 derece adim, S2 ince (dirsek/bilekten bagimsiz grup)
def b_catal():
    M = yukle(["kabuk", "omuz_sag", "dirsek_sag", "omuz_sol", "dirsek_sol"])
    H = M["kabuk"]["P"]
    H0 = np.array([[p["bb"].XMin, p["bb"].YMin, p["bb"].ZMin] for p in H])
    H1 = np.array([[p["bb"].XMax, p["bb"].YMax, p["bb"].ZMax] for p in H])
    S2 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 15.0]
    sonuc = {}
    for taraf in ("sag", "sol"):
        har = [p for p in M["dirsek_" + taraf]["P"] if p["grup"] == "UstKol"]
        en, cak, n = {}, [], 0
        for s2, s1 in itertools.product(S2, range(-45, 136, 5)):
            poz = dict(one_arka=float(s1), yana=s2, dirsek=0.0, bilek=0.0, pan=0.0, tilt=0.0)
            pl = mat(M, "dirsek_" + taraf, "UstKol", poz)
            Mn = npm(pl)
            for p in har:
                a0, a1 = aabb(p, Mn)
                g = np.linalg.norm(np.maximum(np.maximum(H0 - a1, a0 - H1), 0.0), axis=1)
                sk = None
                for j in np.nonzero(g < 25.0)[0]:
                    sk = sk or tasi(p, pl)
                    d = sk.distToShape(H[j]["g"])[0]
                    n += 1
                    k = (s2, p["ad"], H[j]["ad"])
                    if k not in en or d < en[k][0]:
                        en[k] = (round(d, 3), s1)
                    if d < 1e-3:
                        v = sk.common(H[j]["g"]).Volume
                        if v > TOL:
                            cak.append((p["ad"], H[j]["ad"], s1, s2, round(v, 2)))
        s2oz = {}
        for s2 in S2:
            sat = sorted(((d, a, b, s1) for (s, a, b), (d, s1) in en.items() if s == s2), key=lambda r: r[0])
            s2oz[str(s2)] = sat[:6]
        sonuc[taraf] = dict(olcum=n, cakisma_sayisi=len(cak), cakisma=cak[:60], s2=s2oz)
        log("catal", taraf, n, len(cak), {k: (v[0][:3] if v else None) for k, v in s2oz.items()})
    kaydet("catal", dict(izgara="dirsek UstKol grubu x tum kabuk; S2 %s x S1 -45...135/5; AABB suzgeci 25 mm" % S2, sonuc=sonuc))


# ====================================================================== kafa: tilt uclari carpisma izgarasinda yok (kaba -10,0,10; ince 5 adim); +-13 ve +-15'te kol ile bak
def b_kafa():
    M = yukle(["omuz_sag", "dirsek_sag", "omuz_sol", "dirsek_sol", "kafa"])
    KA = M["kafa"]["P"]
    KH = [p for p in KA if p["grup"] != "Govde"]
    sonuc = {}
    TILT = (-15.0, -13.0, 13.0, 15.0)
    PAN = list(range(-90, 91, 15))
    KOL = list(itertools.product((75, 90, 105, 120, 135), (5, 15, 30, 45, 60, 90), (0, 35, 70, 90, 105), (-90, 0, 90)))
    for taraf in ("sag", "sol"):
        har = [dict(p, mod="dirsek_" + taraf) for p in M["dirsek_" + taraf]["P"]] + [dict(p, mod="omuz_" + taraf) for p in M["omuz_" + taraf]["P"] if p["grup"] == "Kol"]
        en, cak, n = {}, [], 0
        # kafa pozlari: parca AABB dizisi
        kp = {}
        for pa, ti in itertools.product(PAN, TILT):
            poz = dict(one_arka=0.0, yana=5.0, dirsek=0.0, bilek=0.0, pan=float(pa), tilt=ti)
            pls = {g: mat(M, "kafa", g, poz) for g in ("Boyun", "Bas")}
            A0, A1 = [], []
            for p in KH:
                a0, a1 = aabb(p, npm(pls[p["grup"]]))
                A0.append(a0)
                A1.append(a1)
            kp[(pa, ti)] = (pls, np.array(A0), np.array(A1))
        for s1, s2, de, bi in KOL:
            poz = dict(one_arka=float(s1), yana=float(s2), dirsek=float(de), bilek=float(bi), pan=0.0, tilt=0.0)
            cc = {}
            for p in har:
                k = (p["mod"], p["grup"])
                if k not in cc:
                    pl = mat(M, p["mod"], p["grup"], poz)
                    cc[k] = (pl, npm(pl))
                pl, Mn = cc[k]
                a0, a1 = aabb(p, Mn)
                sk = None
                for (pa, ti), (pls, A0, A1) in kp.items():
                    g = np.linalg.norm(np.maximum(np.maximum(A0 - a1, a0 - A1), 0.0), axis=1)
                    for j in np.nonzero(g < 10.0)[0]:
                        if sk is None:
                            sk = tasi(p, pl)
                        q = KH[j]
                        s2_ = tasi(q, pls[q["grup"]])
                        d = sk.distToShape(s2_)[0]
                        n += 1
                        key = (ti, p["ad"], q["ad"])
                        if key not in en or d < en[key][0]:
                            en[key] = (round(d, 3), (s1, s2, de, bi, pa))
                        if d < 1e-3:
                            v = sk.common(s2_).Volume
                            if v > TOL:
                                cak.append((p["ad"], q["ad"], s1, s2, de, bi, pa, ti, round(v, 2)))
        sonuc[taraf] = dict(olcum=n, cakisma_sayisi=len(cak), cakisma=cak[:60], en_kucuk_20=sorted(((d, ti, a, b, pz) for (ti, a, b), (d, pz) in en.items()), key=lambda r: r[0])[:20])
        log("kafa", taraf, "olcum", n, "cakisma", len(cak), sonuc[taraf]["en_kucuk_20"][:3])
    kaydet("kafa", dict(izgara="pan -90...90/15 x tilt -15,-13,13,15 x kol S1 75...135/15, S2 5,15,30,45,60,90, dirsek 0,35,70,90,105, bilek -90,0,90", sonuc=sonuc))


# ====================================================================== tilt: 1 derece adimla ilk cakisma (kafa_montaj 5 derece adimla bakar), + kutle/AM/moment parcalardan
def b_tilt():
    M = yukle(["kafa"])
    KA = M["kafa"]["P"]
    Bas = [p for p in KA if p["grup"] == "Bas"]
    Dig = [p for p in KA if p["grup"] != "Bas"]
    sonuc = {}
    for ti in (-20, -19, -18, -17, -16, -15, -14, -13, 13, 14, 15, 16, 17, 18, 19, 20):
        en, cak = None, []
        for pa in (-90, -45, 0, 45, 90):
            poz = dict(pan=float(pa), tilt=float(ti))
            pB, pD = mat(M, "kafa", "Bas", poz), mat(M, "kafa", "Boyun", poz)
            for a in Bas:
                a0, a1 = aabb(a, npm(pB))
                sa = None
                for b in Dig:
                    plb = pD if b["grup"] == "Boyun" else App.Placement()
                    b0, b1 = aabb(b, npm(plb))
                    if gap(a0, a1, b0, b1) < 5.0:
                        sa = sa or tasi(a, pB)
                        sb = tasi(b, plb)
                        d = sa.distToShape(sb)[0]
                        if en is None or d < en[0]:
                            en = (round(d, 3), a["ad"], b["ad"], pa)
                        if d < 1e-3:
                            v = sa.common(sb).Volume
                            if v > TOL:
                                cak.append((a["ad"], b["ad"], pa, round(v, 2)))
        sonuc[str(ti)] = dict(en_kucuk=en, cakisma=cak[:10], cakisma_sayisi=len(cak))
        log("tilt", ti, en, len(cak))
    P = MD.yukle("kafa")["parcalar"]
    B = [p for p in P if not p["haric"] and p["grup"] == "Bas"]
    m = sum(p["kutle"] for p in B)
    c = sum((p["merkez"] * p["kutle"] for p in B), V(0, 0, 0)) * (1.0 / m)
    t = A.KAFA["tilt_nokta"]
    kp = (25.0, V(-10.0, t[1] - 20.0, 15.0))     # kafa_montaj KABLO_KAFA (tahmini)
    m2 = m + kp[0]
    c2 = (c * m + kp[1] * kp[0]) * (1.0 / m2)
    d = ((c2.y - t[1]) ** 2 + (c2.z - t[2]) ** 2) ** 0.5
    sonuc["moment"] = dict(kutle_parca_g=round(m, 1), kutle_g=round(m2, 1), am=[round(x, 2) for x in c2], eksen_yz=[t[1], t[2]], am_eksen_mm=round(d, 2),
                           statik_kgcm=round(m2 * d / 10000.0, 3), z_geri_mm=round(t[2] - c2.z, 2))
    log("moment", sonuc["moment"])
    kaydet("tilt", sonuc)


for b in BOLUM:
    dict(model=b_model, kol=b_kol, kafa=b_kafa, tilt=b_tilt, catal=b_catal)[b]()
log("bitti")
