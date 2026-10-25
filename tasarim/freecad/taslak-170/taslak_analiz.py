# Lale 1,70 m TASLAK - BAGIMSIZ ANALIZ (FreeCAD 1.1): kutle/AM dogrulamasi, atalet, tam carpisma taramasi.
# Analiz ajani (21 Ekim 2026). Tasarim ajaninin ciktilarini (kutle.json, taslak-analiz.json) KULLANMAZ; parcalari
# taslak_parcalar.py'den yeniden kurar, FCStd ve STEP'i ayrica okur. Mevcut modullere ve taslak betiklerine yazmaz.
# Calistir (yolda "ü" var, ASCII baslatici):
#   FC_SCRIPT=<bu dosya> TA_BOLUM=<bolumler> [TASLAK_TABAN_W=520] [TA_ROBOT=eski] freecadcmd.exe C:/Users/Victus/.robot-cad/run_fc.py
# Bolumler (virgulle): kutle (grup kutle/AM/atalet tensoru -> analiz/girdi-<robot>-<W>.json), dogrula (FCStd + STEP + ornek),
#   statik (ev pozu tum parca ciftleri), kol_sag, kol_sol (kol zinciri x sabit), kolkol, kafa (pan x tilt x sabit),
#   kafakol_sag, kafakol_sol (kafa x kol), kafakol_ince_sag, kafakol_ince_sol (kafa x kol en dar yer cevresi ince, kontrol ajani 24 Ekim 2026),
#   catal (dirsek catali dis kolu eski 5 mm / yeni TA.CATAL_DIS_KOL ayni hedeflere: dirsek ekseni + omuz S1 x S2 5 derece; yalniz yeni robot),
#   catal_geo (dis kol geometri kontrolu; once TASLAK_CATAL_DIS_KOL=5 ve =7 ile -> catal-geo-5/-7.json, sonra varsayilanla -> catal-geo.json + fark;
#   8 mm: horn civatasi + bas alti pul yigini, kontrol ajani 24 Ekim 2026 gece).
#   TA_ROBOT=eski: ayni tarama mevcut 125 cm robotta (karsilastirma, yontem dogrulamasi). TA_BOLUM="" : yalniz robotlari kurar (import icin).
# Cikti: analiz/<bolum>-<robot>[-<W>].json. Koordinat global (orijin zemin + robot merkezi, +X sag, +Y yukari, +Z ileri), mm, g.
import os, sys, json, time, math, random, itertools
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BOLUM = [b.strip() for b in os.environ.get("TA_BOLUM", "kutle").split(",") if b.strip()]
ROBOT = os.environ.get("TA_ROBOT", "yeni")
OUT = os.path.join(HERE, "analiz")
os.makedirs(OUT, exist_ok=True)
import FreeCAD as App
import Part
import numpy as np
import taslak_parcalar as TP
from taslak_parcalar import V, A, TA, MD

t0 = time.time()
W = int(round(TA.TABAN_W))
TOL = 0.5


def log(*a):
    print(" ".join(str(x) for x in a), "%.0fs" % (time.time() - t0), flush=True)


def r3(v, n=3):
    return [round(v.x, n), round(v.y, n), round(v.z, n)]


def yaz(ad, veri):
    yol = os.path.join(OUT, ad)
    json.dump(veri, open(yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    log("yazildi", ad)


# ====================================================================== robotlar (yeni = taslak, eski = mevcut 125 cm)
def robot_kur(eski):
    L = TP.ESKI if eski else TP.P
    P = [dict(i=k, ad=p["ad"], modul=p["modul"], grup=p["grup"], shape=p["shape"], kutle=float(p["kutle"]), merkez=V(p["merkez"]),
              tur=p.get("tur", ""), durum=p.get("durum", "")) for k, p in enumerate(L)]
    AX = {}
    if eski:
        for ad in MD.SIRA:
            for e in TP.MOD[ad]["eklemler"]:
                cer = MD.global_cerceve(ad, e["cerceve"])
                AX[(ad, e["anahtar"])] = dict(n=V(cer.Base), u=cer.Rotation.multVec(V(0, 0, 1)), sinir=tuple(e["sinir"]) if e["sinir"] else None)
    else:
        for e in TP.EKLEMLER:
            if e["tip"] == "Revolute":
                cer = e["cerceve"]
                AX[(e["modul"], e["anahtar"])] = dict(n=V(cer.Base), u=cer.Rotation.multVec(V(0, 0, 1)),
                                                     sinir=tuple(e["sinir"]) if e["sinir"] else None)
    return dict(ad="eski" if eski else "yeni", P=P, AX=AX)


def Rm(a, ang):
    if abs(ang) < 1e-12:
        return App.Matrix()
    return App.Placement(V(0, 0, 0), App.Rotation(a["u"], float(ang)), a["n"]).toMatrix()


def kol_M(AX, taraf, g, sp):
    """Seri zincir, ev pozundaki eksenlerle (product of exponentials): S1 x S2 x dirsek x bilek."""
    om, dr = "omuz_" + taraf, "dirsek_" + taraf
    phi, th, al, be = (list(sp) + [0.0] * 4)[:4]
    M = Rm(AX[(om, "one_arka")], phi)
    if g == "Gobek":
        return M
    M = M.multiply(Rm(AX[(om, "yana")], th))
    if g in ("Kol", "UstKol"):
        return M
    M = M.multiply(Rm(AX[(dr, "dirsek")], al))
    if g == "OnKol":
        return M
    return M.multiply(Rm(AX[(dr, "bilek")], be))


def kafa_M(AX, g, sp):
    psi, th = (list(sp) + [0.0, 0.0])[:2]
    if g == "Govde":
        return App.Matrix()
    M = Rm(AX[("kafa", "pan")], psi)
    if g == "Boyun":
        return M
    return M.multiply(Rm(AX[("kafa", "tilt")], th))


def M_parca(R, p, poz):
    m, g = p["modul"], p["grup"]
    if m.startswith(("omuz_", "dirsek_")):
        if g == "Govde":
            return None
        return kol_M(R["AX"], m.split("_")[1], g, poz.get(m.split("_")[1], (0, 0, 0, 0)))
    if m == "kafa":
        return None if g == "Govde" else kafa_M(R["AX"], g, poz.get("kafa", (0, 0)))
    return None


def sekil(p, M):
    s = p["shape"].copy()
    if M is not None:
        s.transformShape(M)
    return s


def kesisim(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def olc_cift(R, pa, pb, poz):
    """Iki parcanin ayni pozdaki (mesafe, cakisma hacmi)."""
    a, b = sekil(pa, M_parca(R, pa, poz)), sekil(pb, M_parca(R, pb, poz))
    d = a.distToShape(b)[0]
    v = kesisim(a, b) if d < 1e-6 else 0.0
    return d, v


YENI = robot_kur(False)
ESKI = robot_kur(True)
R = ESKI if ROBOT == "eski" else YENI
log("robot", R["ad"], "parca", len(R["P"]), "taban W", W)

# --- yeni -> eski parca eslemesi (ayni modul + ad, eski konuma en yakin merkez)
_by = {}
for j, q in enumerate(ESKI["P"]):
    _by.setdefault((q["modul"], q["ad"]), []).append(j)
KARSI = {}
for i, p in enumerate(TP.P):
    c = _by.get((p["modul"], p.get("eski_ad", p["ad"])))       # yeniden adlanan parca (DS3235): 125 cm adiyla eslenir
    if not c:
        continue
    sh = p["v"] if p.get("v") is not None else TP.kaydir(p["modul"], p["grup"])
    hedef = V(p["merkez"]) - sh
    KARSI[i] = min(c, key=lambda j: (ESKI["P"][j]["merkez"] - hedef).Length)


def eski_karsilik(ia, ib, poz):
    """Yeni robottaki (ia, ib) ciftinin 125 cm robottaki karsiligi ayni pozda: (d, v) ya da None (yeni parca)."""
    if ia not in KARSI or ib not in KARSI:
        return None
    return olc_cift(ESKI, ESKI["P"][KARSI[ia]], ESKI["P"][KARSI[ib]], poz)


# ---------------------------------------------------------------------- kinematik dogrulamasi (eski robot: modul fonksiyonlari)
def kinematik_dogrula():
    import omuz_parcalar as OP
    import dirsek_parcalar as DP
    import kafa_parcalar as KP
    hata = 0.0
    pts = [V(200, 700, 30), V(-150, 900, -40), V(10, 1100, 60)]
    for taraf in ("sag", "sol"):
        for sp in ((60, 30, 45, 30), (-30, 90, 100, -60), (120, 10, 80, 90), (135, 5, 105, -90)):
            for g in ("Gobek", "Kol", "UstKol", "OnKol", "El"):
                if g == "Gobek":
                    ref = MD.global_poz("omuz_" + taraf, OP.Pp(sp[0]))
                elif g == "Kol":
                    ref = MD.global_poz("omuz_" + taraf, OP.Pp(sp[0]).multiply(OP.Pr(sp[1])))
                else:
                    ref = MD.global_poz("dirsek_" + taraf, DP.grup_yer(g, *sp))
                M = kol_M(ESKI["AX"], taraf, g, sp)
                for q in pts:
                    hata = max(hata, (ref.multVec(q) - M.multVec(q)).Length)
    for sp in ((45, 20), (-80, -25), (90, 30)):
        for g, kg in (("Boyun", "Pan"), ("Bas", "Kafa")):
            ref = MD.global_poz("kafa", KP.grup_yer(kg, *sp))
            M = kafa_M(ESKI["AX"], g, sp)
            for q in pts:
                hata = max(hata, (ref.multVec(q) - M.multVec(q)).Length)
    # yeni eksenler = eski + beklenen kaydirma
    kay = {}
    for (m, a), e in YENI["AX"].items():
        if (m, a) in ESKI["AX"]:
            d = e["n"] - ESKI["AX"][(m, a)]["n"]
            du = (e["u"] - ESKI["AX"][(m, a)]["u"]).Length
            kay["%s.%s" % (m, a)] = dict(kayma=r3(d, 2), yon_farki=round(du, 9), sinir_eski=ESKI["AX"][(m, a)]["sinir"], sinir_yeni=e["sinir"])
    return dict(en_buyuk_sapma_mm=hata, eksen_kaymasi=kay,
                not_="eski robotta POE zinciri (ev pozu eksenleri, ana montaj eklemleri) ile modul fonksiyonlari (Pp, Pr, grup_yer, "
                     "MD.global_poz) karsilastirildi; yeni robot ayni zincirle, taslak eklem eksenleriyle suruluyor")


# ====================================================================== 1) kutle, AM, atalet tensoru
def kati_bilgi(sh):
    sols = sh.Solids
    if not sols:
        return None
    vt = sum(s.Volume for s in sols)
    if vt <= 0:
        return None
    c = V(0, 0, 0)
    for s in sols:
        c = c + s.CenterOfMass * (s.Volume / vt)
    I = np.zeros((3, 3))
    for s in sols:
        Mi = s.MatrixOfInertia
        Ii = np.array([[Mi.A11, Mi.A12, Mi.A13], [Mi.A21, Mi.A22, Mi.A23], [Mi.A31, Mi.A32, Mi.A33]])
        d = s.CenterOfMass - c
        d = np.array([d.x, d.y, d.z])
        I += Ii + s.Volume * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
    return vt, c, I


def paralel(I, m, d):
    d = np.asarray(d, float)
    return I + m * (np.dot(d, d) * np.eye(3) - np.outer(d, d))


def b_kutle(Rb):
    G = OrderedDict()
    for p in Rb["P"]:
        k = "%s|%s" % (p["modul"], p["grup"])
        kb = kati_bilgi(p["shape"])
        if kb is None:
            vt, cs, Ip = 0.0, p["merkez"], np.zeros((3, 3))
        else:
            vt, cs, I1 = kb
            Ip = I1 * (p["kutle"] / vt)                      # g mm2, parca kendi sekil merkezinde
        g = G.setdefault(k, dict(m=0.0, mc=np.zeros(3), msc=np.zeros(3), parca=[], n=0))
        g["m"] += p["kutle"]
        g["mc"] += p["kutle"] * np.array([p["merkez"].x, p["merkez"].y, p["merkez"].z])
        g["msc"] += p["kutle"] * np.array([cs.x, cs.y, cs.z])
        g["parca"].append((p["kutle"], np.array([cs.x, cs.y, cs.z]), Ip))
        g["n"] += 1
    out = OrderedDict()
    Mtop, mc_top, msc_top = 0.0, np.zeros(3), np.zeros(3)
    for k, g in G.items():
        c = g["mc"] / g["m"] if g["m"] else np.zeros(3)
        cs = g["msc"] / g["m"] if g["m"] else np.zeros(3)
        I = np.zeros((3, 3))
        for m, cp, Ip in g["parca"]:
            I += paralel(Ip, m, cp - cs)
        out[k] = dict(m=round(g["m"], 3), c=[round(x, 3) for x in c], c_sekil=[round(x, 3) for x in cs], I=I.round(1).tolist(), parca=g["n"])
        Mtop += g["m"]
        mc_top += g["mc"]
        msc_top += g["msc"]
    c_top = mc_top / Mtop
    cs_top = msc_top / Mtop
    I_top = np.zeros((3, 3))
    for k, g in out.items():
        I_top += paralel(np.array(g["I"]), g["m"], np.array(g["c_sekil"]) - cs_top)
    ozel = {}
    for p in Rb["P"]:
        if p["ad"] in ("Ust kol tupu", "El", "On kol govdesi", "Govde diregi") and p["modul"] in ("omuz_sag", "dirsek_sag", "iskelet"):
            ozel["%s|%s" % (p["modul"], p["ad"])] = dict(kutle=round(p["kutle"], 2), merkez=r3(p["merkez"]), hacim=round(p["shape"].Volume, 1))
    # bilek servosu alt kumesi (OnKol grubunda, on kol uzayinca bilek ekseniyle birlikte kayar): kol orani varyantlari icin (taslak_hesap)
    alt_kume = OrderedDict()
    for p in Rb["P"]:
        if p["modul"].startswith("dirsek_") and p["grup"] == "OnKol" and p["ad"] in TP.BILEK_ILE:
            k = "%s|OnKol|bilek_ile" % p["modul"]
            kb = kati_bilgi(p["shape"])
            if kb is None:
                vt, cs, Ip = 0.0, p["merkez"], np.zeros((3, 3))
            else:
                vt, cs, I1 = kb
                Ip = I1 * (p["kutle"] / vt)
            g = alt_kume.setdefault(k, dict(m=0.0, mc=np.zeros(3), msc=np.zeros(3), parca=[]))
            g["m"] += p["kutle"]
            g["mc"] += p["kutle"] * np.array([p["merkez"].x, p["merkez"].y, p["merkez"].z])
            g["msc"] += p["kutle"] * np.array([cs.x, cs.y, cs.z])
            g["parca"].append((p["kutle"], np.array([cs.x, cs.y, cs.z]), Ip))
    # on kol govdesinin uzatmanin altinda kalan bolumu (uzama degisince bilek servosuyla birlikte kayar); yalniz taslak (uzatilmis on kol)
    if Rb["ad"] == "yeni" and TA.ON_KOL_UZAMA > 0:
        for p in Rb["P"]:
            if p["modul"].startswith("dirsek_") and p["ad"] == "On kol govdesi":
                y_dir = Rb["AX"][(p["modul"], "dirsek")]["n"].y
                y_kes = y_dir - TA.ON_KOL_KES_S - TA.ON_KOL_UZAMA                 # uzatmanin alt ucu
                bb = p["shape"].BoundBox
                alt = p["shape"].common(Part.makeBox(bb.XLength + 20, y_kes - bb.YMin + 10, bb.ZLength + 20, V(bb.XMin - 10, bb.YMin - 10, bb.ZMin - 10)))
                kb = kati_bilgi(alt)
                vt, cs, I1 = kb
                m = p["kutle"] * vt / p["shape"].Volume
                c = np.array([cs.x, cs.y, cs.z])
                alt_kume["%s|OnKol|on_kol_alt" % p["modul"]] = dict(m=m, mc=m * c, msc=m * c, parca=[(m, c, I1 * (m / vt))], y_kesim=round(y_kes, 3),
                                                                    hacim=round(vt, 1))
    for k, g in list(alt_kume.items()):
        cs = g["msc"] / g["m"]
        I = np.zeros((3, 3))
        for m, cp, Ip in g["parca"]:
            I += paralel(Ip, m, cp - cs)
        alt_kume[k] = dict(m=round(g["m"], 3), c=[round(x, 3) for x in g["mc"] / g["m"]], c_sekil=[round(x, 3) for x in cs], I=I.round(1).tolist(),
                           parca=len(g["parca"]), adlar=list(TP.BILEK_ILE) if k.endswith("bilek_ile") else ["On kol govdesi (uzatmanin alti)"])
        for ek_ in ("y_kesim", "hacim"):
            if ek_ in g:
                alt_kume[k][ek_] = g[ek_]
    return dict(robot=Rb["ad"], taban_w=W if Rb["ad"] == "yeni" else 444, gruplar=out, alt_kume=alt_kume,
                kol=dict(secim=TA.KOL_SECIM, ust_kol=TA.UST_KOL_UZAMA, on_kol=TA.ON_KOL_UZAMA, el=TA.EL_UZAMA, boy=TA.KOL_BOY_YENI,
                         omuz_servo=TA.OMUZ_SERVO["ad"]) if Rb["ad"] == "yeni" else dict(secim="125cm", boy=TA.KOL_BOY_ESKI),
                toplam=dict(m=round(Mtop, 2), c=[round(x, 3) for x in c_top], c_sekil=[round(x, 3) for x in cs_top], I=I_top.round(1).tolist()),
                eksen={"%s|%s" % k: dict(n=r3(v["n"]), u=r3(v["u"], 9), sinir=v["sinir"]) for k, v in Rb["AX"].items()},
                ozel_parca=ozel, birim="g, mm, g*mm2 (atalet: sekil merkezine gore, parca kutlesi hacme uniform)",
                destek_x=round(TP.TP.X_WH + (TA.TABAN_DX if Rb["ad"] == "yeni" else 0.0), 2), destek_z=TP.TP.Z_WH)


# ====================================================================== 2) dogrulama: FCStd + STEP + rastgele ornek
def b_dogrula():
    K = json.load(open(os.path.join(HERE, "kutle.json"), encoding="utf-8"))
    out = dict()
    # (a) taslak_parcalar yeniden kurulum = kutle.json
    m_p = sum(p["kutle"] for p in TP.P)
    c_p = sum((V(p["merkez"]) * p["kutle"] for p in TP.P), V(0, 0, 0)) * (1.0 / m_p)
    out["yeniden_kurulum"] = dict(parca=len(TP.P), kutle_g=round(m_p, 2), am=r3(c_p), kutle_json_kutle_g=K["toplam"]["kutle_g"],
                                  kutle_json_am=K["toplam"]["am"], fark_g=round(m_p - K["toplam"]["kutle_g"], 2))
    sira_ok = all(abs(q["kutle_g"] - round(p["kutle"], 2)) < 0.011 and q["ad"] == p["ad"] for p, q in zip(TP.P, K["parcalar"]))
    out["yeniden_kurulum"]["parca_sirasi_ve_kutle_ayni"] = bool(sira_ok and len(K["parcalar"]) == len(TP.P))
    # (b) FCStd: Kutle_g toplami + sekil merkezleri (bagimsiz AM)
    doc = App.openDocument(os.path.join(HERE, "taslak-170.FCStd"))
    F = [o for o in doc.Objects if o.TypeId == "Part::Feature" and hasattr(o, "Kutle_g")]
    F.sort(key=lambda o: o.Name)
    m_f = sum(o.Kutle_g for o in F)
    gl = {}
    for o in doc.Objects:
        if o.TypeId == "App::Part":
            gl[o.Name] = o.Placement
    c_f = V(0, 0, 0)
    vol_f, vc_f = 0.0, V(0, 0, 0)
    FL = []
    for o in F:
        sh = o.Shape
        kb = kati_bilgi(sh)
        cs = kb[1] if kb else sh.BoundBox.Center
        c_f = c_f + cs * o.Kutle_g
        vol_f += sh.Volume
        vc_f = vc_f + cs * sh.Volume
        FL.append((dict(Kutle_g=float(o.Kutle_g), Label=o.Label, Name=o.Name), cs, sh.Volume))
    c_f = c_f * (1.0 / m_f)
    grup_yer_birim = all(pl.isIdentity() for pl in gl.values())
    out["fcstd"] = dict(nesne=len(F), kutle_g=round(m_f, 2), am_sekil_merkezleriyle=r3(c_f), grup_yerlesimi_birim=grup_yer_birim,
                        hacim_mm3=round(vol_f, 0), not_="AM burada her parcanin FCStd sekil merkezinden (kutle.json 'merkez' alanindan degil)")
    # (c) rastgele ornek: kutle.json <-> FCStd <-> eski karsilik
    random.seed(170)
    idx = sorted(random.sample(range(len(TP.P)), 30))
    for i in [i for i, p in enumerate(TP.P) if p["durum"] in ("degisti",) or p["ad"].startswith(("Govde uzatma bandi", "Yuz ekrani", "Govde diregi"))][:14]:
        if i not in idx:
            idx.append(i)
    RHO = {"PETG": A.PETG_RHO}
    orn = []
    for i in sorted(idx):
        p, q = TP.P[i], K["parcalar"][i]
        o, cs, vol = FL[i]
        e = ESKI["P"][KARSI[i]] if i in KARSI else None
        kay = (p["merkez"] - e["merkez"]) if e else None
        orn.append(dict(
            i=i, ad=p["ad"], modul=p["modul"], durum=p["durum"], malzeme=p["malzeme"], kutle_json_g=q["kutle_g"], fcstd_g=round(o["Kutle_g"], 2),
            fcstd_etiket=o["Label"], hacim_mm3=round(vol, 1), yogunluk_g_cm3=round(o["Kutle_g"] / vol * 1000, 4) if vol > 0 else None,
            merkez_json=q["am"], merkez_fcstd_sekil=r3(cs, 2), merkez_farki_mm=round((V(*q["am"]) - cs).Length, 2),
            eski_kutle_g=round(e["kutle"], 2) if e else None, eski_hacim=round(e["shape"].Volume, 1) if e else None,
            eski_merkez_kaymasi=r3(kay, 2) if kay else None))
    out["ornek"] = orn
    App.closeDocument(doc.Name)
    # (d) STEP: kati sayisi, toplam hacim, hacim agirlikli merkez, FCStd ile eslesme ve STEP geometrisiyle kutle agirlikli AM
    st = Part.read(os.path.join(HERE, "taslak-170.step"))
    S = st.Solids
    vs = np.array([s.Volume for s in S])
    cs_ = np.array([[s.CenterOfMass.x, s.CenterOfMass.y, s.CenterOfMass.z] for s in S])
    fv = np.array([v for _, _, v in FL])
    fc = np.array([[c.x, c.y, c.z] for _, c, _ in FL])
    fm = np.array([o["Kutle_g"] for o, _, _ in FL])
    eslesen, mc, mm, kalan = 0, np.zeros(3), 0.0, set(range(len(FL)))
    en_kotu = 0.0
    for k in range(len(S)):
        d = np.linalg.norm(fc - cs_[k], axis=1) + np.abs(fv - vs[k]) / np.maximum(fv, 1e-9) * 10.0
        j = int(np.argmin(d))
        if d[j] < 0.5:
            eslesen += 1
            kalan.discard(j)
            mc += fm[j] * cs_[k]
            mm += fm[j]
            en_kotu = max(en_kotu, float(d[j]))
    out["step"] = dict(kati=len(S), toplam_hacim_mm3=round(float(vs.sum()), 0), hacim_merkezi=[round(x, 2) for x in (vs[:, None] * cs_).sum(0) / vs.sum()],
                       fcstd_hacim_merkezi=r3(vc_f * (1.0 / vol_f), 2), eslesen_kati=eslesen, eslesmeyen_fcstd=len(kalan),
                       step_geometrisi_kutle_agirlikli_am=[round(x, 2) for x in mc / max(mm, 1e-9)], eslesen_kutle_g=round(mm, 1),
                       en_kotu_eslesme_olcutu=round(en_kotu, 4))
    # (e) kafa: tilt grubu AM'sinin eksene uzakligi (sekil merkezleriyle) ve pan grubu
    AX = YENI["AX"]
    bas = [p for p in YENI["P"] if p["modul"] == "kafa" and p["grup"] == "Bas"]
    boy = [p for p in YENI["P"] if p["modul"] == "kafa" and p["grup"] == "Boyun"]

    def am_sekil(L):
        m = sum(p["kutle"] for p in L)
        c = V(0, 0, 0)
        for p in L:
            kb = kati_bilgi(p["shape"])
            c = c + (kb[1] if kb else p["merkez"]) * p["kutle"]
        return m, c * (1.0 / m)

    def eksen_uz(c, a):
        d = c - a["n"]
        return (d - a["u"] * d.dot(a["u"])).Length

    mb, cb = am_sekil(bas)
    mpb, cpb = am_sekil(bas + boy)
    mbr = sum(p["kutle"] for p in bas)
    cbr = sum((p["merkez"] * p["kutle"] for p in bas), V(0, 0, 0)) * (1.0 / mbr)
    out["kafa"] = dict(tilt_grubu_g=round(mb, 1), tilt_am_sekil=r3(cb, 3), tilt_am_eksene_dik_mm_sekil=round(eksen_uz(cb, AX[("kafa", "tilt")]), 3),
                       tilt_am_eksene_dik_mm_merkez_alani=round(eksen_uz(cbr, AX[("kafa", "tilt")]), 3),
                       pan_grubu_g=round(mpb, 1), pan_am_eksene_dik_mm_sekil=round(eksen_uz(cpb, AX[("kafa", "pan")]), 2),
                       tilt_ekseni=r3(AX[("kafa", "tilt")]["n"]), pan_ekseni=r3(AX[("kafa", "pan")]["n"]))
    # (f) kol: el ucu ve eksenler
    out["kinematik"] = kinematik_dogrula()
    out["olcu"] = dict(boy_ymax=round(max(p["shape"].BoundBox.YMax for p in YENI["P"]), 2),
                       ymin=round(min(p["shape"].BoundBox.YMin for p in YENI["P"]), 2))
    return out


# ====================================================================== 3) statik: ev pozu tum parca ciftleri
EV_S2 = float(A.OMUZ["yana_aralik"][0])     # K6 (S1 kaseti kontrolu, 25 Ekim 2026): statik kontrol yazilim ev pozunda (S1 0, S2 5)


def b_statik(Rb):
    # K6: FCStd kolu mekanik sifirda (S2 0) tutar; orada kol S1 tamburuna / kaset kapagina biner (6 cift, S2 < 3,75). Kontrol pozu yazilim
    # ev pozu S2 = EV_S2 (omuz Kol + dirsek gruplari kol_M ile); S2 0 yalniz bilgi (cakisma_s2_0). Eklem sifiri degismez.
    P = Rb["P"]
    poz = {"sag": (0.0, EV_S2, 0.0, 0.0), "sol": (0.0, EV_S2, 0.0, 0.0)}
    M = [M_parca(Rb, p, poz) if (p["modul"].startswith(("omuz_", "dirsek_")) and p["grup"] not in ("Govde", "Gobek")) else None
         for p in P]
    SH = [sekil(p, m) for p, m in zip(P, M)]
    bbs = [s_.optimalBoundingBox() for s_ in SH]
    bb0 = [p["shape"].optimalBoundingBox() for p in P]
    for b in bbs + bb0:
        b.enlarge(0.01)
    cak, aday, cak0 = [], 0, []
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            if (M[i] is not None or M[j] is not None) and bb0[i].intersect(bb0[j]):
                v0 = kesisim(P[i]["shape"], P[j]["shape"])
                if v0 > TOL or v0 < 0:
                    cak0.append(dict(a=P[i]["ad"], a_modul=P[i]["modul"], b=P[j]["ad"], b_modul=P[j]["modul"], hacim_mm3=round(v0, 2)))
            if not bbs[i].intersect(bbs[j]):
                continue
            aday += 1
            v = kesisim(SH[i], SH[j])
            if v > TOL or v < 0:
                c = dict(a=P[i]["ad"], a_modul=P[i]["modul"], b=P[j]["ad"], b_modul=P[j]["modul"], hacim_mm3=round(v, 2), i=i, j=j)
                if Rb["ad"] == "yeni":
                    e = eski_karsilik(i, j, poz)
                    c["eski_125_hacim_mm3"] = None if e is None else round(e[1], 2)
                    c["kaynak"] = "mevcut tasarim (125'te de var)" if (e and (e[1] > TOL or e[1] < 0)) else "taslak (yeni)"
                cak.append(c)
        if i % 200 == 0:
            log("  statik", i, "/", len(P), "aday", aday, "cakisma", len(cak))
    return dict(robot=Rb["ad"], parca=len(P), aday_cift=aday, esik_mm3=TOL, cakisma=cak, poz=dict(s1=0.0, s2=EV_S2),
                cakisma_s2_0=cak0,
                not_="yazilim ev pozu (S1 0, S2 %g; kollar asagida, kafa duz; K6); tum parca ciftleri, siki sinir kutusu on elemesi, common "
                     "hacmi. cakisma_s2_0: mekanik sifir (FCStd yerlesimi) yalniz bilgi, hareketli kol parcasi iceren ciftler" % EV_S2)


# ====================================================================== 4) kol zinciri x sabit hedefler (carpisma.py bolum 4 yontemi)
def np_m(M):
    return np.array([[M.A11, M.A12, M.A13, M.A14], [M.A21, M.A22, M.A23, M.A24], [M.A31, M.A32, M.A33, M.A34]])


def bb6(b):
    return np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])


def bosluk_np(b, B):
    d = np.maximum(0.0, np.maximum(B[:, :3] - b[3:], b[:3] - B[:, 3:]))
    return np.sqrt((d * d).sum(1))


def noktalar(p, n_max=3000):
    if "pts" not in p:
        try:
            v = p["shape"].tessellate(0.5)[0]
            pts = np.array([[q.x, q.y, q.z] for q in v])
        except Exception:
            pts = np.zeros((0, 3))
        b = p["shape"].BoundBox
        kose = np.array([[x, y, z] for x in (b.XMin, b.XMax) for y in (b.YMin, b.YMax) for z in (b.ZMin, b.ZMax)])
        if len(pts) < 8:
            pts = kose
        if len(pts) > n_max:
            pts = pts[np.linspace(0, len(pts) - 1, n_max).astype(int)]
        p["pts"] = np.hstack([pts, np.ones((len(pts), 1))])
    return p["pts"]


PAY_SIKI = 0.6     # tessellation (0,5 mm) kirisi icin siki kutu payi


def kutu_siki(p, Mn):
    q = noktalar(p) @ Mn.T
    return np.concatenate([q.min(0) - PAY_SIKI, q.max(0) + PAY_SIKI])


YAKIN, INCE_ESIK, LIM, GOMULU, ESIK_YUZ = 5.0, 5.0, 150.0, 3.0, 40
_YANA = tuple(A.OMUZ["yana_aralik"])
if os.environ.get("TA_S2_MIN"):                           # yontem dogrulamasi: 125 cm yasak bolgesi S2 = 0'da bulunmustu (8-9 Ekim)
    _YANA = (float(os.environ["TA_S2_MIN"]), _YANA[1])
KOL_ARALIK = (tuple(A.OMUZ["one_arka_aralik"]), _YANA, tuple(A.DIRSEK["aralik"]), tuple(A.DIRSEK["bilek_aralik"]))
YANA_MIN = KOL_ARALIK[1][0]
KABA = (list(range(int(KOL_ARALIK[0][0]), int(KOL_ARALIK[0][1]) + 1, 15)),
        sorted(set([int(YANA_MIN)] + [t for t in range(0, int(KOL_ARALIK[1][1]) + 1, 15) if t > YANA_MIN])),
        [0, 30, 60, 90, 105], [-90, 0, 90])
GRUP_UZ = OrderedDict([("Gobek", 1), ("Kol", 2), ("UstKol", 2), ("OnKol", 3), ("El", 4)])
KOL_GRUP = os.environ.get("TA_KOL_GRUP", "hepsi")       # dirsek: yalniz dirsek parcalari hareketli (125 cm carpisma.py kapsami)


def kol_araliginda(sp):
    return all(KOL_ARALIK[k][0] - 1e-9 <= v <= KOL_ARALIK[k][1] + 1e-9 for k, v in enumerate(sp))


def hedef_hazirla(q):
    if "fbb" not in q:
        fs = q["shape"].Faces
        q["faces"] = fs
        q["fbb"] = np.array([bb6(f.BoundBox) for f in fs]) if len(fs) > ESIK_YUZ else None


def tam_olc(s, q, qs, qbb, B):
    """s: hareketli sekil, q: hedef parca (faces icin), qs: hedefin (pozdaki) sekli, qbb: np6."""
    sb = bb6(s.BoundBox)
    if bosluk_np(sb, qbb[None, :])[0] >= B:
        return None
    if qs is q["shape"]:
        hedef_hazirla(q)
        if q["fbb"] is None:
            hs = qs
        else:
            sec = np.nonzero(bosluk_np(sb, q["fbb"]) < B)[0]
            if len(sec) == 0:
                return None
            hs = q["faces"][sec[0]] if len(sec) == 1 else Part.Compound([q["faces"][i] for i in sec])
    else:
        hs = qs
    try:
        d = s.distToShape(hs)[0]
    except Exception:
        d = 0.0
    v = 0.0
    ic = all(sb[k] >= qbb[k] for k in range(3)) and all(sb[k + 3] <= qbb[k + 3] for k in range(3))
    if d < 1e-6 or (d < GOMULU and ic and qs.Solids):
        v = kesisim(s, qs)
        if v > TOL or v < 0:
            d = 0.0
    return d, v


class Onbellek:
    def __init__(self, n=3000):
        self.n, self.d = n, OrderedDict()

    def al(self, k, f):
        if k in self.d:
            self.d.move_to_end(k)
            return self.d[k]
        v = f()
        self.d[k] = v
        if len(self.d) > self.n:
            self.d.popitem(last=False)
        return v


def b_kol(Rb, taraf):
    ts = time.time()
    om, dr = "omuz_" + taraf, "dirsek_" + taraf
    AX = Rb["AX"]
    P = Rb["P"]
    sabit = [p for p in P if p["modul"] in ("iskelet", "kabuk", "taban") or (p["modul"] == "kafa" and p["grup"] == "Govde")
             or (p["modul"].startswith("omuz_") and p["grup"] == "Govde")]
    for q in sabit:
        if "obb" not in q:
            q["obb"] = bb6(q["shape"].optimalBoundingBox())
    SB = np.array([q["obb"] for q in sabit])
    gobek_p = [p for p in P if p["modul"] == om and p["grup"] == "Gobek"]
    har = [p for p in P if (p["modul"] == om and p["grup"] in ("Gobek", "Kol")) or p["modul"] == dr]
    if KOL_GRUP == "dirsek":
        har = [p for p in har if p["modul"] == dr]           # carpisma.py bolum 4 ile ayni kapsam (yalniz dirsek parcalari)
    for p in har:
        noktalar(p)
    mcache = {}

    def M_al(g, sp):
        k = (g, sp)
        if k not in mcache:
            mcache[k] = kol_M(AX, taraf, g, sp)
        return mcache[k]

    gcache = {}

    def gobek(phi):
        if phi not in gcache:
            M = M_al("Gobek", (phi,))
            L = []
            for q in gobek_p:
                s = sekil(q, M)
                L.append((q, s, bb6(s.BoundBox)))
            gcache[phi] = (L, np.array([x[2] for x in L]))
        return gcache[phi]

    scache = Onbellek(4000)

    def tasi(pi, g, sp):
        return scache.al((pi, g, sp), lambda: sekil(har[pi], M_al(g, sp)))

    def kendi_govde(q):
        return q["modul"] == om and q["grup"] == "Govde"

    aday, islenen, olcum = [], set(), {}

    def aday_topla(alt):
        n0 = len(aday)
        for g, sp in alt:
            if (g, sp) in islenen:
                continue
            islenen.add((g, sp))
            Mn = np_m(M_al(g, sp))
            GL, GB = gobek(sp[0])
            for pi, p in enumerate(har):
                if p["grup"] != g:
                    continue
                cb = kutu_siki(p, Mn)
                gs = bosluk_np(cb, SB)
                for j in np.nonzero(gs < LIM)[0]:
                    if g == "Gobek" and kendi_govde(sabit[j]):
                        continue           # omuz ici (gobek <-> kendi govdesi) omuz modulunde tarandi
                    aday.append((float(gs[j]), g, sp, pi, ("s", int(j))))
                if g != "Gobek":
                    gg = bosluk_np(cb, GB)
                    for j in np.nonzero(gg < LIM)[0]:
                        aday.append((float(gg[j]), g, sp, pi, ("g", int(j))))
        return n0

    def hedef(hk, sp):
        if hk[0] == "s":
            q = sabit[hk[1]]
            return q, q["shape"], q["obb"]
        L, _ = gobek(sp[0])
        q, s, b = L[hk[1]]
        return q, s, b

    def mod_ad(hk):
        if hk[0] == "g":
            return "%s gobek" % om
        q = sabit[hk[1]]
        return ("%s govde" % q["modul"]) if q["modul"].startswith(("omuz_", "kafa")) else q["modul"]

    def olc(c, B):
        k = (c[1], c[2], c[3], c[4])
        if k in olcum:
            return olcum[k]
        q, qs, qbb = hedef(c[4], c[2])
        r = tam_olc(tasi(c[3], c[1], c[2]), q, qs, qbb, B)
        if r is not None:
            olcum[k] = r
        return r

    en_iyi = {}

    def degerlendir(n0):
        yeni = sorted(aday[n0:], key=lambda c: c[0])
        n = 0
        for c in yeni:
            if c[0] >= YAKIN:
                break
            r = olc(c, YAKIN)
            n += 1
            if r is not None and r[0] < en_iyi.get(mod_ad(c[4]), (1e9,))[0]:
                en_iyi[mod_ad(c[4])] = (r[0], c)
        for c in yeni:
            m = mod_ad(c[4])
            B = en_iyi.get(m, (LIM,))[0]
            if c[0] >= B:
                continue
            r = olc(c, B)
            n += 1
            if n % 500 == 0:
                log("    kol %s: %d tam olcum" % (taraf, n))
            if r is not None and r[0] < B:
                en_iyi[m] = (r[0], c)
        return n

    kaba = [(phi, th, al, be) for phi in KABA[0] for th in KABA[1] for al in KABA[2] for be in KABA[3]]

    def alt(poz):
        return [(g, tuple(float(x) for x in poz[:n])) for g, n in GRUP_UZ.items()]

    altlar = sorted(set(a for poz in kaba for a in alt(poz)))
    n0 = aday_topla(altlar)
    nt = degerlendir(n0)
    log("kol %s: kaba %d poz, %d alt poz, %d aday, %d tam olcum" % (taraf, len(kaba), len(altlar), len(aday), nt))
    isa = sorted(set((k[0], k[1]) for k, r in olcum.items() if (r[0] < INCE_ESIK or r[1] > TOL or r[1] < 0) and kol_araliginda(k[1])))
    ADIM = ((-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-15, 0, 15))
    ince = set()
    for g, sp in isa:
        for q in itertools.product(*[[sp[k] + d for d in ADIM[k]] for k in range(len(sp))]):
            q = tuple(float(x) for x in q)
            if kol_araliginda(q):
                ince.add((g, q))
    ince = sorted(ince - islenen)
    n0 = aday_topla(ince)
    nt2 = degerlendir(n0)
    log("kol %s: isaretli %d, ince %d alt poz, %d tam olcum" % (taraf, len(isa), len(ince), nt2))

    def bulgu(k, r):
        g, sp, pi, hk = k
        q, _, _ = hedef(hk, sp)
        return dict(grup=g, poz=list(sp), parca=har[pi]["ad"], hedef_modul=mod_ad(hk), hedef=q["ad"], bosluk_mm=round(r[0], 2),
                    hacim_mm3=round(r[1], 1), aralikta=kol_araliginda(sp), _i=har[pi]["i"], _j=q["i"])

    cak = [bulgu(k, r) for k, r in olcum.items() if r[1] > TOL or r[1] < 0]
    # yeni/eski ayrimi: cakisan her (parca, hedef) ciftinin 125 cm robottaki karsiligi ayni pozda
    if Rb["ad"] == "yeni":
        kc = {}
        for b in cak:
            key = (b["_i"], b["_j"])
            poz = {taraf: tuple(b["poz"])}
            e = eski_karsilik(b["_i"], b["_j"], poz)
            b["eski_125_hacim_mm3"] = None if e is None else round(e[1], 1)
            b["kaynak"] = "mevcut tasarim (125'te de var)" if (e and (e[1] > TOL or e[1] < 0)) else "taslak (yeni)"
    mod_min, cift_min = {}, {}
    for k, r in olcum.items():
        b = bulgu(k, r)
        if not b["aralikta"]:
            continue
        if r[0] < mod_min.get(b["hedef_modul"], (1e9,))[0]:
            mod_min[b["hedef_modul"]] = (r[0], b)
        a2 = (b["hedef_modul"], b["parca"], b["hedef"])
        if r[0] < cift_min.get(a2, (1e9,))[0]:
            cift_min[a2] = (r[0], b)
    for b in cak:
        b.pop("_i", None), b.pop("_j", None)

    def temiz(b):
        b = dict(b)
        b.pop("_i", None), b.pop("_j", None)
        return b

    cak_cift = {}
    for b in cak:
        if not b["aralikta"]:
            continue
        a2 = (b["parca"], b["hedef_modul"], b["hedef"], b.get("kaynak", ""))
        c = cak_cift.setdefault(a2, dict(parca=b["parca"], hedef_modul=b["hedef_modul"], hedef=b["hedef"], kaynak=b.get("kaynak", ""),
                                         alt_poz=0, en_buyuk_mm3=0.0, ornek_poz=b["poz"], grup=b["grup"]))
        c["alt_poz"] += 1
        if b["hacim_mm3"] > c["en_buyuk_mm3"]:
            c["en_buyuk_mm3"], c["ornek_poz"] = b["hacim_mm3"], b["poz"]
    return dict(robot=Rb["ad"], taraf=taraf, aralik=dict(one_arka=KOL_ARALIK[0], yana=KOL_ARALIK[1], dirsek=KOL_ARALIK[2], bilek=KOL_ARALIK[3]),
                kaba=dict(one_arka=KABA[0], yana=KABA[1], dirsek=KABA[2], bilek=KABA[3], tam_poz=len(kaba)),
                alt_poz=dict(kaba=len(altlar), ince=len(ince)), tam_olcum=len(olcum),
                cakisan_alt_poz=len(set((b["grup"], tuple(b["poz"])) for b in cak if b["aralikta"])),
                cakisma_ciftleri=sorted(cak_cift.values(), key=lambda c: -c["en_buyuk_mm3"]),
                en_kucuk_bosluk={m: temiz(v[1]) for m, v in sorted(mod_min.items())},
                en_kucuk_ciftler={m: [temiz(v[1]) for v in sorted([v for kk, v in cift_min.items() if kk[0] == m], key=lambda v: v[0])[:12]]
                                  for m in sorted(mod_min)},
                hareketli="omuz gobegi (S1) + ust kol (S1+S2: kol catali, tup, S2 servosu) + dirsek catali + on kol + el",
                hedefler="iskelet, kabuk, taban, kafa govdesi (sabit boyun), iki omuzun govdesi, kendi omuzunun gobegi (S1 ile); gobek <-> kendi "
                         "govdesi omuz ici (haric)",
                sure_s=round(time.time() - ts, 1))


# ---------------------------------------------------------------------- kol <-> kol
def b_kolkol(Rb):
    ts = time.time()
    AX = Rb["AX"]
    P = Rb["P"]

    def kolp(taraf):
        L = [p for p in P if (p["modul"] == "omuz_" + taraf and p["grup"] in ("Gobek", "Kol")) or p["modul"] == "dirsek_" + taraf]
        for p in L:
            noktalar(p)
        return L

    KS, KL = kolp("sag"), kolp("sol")
    ciftler = []
    for phi in (-45, 0, 45, 90, 135):
        for th in (YANA_MIN, 60, 120):
            for al in (0, 60, 105):
                for be in (-90, 90):
                    ciftler.append(("simetrik", (phi, th, al, be), (phi, th, al, be)))
    _y = YANA_MIN
    for (a, b) in (((135, _y), (-45, _y)), ((-45, _y), (135, _y)), ((90, _y), (0, _y)), ((135, 120), (-45, _y)), ((0, 120), (135, _y)),
                   ((90, 30), (-45, 60)), ((45, _y), (-45, _y)), ((120, _y), (-30, _y))):
        for al in (0, 105):
            for be in (-90, 90):
                ciftler.append(("zit", (a[0], a[1], al, be), (b[0], b[1], 105 - al, -be)))
    for th in (YANA_MIN, 15, 30):
        for al in (0, 30, 60, 90, 105):
            for be in (-90, 0, 90):
                ciftler.append(("birlikte one", (90, th, al, be), (90, th, al, -be)))
                ciftler.append(("birlikte one (bilek ayni)", (90, th, al, be), (90, th, al, be)))
    for phi in (60, 75, 105, 120, 135):
        for al in (0, 60, 105):
            ciftler.append(("birlikte one", (phi, YANA_MIN, al, 0), (phi, YANA_MIN, al, 0)))

    def kutular(KX, taraf, poz):
        out = []
        for p in KX:
            M = kol_M(AX, taraf, p["grup"], poz)
            out.append((M, kutu_siki(p, np_m(M))))
        return out

    sonuc = []
    for tip, pr, pl in ciftler:
        cr, cl = kutular(KS, "sag", pr), kutular(KL, "sol", pl)
        BR = np.array([c[1] for c in cr])
        BL = np.array([c[1] for c in cl])
        G = np.sqrt((np.maximum(0.0, np.maximum(BL[None, :, :3] - BR[:, None, 3:], BR[:, None, :3] - BL[None, :, 3:])) ** 2).sum(2))
        en, v_cak = (1e9, None), []
        sira = np.dstack(np.unravel_index(np.argsort(G, axis=None), G.shape))[0]
        for i, j in sira:
            if G[i, j] >= en[0]:
                break
            a = sekil(KS[i], cr[i][0])
            b = sekil(KL[j], cl[j][0])
            d = a.distToShape(b)[0]
            if d < 1e-6:
                v = kesisim(a, b)
                if v > TOL or v < 0:
                    v_cak.append((KS[i]["ad"], KL[j]["ad"], round(v, 1)))
            if d < en[0]:
                en = (d, (KS[i]["ad"], KL[j]["ad"]))
        sonuc.append(dict(tip=tip, sag=list(pr), sol=list(pl), bosluk_mm=round(en[0], 1), cift=en[1], cakisma=v_cak))
    en = min(sonuc, key=lambda s: s["bosluk_mm"])
    log("kol-kol: %d poz cifti, cakisan %d, en kucuk %.1f mm %s" % (len(sonuc), sum(1 for s in sonuc if s["cakisma"]), en["bosluk_mm"], en["cift"]))
    return dict(robot=Rb["ad"], poz_cifti=len(sonuc), cakisan=sum(1 for s in sonuc if s["cakisma"]), en_kucuk=en,
                tip_ozet={t: min([s for s in sonuc if s["tip"] == t], key=lambda s: s["bosluk_mm"]) for t in sorted(set(s["tip"] for s in sonuc))},
                sure_s=round(time.time() - ts, 1))


# ====================================================================== 5) kafa x sabit (pan x tilt)
def kafa_aralik(Rb):
    pa = Rb["AX"][("kafa", "pan")]["sinir"]
    ta = Rb["AX"][("kafa", "tilt")]["sinir"]
    return tuple(pa), tuple(ta)


def b_kafa(Rb):
    ts = time.time()
    AX, P = Rb["AX"], Rb["P"]
    (p0, p1), (t0_, t1) = kafa_aralik(Rb)
    PAN = list(range(int(p0), int(p1) + 1, 5))
    TILT = sorted(set(list(range(int(math.ceil(t0_ / 5.0) * 5), int(t1) + 1, 5)) + [int(t0_), int(t1)]))
    har = [p for p in P if p["modul"] == "kafa" and p["grup"] in ("Boyun", "Bas")]
    boyun = [p for p in P if p["modul"] == "kafa" and p["grup"] == "Boyun"]
    sabit = [p for p in P if p["modul"] in ("iskelet", "kabuk") or (p["modul"] == "kafa" and p["grup"] == "Govde")
             or (p["modul"].startswith("omuz_") and p["grup"] in ("Govde", "Gobek", "Kol")) or p["modul"].startswith("dirsek_")]
    sabit = [q for q in sabit if q["shape"].BoundBox.YMax > AX[("kafa", "pan")]["n"].y - 250]
    for q in sabit:
        if "obb" not in q:
            q["obb"] = bb6(q["shape"].optimalBoundingBox())
    SB = np.array([q["obb"] for q in sabit])
    for p in har:
        noktalar(p)
    olcum, en_iyi = {}, {}
    sc = Onbellek(3000)
    for psi in PAN:
        for th in TILT:
            hp = (float(psi), float(th))
            bcache = {}
            for pi, p in enumerate(har):
                M = kafa_M(AX, p["grup"], hp)
                cb = kutu_siki(p, np_m(M))
                hed = [(float(g), ("s", int(j))) for j, g in enumerate(bosluk_np(cb, SB)) if g < LIM]
                if p["grup"] == "Bas":
                    Mb = kafa_M(AX, "Boyun", hp)
                    for j, q in enumerate(boyun):
                        if j not in bcache:
                            bcache[j] = kutu_siki(q, np_m(Mb))
                        g = bosluk_np(cb, bcache[j][None, :])[0]
                        if g < LIM:
                            hed.append((float(g), ("b", j)))
                hed.sort()
                for g, hk in hed:
                    if hk[0] == "s":
                        q = sabit[hk[1]]
                        mod = ("%s govde" % q["modul"]) if q["modul"].startswith(("omuz_", "kafa")) and q["grup"] == "Govde" else \
                            ("%s (ev pozu)" % q["modul"].split("_")[0] if q["modul"].startswith(("omuz_", "dirsek_")) else q["modul"])
                    else:
                        q = boyun[hk[1]]
                        mod = "kafa boyun (pan grubu)"
                    B = max(YAKIN, en_iyi.get(mod, (LIM,))[0])
                    if g >= B:
                        continue
                    s = sc.al((pi, hp), lambda: sekil(p, M))
                    if hk[0] == "s":
                        r = tam_olc(s, q, q["shape"], q["obb"], B)
                    else:
                        qs = sc.al(("b", hk[1], hp), lambda: sekil(q, Mb))
                        r = tam_olc(s, q, qs, bb6(qs.BoundBox), B)
                    if r is None:
                        continue
                    olcum[(hp, pi, hk)] = (r, mod, q["ad"])
                    if r[0] < en_iyi.get(mod, (1e9,))[0]:
                        en_iyi[mod] = (r[0], dict(poz=list(hp), parca=p["ad"], hedef=q["ad"], bosluk_mm=round(r[0], 2)))
    cak = [dict(poz=list(k[0]), parca=har[k[1]]["ad"], hedef_modul=v[1], hedef=v[2], hacim_mm3=round(v[0][1], 1),
                _i=har[k[1]]["i"], _j=(sabit[k[2][1]]["i"] if k[2][0] == "s" else boyun[k[2][1]]["i"]))
           for k, v in olcum.items() if v[0][1] > TOL or v[0][1] < 0]
    if Rb["ad"] == "yeni":
        for b in cak:
            e = eski_karsilik(b["_i"], b["_j"], {"kafa": tuple(b["poz"])})
            b["eski_125_hacim_mm3"] = None if e is None else round(e[1], 1)
            b["kaynak"] = "mevcut tasarim (125'te de var)" if (e and (e[1] > TOL or e[1] < 0)) else "taslak (yeni)"
    for b in cak:
        b.pop("_i"), b.pop("_j")
    log("kafa x sabit: %d poz, cakisma %d" % (len(PAN) * len(TILT), len(cak)))
    return dict(robot=Rb["ad"], pan=PAN, tilt=TILT, poz=len(PAN) * len(TILT), cakisma=cak,
                en_kucuk_bosluk={m: v[1] for m, v in sorted(en_iyi.items())},
                hedefler="iskelet, kabuk, sabit boyun (Kafa_Govde), iki omuz (govde + ev pozunda gobek/kol), iki kol ev pozunda; Bas <-> Boyun (tilt)",
                sure_s=round(time.time() - ts, 1))


# ====================================================================== 6) kafa x kol
def b_kafakol(Rb, taraf):
    ts = time.time()
    AX, P = Rb["AX"], Rb["P"]
    (p0, p1), (t0_, t1) = kafa_aralik(Rb)
    PAN_K = list(range(int(p0), int(p1) + 1, 15))
    TILT_K = sorted(set(list(range(int(math.ceil(t0_ / 5.0) * 5), int(t1) + 1, 5)) + [int(t0_), int(t1)]))
    HP = [(float(a), float(b)) for a in PAN_K for b in TILT_K]
    bas = [p for p in P if p["modul"] == "kafa" and p["grup"] in ("Boyun", "Bas")]
    kol = [p for p in P if (p["modul"] == "omuz_" + taraf and p["grup"] in ("Gobek", "Kol")) or p["modul"] == "dirsek_" + taraf]
    for p in bas + kol:
        noktalar(p)

    def hkutu(hp):
        return np.array([kutu_siki(p, np_m(kafa_M(AX, p["grup"], hp))) for p in bas])

    HB = {hp: hkutu(hp) for hp in HP}
    U = np.concatenate([np.min([b[:, :3].min(0) for b in HB.values()], 0), np.max([b[:, 3:].max(0) for b in HB.values()], 0)])
    LIMK = 60.0
    kaba = [(phi, th, al, be) for phi in KABA[0] for th in KABA[1] for al in KABA[2] for be in KABA[3]]
    altlar = sorted(set((g, tuple(float(x) for x in poz[:n])) for poz in kaba for g, n in GRUP_UZ.items()))
    kc = {}

    def kkutu(pi, g, sp):
        k = (pi, g, sp)
        if k not in kc:
            kc[k] = kutu_siki(kol[pi], np_m(kol_M(AX, taraf, g, sp)))
        return kc[k]

    items = []
    for g, sp in altlar:
        for pi, p in enumerate(kol):
            if p["grup"] != g:
                continue
            b = kkutu(pi, g, sp)
            if bosluk_np(b, U[None, :])[0] < LIMK:
                items.append((pi, g, sp))
    log("kafa x kol %s: %d kafa pozu, %d kol alt pozu, kafaya yakin kol ogesi %d" % (taraf, len(HP), len(altlar), len(items)))
    sc = Onbellek(4000)

    def ksekil(pi, g, sp):
        return sc.al(("k", pi, g, sp), lambda: sekil(kol[pi], kol_M(AX, taraf, g, sp)))

    def hsekil(hj, hp):
        return sc.al(("h", hj, hp), lambda: sekil(bas[hj], kafa_M(AX, bas[hj]["grup"], hp)))

    olcum = {}

    def olc(pi, g, sp, hj, hp, B):
        k = (pi, g, sp, hj, hp)
        if k in olcum:
            return olcum[k]
        a, b = ksekil(pi, g, sp), hsekil(hj, hp)
        if bosluk_np(bb6(a.BoundBox), bb6(b.BoundBox)[None, :])[0] >= B:
            return None
        d = a.distToShape(b)[0]
        v = kesisim(a, b) if d < 1e-6 else 0.0
        if v > TOL or v < 0:
            d = 0.0
        olcum[k] = (d, v)
        return olcum[k]

    adaylar = []
    if items:
        IB = np.array([kkutu(*it) for it in items])
        for hp in HP:
            Hb = HB[hp]
            Gm = np.sqrt((np.maximum(0.0, np.maximum(Hb[None, :, :3] - IB[:, None, 3:], IB[:, None, :3] - Hb[None, :, 3:])) ** 2).sum(2))
            ii, jj = np.nonzero(Gm < LIMK)
            for a_, b_ in zip(ii, jj):
                adaylar.append((float(Gm[a_, b_]), a_, b_, hp))
    adaylar.sort(key=lambda c: c[0])
    en = (1e9, None)
    nt = 0
    for gap, a_, b_, hp in adaylar:
        if gap >= max(YAKIN, en[0]):
            break
        pi, g, sp = items[a_]
        r = olc(pi, g, sp, b_, hp, max(YAKIN, en[0]))
        nt += 1
        if r is not None and r[0] < en[0]:
            en = (r[0], (pi, g, sp, b_, hp))
    log("kafa x kol %s: kaba %d aday (<%.0f), %d tam olcum, en kucuk %.2f" % (taraf, len(adaylar), LIMK, nt, en[0]))
    # sinir: cakisan / yakin ciftlerin eksen komsulari, yakinsayana dek
    pa, ta = (p0, p1), (t0_, t1)

    def hp_ok(hp):
        return pa[0] - 1e-9 <= hp[0] <= pa[1] + 1e-9 and ta[0] - 1e-9 <= hp[1] <= ta[1] + 1e-9

    ADIM = (5.0, 5.0, 5.0, 15.0)
    tur = 0
    while tur < 30:
        tur += 1
        isa = [k for k, r in olcum.items() if r[0] < INCE_ESIK or r[1] > TOL or r[1] < 0]
        if tur > 1:
            isa = [k for k in isa if olcum[k][1] > TOL or olcum[k][1] < 0]
        yeni = set()
        for (pi, g, sp, hj, hp) in isa:
            for k in range(len(sp)):
                for s_ in (-1, 1):
                    q = list(sp)
                    q[k] += s_ * ADIM[k]
                    q = tuple(q)
                    if kol_araliginda(q):
                        yeni.add((pi, g, q, hj, hp))
            for k in range(2):
                for s_ in (-1, 1):
                    h2 = list(hp)
                    h2[k] += s_ * 5.0
                    h2 = tuple(h2)
                    if hp_ok(h2):
                        yeni.add((pi, g, sp, hj, h2))
        yeni = [k for k in yeni if k not in olcum]
        n_c0 = sum(1 for r in olcum.values() if r[1] > TOL or r[1] < 0)
        for (pi, g, sp, hj, hp) in yeni:
            a = kkutu(pi, g, sp)
            b = kutu_siki(bas[hj], np_m(kafa_M(AX, bas[hj]["grup"], hp)))
            if bosluk_np(a, b[None, :])[0] < INCE_ESIK:
                olc(pi, g, sp, hj, hp, INCE_ESIK)
        n_c1 = sum(1 for r in olcum.values() if r[1] > TOL or r[1] < 0)
        log("  sinir turu %d: %d yeni aday, cakisma %d -> %d" % (tur, len(yeni), n_c0, n_c1))
        if n_c1 == n_c0 and tur > 1:
            break
    cak = []
    for (pi, g, sp, hj, hp), r in olcum.items():
        if r[1] > TOL or r[1] < 0:
            cak.append(dict(kol_grup=g, kol_poz=list(sp), kol_parca=kol[pi]["ad"], kafa_poz=list(hp), kafa_parca=bas[hj]["ad"], hacim_mm3=round(r[1], 1),
                            _i=kol[pi]["i"], _j=bas[hj]["i"]))
    if Rb["ad"] == "yeni":
        for b in cak:
            e = eski_karsilik(b["_i"], b["_j"], {taraf: tuple(b["kol_poz"]), "kafa": tuple(b["kafa_poz"])})
            b["eski_125_hacim_mm3"] = None if e is None else round(e[1], 1)
            b["kaynak"] = "mevcut tasarim (125'te de var)" if (e and (e[1] > TOL or e[1] < 0)) else "taslak (yeni)"
    for b in cak:
        b.pop("_i"), b.pop("_j")
    kural = None
    if cak:
        def ar(i, key):
            vals = [b[key][i] for b in cak if len(b[key]) > i]
            return [min(vals), max(vals)] if vals else None
        kural = dict(one_arka=ar(0, "kol_poz"), yana=ar(1, "kol_poz"), dirsek=ar(2, "kol_poz"), pan=ar(0, "kafa_poz"), tilt=ar(1, "kafa_poz"),
                     kafa_parcalari=sorted(set(b["kafa_parca"] for b in cak)), kol_parcalari=sorted(set(b["kol_parca"] for b in cak)),
                     not_="cakisan alt poz ciftlerinin eksen bazinda kapsadigi aralik (kesin kural: liste)")
    eb = None
    if en[1]:
        pi, g, sp, hj, hp = en[1]
        eb = dict(bosluk_mm=round(en[0], 2), kol_grup=g, kol_poz=list(sp), kol_parca=kol[pi]["ad"], kafa_poz=list(hp), kafa_parca=bas[hj]["ad"])
    # cakismasiz en kucuk bosluk
    temiz = [(r[0], k) for k, r in olcum.items() if not (r[1] > TOL or r[1] < 0)]
    ek = None
    if temiz:
        d, (pi, g, sp, hj, hp) = min(temiz, key=lambda x: x[0])
        ek = dict(bosluk_mm=round(d, 2), kol_grup=g, kol_poz=list(sp), kol_parca=kol[pi]["ad"], kafa_poz=list(hp), kafa_parca=bas[hj]["ad"])
    return dict(robot=Rb["ad"], taraf=taraf, kafa_pan=PAN_K, kafa_tilt=TILT_K, kafa_poz=len(HP), kol_alt_poz=len(altlar), yakin_oge=len(items),
                aday=len(adaylar), tam_olcum=len(olcum), sinir_turu=tur, cakisma_sayisi=len(cak),
                cakisan_tam_cift=len(set((tuple(b["kol_poz"]), tuple(b["kafa_poz"])) for b in cak)),
                cakismalar=sorted(cak, key=lambda b: (b["kol_poz"], b["kafa_poz"]))[:400], yasak_bolge=kural, en_kucuk=eb, en_kucuk_cakismasiz=ek,
                sure_s=round(time.time() - ts, 1))


# ====================================================================== 7) kafa x kol: en dar yer cevresinde ince tarama (kontrol ajani, 24 Ekim 2026)
def b_kafakol_ince(Rb, taraf):
    """Kaba kafa x kol taramasi (pan 15 derece adim) x1,25 kolda en dar yeri kol on-yukari (S1 135, S2 5, dirsek 105) + kafa o kola pan ~30,
    tilt 15'te verdi. Bu bolge kol S1 120...135, S2 5...20, dirsek 85...105 (2,5 derece), bilek 9 aci x kafa pan 0...60 (2 derece, o kola dogru),
    tilt 9 aci ile taranir: on kol + el gruplari (tessellation bulutu) x kafa Boyun + Bas parcalari, siki kutu alt siniriyla dal-sinir (kesin en kucuk)."""
    ts = time.time()
    AX = Rb["AX"]
    sx = 1 if taraf == "sag" else -1
    bas = [p for p in Rb["P"] if p["modul"] == "kafa" and p["grup"] in ("Boyun", "Bas")]
    grp = {g: [p for p in Rb["P"] if p["modul"] == "dirsek_" + taraf and p["grup"] == g] for g in ("OnKol", "El")}
    for p in bas + grp["OnKol"] + grp["El"]:
        noktalar(p)
    PT = {g: np.vstack([p["pts"] for p in L]) for g, L in grp.items()}
    S1 = [120.0, 122.5, 125.0, 127.5, 130.0, 132.5, 135.0]
    S2 = [5.0, 7.5, 10.0, 12.5, 15.0, 20.0]
    DI = [85.0, 87.5, 90.0, 92.5, 95.0, 97.5, 100.0, 102.5, 105.0]
    BI = [-90.0, -75.0, -60.0, -45.0, -30.0, 0.0, 30.0, 60.0, 90.0]
    PAN = [sx * float(a) for a in range(0, 61, 2)]
    TILT = [-15.0, -10.0, -5.0, 0.0, 5.0, 7.5, 10.0, 12.5, 15.0]
    HP = [(a, b) for a in PAN for b in TILT]
    HBf = np.array([[kutu_siki(q, np_m(kafa_M(AX, q["grup"], hp))) for q in bas] for hp in HP]).reshape(-1, 6)
    aday = []
    for sp in itertools.product(S1, S2, DI, BI):
        for g in ("OnKol", "El"):
            q = PT[g] @ np_m(kol_M(AX, taraf, g, sp)).T
            b = np.concatenate([q.min(0) - PAY_SIKI, q.max(0) + PAY_SIKI])
            gap = bosluk_np(b, HBf)
            for k in np.nonzero(gap < 12.0)[0]:
                aday.append((float(gap[k]), sp, g, int(k // len(bas)), int(k % len(bas))))
    aday.sort(key=lambda c: c[0])
    log("kafa x kol ince %s: %d kol x %d kafa pozu, %d aday (<12 mm)" % (taraf, len(S1) * len(S2) * len(DI) * len(BI), len(HP), len(aday)))
    sc = Onbellek(3000)

    def ksekil(g, sp):
        return sc.al(("k", g, sp), lambda: Part.Compound([sekil(p, kol_M(AX, taraf, g, sp)) for p in grp[g]]))

    def hsekil(j, hp):
        return sc.al(("h", j, hp), lambda: sekil(bas[j], kafa_M(AX, bas[j]["grup"], hp)))

    en, n, cak = (1e9, None), 0, []
    for gap, sp, g, ih, j in aday:
        if gap >= en[0]:
            break
        hp = HP[ih]
        a, b = ksekil(g, sp), hsekil(j, hp)
        d = a.distToShape(b)[0]
        n += 1
        if d < 1e-6:
            v = sum(kesisim(s, b) for s in a.Solids)
            if v > TOL or v < 0:
                cak.append(dict(kol_poz=list(sp), kol_grup=g, kafa_poz=list(hp), kafa_parca=bas[j]["ad"], hacim_mm3=round(v, 2)))
                continue
        if d < en[0]:
            en = (d, dict(bosluk_mm=round(d, 2), kol_poz=list(sp), kol_grup=g, kafa_poz=list(hp), kafa_parca=bas[j]["ad"]))
    log("kafa x kol ince %s: %d tam olcum, en kucuk %s, cakisma %d" % (taraf, n, en[1], len(cak)))
    return dict(robot=Rb["ad"], taraf=taraf, izgara=dict(S1=S1, S2=S2, dirsek=DI, bilek=BI, pan=PAN, tilt=TILT),
                kol_poz=len(S1) * len(S2) * len(DI) * len(BI), kafa_poz=len(HP), aday_12mm=len(aday), tam_olcum=n, cakisma=cak, en_kucuk=en[1],
                not_="kaba kafakol taramasinin en dar yeri cevresi; on kol + el gruplari x kafa Boyun + Bas; siki kutu alt siniri + dal-sinir",
                sure_s=round(time.time() - ts, 1))


# ====================================================================== 8) dirsek catali dis kolu 5 -> TA.CATAL_DIS_KOL (kontrol ajani, 24 Ekim 2026)
def b_catal(Rb):
    """Ayni hedeflere eski (5 mm, TP.CATAL_ESKI: catal + M3x8), ara (TP.CATAL_ARA, 8 mm kosusunda 7 mm + M3x10) ve yeni catal (TP.P: catal +
    horn civatalari + bas alti pul yigini; 8 mm: M3x12 + 2x DIN 125-A, kontrol ajani 24 Ekim 2026 gece) iki kolda:
    (a) dirsek ekseni boyunca 0...105 (1 derece) on kol (OnKol) + el (El, bilek -90/0/90) parcalarina; es eksenli parcalar (mil, rulman ic
        bilezigi, pim, pul) ayri raporlanir (mesafe aciyla degismez, temas beklenir: hacim kesisimi olculur);
    (b) omuz S1 x S2 ince izgara (5 derece, aralik ici) sabit hedeflere: iskelet, kabuk, taban, kafa (ev pozu, tum gruplar), iki omuz govdesi,
        kendi gobegi (S1 ile), karsi kol (ev pozu). En kucuk bosluk ve kesisim hacmi (eski / yeni)."""
    ts = time.time()
    AX, P = Rb["AX"], Rb["P"]
    KOAKS = ("Dirsek servosu cikis mili", "625ZZ rulman (ic bilezik)", "Pim pulu M5", "Pim civatasi M5x12")
    out = dict(kalinlik_mm=TA.CATAL_DIS_KOL, eski_mm=TA.CATAL_DIS_KOL_ESKI, ara_mm=list(TP.CATAL_ARA_T), koaks=list(KOAKS), taraf={},
               civata=dict(boy=TA.HORN_CIVATA_L, pul_n=TA.HORN_PUL_N, pul_mm=TA.HORN_PUL_T))
    S1g = list(range(int(KOL_ARALIK[0][0]), int(KOL_ARALIK[0][1]) + 1, 5))
    S2g = sorted(set([int(YANA_MIN)] + [t for t in range(0, int(KOL_ARALIK[1][1]) + 1, 5) if t > YANA_MIN]))
    out["izgara"] = dict(dirsek=[0, 105, 1], bilek_el=[-90, 0, 90], S1=S1g, S2=S2g)

    def setler(taraf):
        dr = "dirsek_" + taraf
        yc = [p["shape"] for p in P if p["modul"] == dr and p["ad"] == "Dirsek catali"]
        yv = [p["shape"] for p in P if p["modul"] == dr and p["ad"].startswith("Catal-horn civatasi")]
        yp = [p["shape"] for p in P if p["modul"] == dr and p["ad"].startswith("Catal-horn pulu")]       # bas alti pul yigini (8 mm: 2x DIN 125-A)
        E = TP.CATAL_ESKI[taraf]
        assert len(yc) == 1 and len(yv) == 4 and len(yp) == (4 if TA.HORN_PUL_N else 0)
        assert len(E["Dirsek catali"]) == 1 and len(E["Catal-horn civatasi M3x8"]) == 4
        S = OrderedDict([("yeni_catal", yc), ("yeni_civata", yv + yp), ("eski_catal", E["Dirsek catali"]), ("eski_civata", E["Catal-horn civatasi M3x8"])])
        for ta in TP.CATAL_ARA_T:                                       # ara kalinlik (8 mm kosusunda 7 mm + M3x10): ayni hedeflere
            C = TP.CATAL_ARA[ta][taraf]
            assert len(C["Dirsek catali"]) == 1 and len(C["civata"]) == 4
            S["ara%g_catal" % ta] = C["Dirsek catali"]
            S["ara%g_civata" % ta] = C["civata"] + C["pul"]
        return S

    def olc(shs, hs, pay):
        hb = hs.BoundBox
        en, v = None, 0.0
        for s in shs:
            b = App.BoundBox(s.BoundBox)
            b.enlarge(pay)
            if not b.intersect(hb):
                continue
            d = s.distToShape(hs)[0]
            if d < 1e-6:
                vv = kesisim(s, hs)
                v += vv if vv > 0 else 0.0
            en = d if en is None else min(en, d)
        return en, v

    for taraf in ("sag", "sol"):
        dr, om = "dirsek_" + taraf, "omuz_" + taraf
        ST = setler(taraf)
        T = dict(dirsek=[], dirsek_parca={}, omuz=[], omuz_parca={})
        # (a) dirsek ekseni
        hed = [p for p in P if p["modul"] == dr and p["grup"] in ("OnKol", "El")]
        for al in range(0, 106):
            for be in ((-90, 0, 90) if True else (0,)):
                if be != 0 and al % 5:
                    continue                                    # el (bilek) yalniz 5 derecede bir; on kol her derecede
                kay = {}
                for q in hed:
                    if q["grup"] == "El":
                        M = kol_M(AX, taraf, "El", (0.0, 0.0, float(al), float(be)))
                    elif be != 0:
                        continue
                    else:
                        M = kol_M(AX, taraf, "OnKol", (0.0, 0.0, float(al)))
                    qs = sekil(q, M)
                    for k, shs in ST.items():
                        d, v = olc(shs, qs, 25.0)
                        if d is None:
                            continue
                        kk = (q["ad"], k)
                        r = T["dirsek_parca"].setdefault("%s|%s" % kk, dict(parca=q["ad"], grup=q["grup"], set=k, koaks=q["ad"] in KOAKS,
                                                                           en_az_mm=1e9, poz=None, en_cok_hacim_mm3=0.0))
                        if d < r["en_az_mm"]:
                            r["en_az_mm"], r["poz"] = round(d, 3), [al, be]
                        r["en_cok_hacim_mm3"] = max(r["en_cok_hacim_mm3"], round(v, 3))
                        if q["ad"] not in KOAKS:
                            kay.setdefault(k, []).append((d, q["ad"], v))
                if kay:
                    T["dirsek"].append(dict(dirsek=al, bilek=be, **{k: [round(min(x)[0], 3), min(x)[1], round(sum(y[2] for y in x), 3)] for k, x in kay.items()}))
        log("catal %s: dirsek ekseni bitti (%d satir)" % (taraf, len(T["dirsek"])))
        # (b) omuz izgarasi
        sabit = [p for p in P if p["modul"] in ("iskelet", "kabuk", "taban", "kafa") or (p["modul"].startswith("omuz_") and p["grup"] == "Govde")
                 or (p["modul"] in ("omuz_" + ("sol" if taraf == "sag" else "sag"), "dirsek_" + ("sol" if taraf == "sag" else "sag")))]
        gob = [p for p in P if p["modul"] == om and p["grup"] == "Gobek"]
        gob_id = set(id(q) for q in gob)
        for q in sabit + gob:
            if "obb" not in q:
                q["obb"] = bb6(q["shape"].optimalBoundingBox())
        SB = np.array([q["obb"] for q in sabit])
        for phi in S1g:
            Mg = kol_M(AX, taraf, "Gobek", (float(phi),))
            gs = [(q, sekil(q, Mg)) for q in gob]
            for th in S2g:
                M = kol_M(AX, taraf, "UstKol", (float(phi), float(th)))
                tst = OrderedDict((k, [s.copy() for s in shs]) for k, shs in ST.items())
                for shs in tst.values():
                    for s in shs:
                        s.transformShape(M)
                ub = np.concatenate([np.min([bb6(s.BoundBox)[:3] for shs in tst.values() for s in shs], 0) - 30.0,
                                     np.max([bb6(s.BoundBox)[3:] for shs in tst.values() for s in shs], 0) + 30.0])
                yak = [sabit[j] for j in np.nonzero(bosluk_np(ub, SB) < 1e-9)[0]]
                satir = dict(poz=[phi, th])
                for q, qs in [(q, q["shape"]) for q in yak] + gs:
                    for k, shs in tst.items():
                        d, v = olc(shs, qs, 30.0)
                        if d is None:
                            continue
                        hm = q["modul"] + (" gobek" if id(q) in gob_id else "")
                        r = T["omuz_parca"].setdefault("%s|%s|%s" % (hm, q["ad"], k), dict(hedef=q["ad"], hedef_modul=hm, set=k, en_az_mm=1e9, poz=None,
                                                                                         en_cok_hacim_mm3=0.0))
                        if d < r["en_az_mm"]:
                            r["en_az_mm"], r["poz"] = round(d, 3), [phi, th]
                        r["en_cok_hacim_mm3"] = max(r["en_cok_hacim_mm3"], round(v, 3))
                        if k not in satir or d < satir[k][0]:
                            satir[k] = [round(d, 3), q["ad"], round(v, 3)]
                T["omuz"].append(satir)
        log("catal %s: omuz izgarasi bitti (%d poz)" % (taraf, len(T["omuz"])))

        def ozet(rows, k):
            v = [(r[k][0], r) for r in rows if k in r]
            if not v:
                return None
            d, r = min(v, key=lambda x: x[0])
            return dict(mm=d, parca=r[k][1], poz=r.get("poz", [r.get("dirsek"), r.get("bilek")]), hacim_toplam_mm3=sum(x[1][k][2] for x in v))
        T["ozet"] = {bol: {k: ozet(T[bol], k) for k in ST} for bol in ("dirsek", "omuz")}
        T["dirsek_parca"] = sorted(T["dirsek_parca"].values(), key=lambda r: (r["koaks"], r["en_az_mm"]))
        T["omuz_parca"] = sorted(T["omuz_parca"].values(), key=lambda r: r["en_az_mm"])
        out["taraf"][taraf] = T
    out["sure_s"] = round(time.time() - ts, 1)
    return out


def b_catal_geo():
    """Dirsek catali dis kolu geometri kontrolu (TA.CATAL_DIS_KOL ile kurulan TP.P): yeni catal ↔ 5 mm catal (TP.CATAL_ESKI), delikler, horn
    civatalari + bas alti pul yigini (bas temasi, uc, horn'da kavrama, servo kasasina / cikis miline mesafe dirsek ekseni araliginda 1 derece),
    45 der. destek ↔ ust kol tupu, eksenler, baski olcusu ve tum parca listesi ozeti (hacim, sinir kutusu, merkez).
    Cikti adi: ortamda TASLAK_CATAL_DIS_KOL verilmisse catal-geo-<t>.json (5 / 7 karsilastirma kosulari), yoksa catal-geo.json; varsayilan kosu
    catal-geo-5.json ve catal-geo-7.json ile parca parca karsilastirir (pul parcalari ayri sayilir, kalan parcalar ayni sirada eslenir).
    Kontrol ajani 24 Ekim 2026 (gece): pullar (8 mm: M3x12 + 2x DIN 125-A) eklendi; TA_KUTLE_REF=<kutle.json> verilirse onunla da karsilastirir."""
    def bb(s):
        b = s.BoundBox
        return [round(x, 4) for x in (b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax)]

    PUL = "Catal-horn pulu"
    out = dict(kalinlik_mm=TA.CATAL_DIS_KOL, eski_mm=TA.CATAL_DIS_KOL_ESKI, taraf={},
               civata=dict(boy=TA.HORN_CIVATA_L, pul_n=TA.HORN_PUL_N, pul_mm=TA.HORN_PUL_T, destek_dis=TA.CATAL_DESTEK_DIS))
    out["parca"] = [dict(ad=p["ad"], modul=p["modul"], kutle=round(float(p["kutle"]), 4), hacim=round(p["shape"].Volume, 3), bb=bb(p["shape"]),
                         merkez=r3(V(p["merkez"]), 4)) for p in TP.P]
    out["eksen"] = {"%s|%s" % k: dict(n=r3(v["n"], 5), u=r3(v["u"], 7)) for k, v in YENI["AX"].items()}
    for taraf in ("sag", "sol"):
        dr, om = "dirsek_" + taraf, "omuz_" + taraf
        bul = lambda ad, m=dr: [p["shape"] for p in TP.P if p["modul"] == m and p["ad"] == ad][0]
        cat, horn, servo, mil = bul("Dirsek catali"), bul("Dirsek horn 25T aluminyum disk"), bul("Dirsek servosu MG996R"), bul("Dirsek servosu cikis mili")
        tup = bul("Ust kol tupu", om)
        civ = [p["shape"] for p in TP.P if p["modul"] == dr and p["ad"].startswith("Catal-horn civatasi")]
        pul = [p["shape"] for p in TP.P if p["modul"] == dr and p["ad"].startswith(PUL)]
        E5 = TP.CATAL_ESKI[taraf]
        cat5, civ5 = E5["Dirsek catali"][0], E5["Catal-horn civatasi M3x8"]
        ax = YENI["AX"][(dr, "dirsek")]
        dis = 1.0 if taraf == "sag" else -1.0                               # disari (govdeden uzak) yon, global X
        hb, cb, cb5 = horn.BoundBox, cat.BoundBox, cat5.BoundBox
        ek, cik = cat.cut(cat5), cat5.cut(cat)
        K = dict(catal_bb=bb(cat), catal5_bb=bb(cat5), catal_hacim=round(cat.Volume, 2), catal5_hacim=round(cat5.Volume, 2), gecerli=cat.isValid(),
                 kati=len(cat.Solids), eklenen_hacim=round(ek.Volume, 2), eklenen_bb=bb(ek) if ek.Volume > 1e-6 else None, cikan_hacim=round(cik.Volume, 4),
                 horn_x=[round(hb.XMin, 3), round(hb.XMax, 3)], servo_bb=bb(servo), eksen=dict(n=r3(ax["n"], 4), u=r3(ax["u"], 6)),
                 dis_yuz_x=round(cb.XMax if taraf == "sag" else cb.XMin, 3), dis_yuz5_x=round(cb5.XMax if taraf == "sag" else cb5.XMin, 3),
                 ic_yuz_x=round(cb.XMin if taraf == "sag" else cb.XMax, 3), ic_yuz5_x=round(cb5.XMin if taraf == "sag" else cb5.XMax, 3),
                 baski_olcu=sorted([round(cb.XLength, 2), round(cb.YLength, 2), round(cb.ZLength, 2)], reverse=True), tabla=TA.TABLA, hedef=TA.TABLA_HEDEF)
        K["tabla_sigar"] = max(K["baski_olcu"]) <= TA.TABLA_HEDEF
        if ek.Volume > 1e-6:                          # eklenen hacim: eski dis yuz duzleminin disi (dis kol + kopru) ve ici (yalniz 45 der. destek eki olmali)
            x5 = cb5.XMax if taraf == "sag" else cb5.XMin
            kut = Part.makeBox(400, 400, 400, V(x5 if taraf == "sag" else x5 - 400, cb.YMin - 100, cb.ZMin - 100))
            ek_d = ek.common(kut)
            ek_i = ek.cut(kut)
            K["eklenen_dis"] = dict(hacim=round(ek_d.Volume, 2), bb=bb(ek_d) if ek_d.Volume > 1e-6 else None)
            K["eklenen_ic"] = dict(hacim=round(ek_i.Volume, 2), bb=bb(ek_i) if ek_i.Volume > 1e-6 else None,
                                   horn_mm=round(ek_i.distToShape(horn)[0], 3) if ek_i.Volume > 1e-6 else None,
                                   servo_mm=round(ek_i.distToShape(servo)[0], 3) if ek_i.Volume > 1e-6 else None)
        # 45 der. destek ve tup: ust kol tupu ile ortak hacim / mesafe (5 mm ile ayni olmali: oturma temasi), eklenen hacim ↔ tup mesafesi
        K["tup"] = dict(ortak_mm3=round(cat.common(tup).Volume, 4), ortak5_mm3=round(cat5.common(tup).Volume, 4), mesafe_mm=round(cat.distToShape(tup)[0], 4),
                        eklenen_tupe_mm=round(ek.distToShape(tup)[0], 4) if ek.Volume > 1e-6 else None)
        dl = []
        for s in civ:                                 # delik acik mi: civata ekseninde r 1,6 silindir, catal boyunca: yeni ve eski catalla ayni ortak hacim
            b = s.BoundBox
            cy = Part.makeCylinder(1.6, cb.XLength + 2, V(cb.XMin - 1, (b.YMin + b.YMax) / 2, (b.ZMin + b.ZMax) / 2), V(1, 0, 0))
            dl.append(dict(yz=[round((b.YMin + b.YMax) / 2, 3), round((b.ZMin + b.ZMax) / 2, 3)], yeni_mm3=round(cat.common(cy).Volume, 4),
                           eski_mm3=round(cat5.common(cy).Volume, 4)))
        K["horn_delikleri"] = dl
        xd = hb.XMax if taraf == "sag" else hb.XMin - 30
        cy = Part.makeCylinder(4.4, cb.XLength + 2, V(cb.XMin - 1, ax["n"].y, ax["n"].z), V(1, 0, 0)).common(
            Part.makeBox(30, 200, 200, V(xd, ax["n"].y - 100, ax["n"].z - 100)))
        K["merkez_erisim_ortak_mm3"] = dict(yeni=round(cat.common(cy).Volume, 4), eski=round(cat5.common(cy).Volume, 4))
        ky = lambda s: (round(s.BoundBox.Center.y, 2), round(s.BoundBox.Center.z, 2))
        pul_k = {ky(q): q for q in pul}
        cv = []
        for s, s5 in zip(sorted(civ, key=ky), sorted(civ5, key=ky)):
            b, b5 = s.BoundBox, s5.BoundBox
            uc, uc5 = (b.XMin, b5.XMin) if taraf == "sag" else (b.XMax, b5.XMax)
            r = dict(yz=list(ky(s)), eski_yz=list(ky(s5)), uc_x=round(uc, 3), eski_uc_x=round(uc5, 3), boy=round(b.XLength, 3), eski_boy=round(b5.XLength, 3),
                     bas_catal_mm=round(s.distToShape(cat)[0], 4), catal_ortak_mm3=round(s.common(cat).Volume, 4),
                     horn_kavrama_mm=round(min(hb.XMax, b.XMax) - max(hb.XMin, b.XMin), 3),
                     eski_horn_kavrama_mm=round(min(hb.XMax, b5.XMax) - max(hb.XMin, b5.XMin), 3),
                     uc_horn_alti_mm=round((hb.XMin - uc) if taraf == "sag" else (uc - hb.XMax), 3))      # < 0: uc horn icinde (cikmiyor)
            q = pul_k.get(ky(s))
            if q is not None:                         # pul yigini: catal dis yuzune oturur, bas pulun ustunde, ortak hacim yok, tam destekli mi
                qb = q.BoundBox
                q_ic = q.copy()
                q_ic.translate(V(-dis * qb.XLength, 0, 0))   # yigin kalinligi kadar iceri kaydirilmis kopya: pulun altinda catal malzemesi (oturma alani orani)
                alt_x = qb.XMin if taraf == "sag" else qb.XMax
                r["pul"] = dict(x=[round(qb.XMin, 3), round(qb.XMax, 3)], kalinlik=round(qb.XLength, 3), dis_cap=round(max(qb.YLength, qb.ZLength), 3),
                                alt_dis_yuze_mm=round(dis * (alt_x - K["dis_yuz_x"]), 4), catal_mm=round(q.distToShape(cat)[0], 4),
                                catal_ortak_mm3=round(q.common(cat).Volume, 4), civata_mm=round(q.distToShape(s)[0], 4),
                                civata_ortak_mm3=round(q.common(s).Volume, 4), hacim=round(q.Volume, 3), kati=len(q.Solids),
                                oturma_orani=round(q_ic.common(cat).Volume / q.Volume, 4),
                                kenar_bosluk_mm=round(min(qb.YMin - cb.YMin, cb.YMax - qb.YMax, qb.ZMin - cb.ZMin, cb.ZMax - qb.ZMax), 3))
            cv.append(r)
        K["civatalar"] = cv
        K["pul_sayisi"] = len(pul)
        # dirsek ekseni araligi (1 derece): servo govdesi ve cikis mili (kubbe) on kolla doner; civata + pul (catal tarafi) sabit
        lo, hi = KOL_ARALIK[2]
        sv = []
        for al in range(int(math.floor(lo)), int(math.ceil(hi)) + 1):
            M = Rm(ax, al)
            s_, m_ = servo.copy(), mil.copy()
            s_.transformShape(M)
            m_.transformShape(M)
            sv.append([al, round(min(s.distToShape(s_)[0] for s in civ + pul), 3), round(min(s.distToShape(s_)[0] for s in civ5), 3),
                       round(min(s.distToShape(m_)[0] for s in civ + pul), 3), round(min(s.distToShape(m_)[0] for s in civ5), 3)])
        K["civata_servo_kasasi"] = dict(yeni_en_az=min(x[1] for x in sv), eski_en_az=min(x[2] for x in sv), satir=[x[:3] for x in sv], aralik=[lo, hi])
        K["civata_cikis_mili"] = dict(yeni_en_az=min(x[3] for x in sv), eski_en_az=min(x[4] for x in sv),
                                     sabit=(max(x[3] for x in sv) - min(x[3] for x in sv)) < 1e-3)
        out["taraf"][taraf] = K

    def esle(A_, B_):
        """Pul parcalari disinda ayni sirada eslenen parca farklari (ad / kutle / bb)."""
        a_ = [x for x in A_ if not x["ad"].startswith(PUL)]
        b_ = [x for x in B_ if not x["ad"].startswith(PUL)]
        fark = [dict(i=i, modul=a["modul"], ad_ref=a["ad"], ad=b["ad"], kutle_ref=a["kutle"], kutle=b["kutle"], bb_ref=a["bb"], bb=b["bb"])
                for i, (a, b) in enumerate(zip(a_, b_)) if a != b]
        return dict(parca_ref=len(A_), parca=len(B_), pul_ref=len(A_) - len(a_), pul=len(B_) - len(b_), esit_sayi=len(a_) == len(b_), farkli=fark,
                    kutle_ref=round(sum(p["kutle"] for p in A_), 3), kutle=round(sum(p["kutle"] for p in B_), 3))

    if os.environ.get("TASLAK_CATAL_DIS_KOL") is None:
        for tr in (5, 7):
            yol = os.path.join(OUT, "catal-geo-%d.json" % tr)
            if os.path.exists(yol):
                g = json.load(open(yol, encoding="utf-8"))
                out["fark_%d" % tr] = dict(esle(g["parca"], out["parca"]), eksen_ayni=g["eksen"] == out["eksen"])
                out["fark_%d" % tr]["pul_parca"] = [dict(modul=p["modul"], ad=p["ad"], kutle=p["kutle"]) for p in out["parca"] if p["ad"].startswith(PUL)]
    ref = os.environ.get("TA_KUTLE_REF")              # ornek: 7 mm kosusunun kutle.json kopyasi (birebir uretim kontrolu)
    if ref and os.path.exists(ref):
        K5 = json.load(open(ref, encoding="utf-8"))["parcalar"]
        out["fark_kutle_ref"] = dict(yol=ref, parca_ref=len(K5), parca=len(out["parca"]), farkli=[
            dict(i=i, ad=a["ad"], kutle=a["kutle"], kutle_json=b["kutle_g"]) for i, (a, b) in enumerate(zip(out["parca"], K5))
            if a["ad"] != b["ad"] or abs(a["kutle"] - b["kutle_g"]) > 0.006 or max(abs(x - y) for x, y in zip(a["merkez"], b["am"])) > 0.006])
    try:                                                # git 8ee72a0 kutle.json (catal oncesi, 5 mm) ile ad / kutle / merkez (pullar haric)
        import subprocess
        r = subprocess.run(["git", "-C", HERE, "show", "%s:tasarim/freecad/taslak-170/kutle.json" % CATAL5_GIT], capture_output=True, check=True)
        K5 = json.loads(r.stdout.decode("utf-8"))["parcalar"]
        pp = [p for p in out["parca"] if not p["ad"].startswith(PUL)]
        out["fark_kutle_json_%s" % CATAL5_GIT] = [dict(i=i, ad=a["ad"], kutle=a["kutle"], kutle_json=b["kutle_g"]) for i, (a, b) in enumerate(zip(pp, K5))
                                                 if a["ad"] != b["ad"] or abs(a["kutle"] - b["kutle_g"]) > 0.006 or
                                                 max(abs(x - y) for x, y in zip(a["merkez"], b["am"])) > 0.006]
    except Exception as e:
        out["fark_kutle_json_hata"] = str(e)
    return out


CATAL5_GIT = "8ee72a0"          # dirsek catali 5 mm iken son kontrol kosusu (kutle.json, analiz/*.json, kol-analiz)


# ====================================================================== kosucu
for b in BOLUM:
    tb = time.time()
    if b == "kutle":
        yaz("girdi-yeni-%d.json" % W, b_kutle(YENI))
        if W == 444:
            yaz("girdi-eski-444.json", b_kutle(ESKI))
    elif b == "dogrula":
        yaz("dogrulama.json", b_dogrula())
    elif b == "statik":
        yaz("statik-%s-%d.json" % (R["ad"], W), b_statik(R))
    elif b in ("kol_sag", "kol_sol"):
        yaz("%s-%s%s.json" % (b, R["ad"], "-dirsek" if KOL_GRUP == "dirsek" else ""), b_kol(R, b.split("_")[1]))
    elif b == "kolkol":
        yaz("kolkol-%s.json" % R["ad"], b_kolkol(R))
    elif b == "kafa":
        yaz("kafa-%s.json" % R["ad"], b_kafa(R))
    elif b == "catal":
        yaz("catal-%s.json" % R["ad"], b_catal(R))
    elif b == "catal_geo":
        yaz(("catal-geo-%g.json" % TA.CATAL_DIS_KOL) if os.environ.get("TASLAK_CATAL_DIS_KOL") is not None else "catal-geo.json", b_catal_geo())
    elif b in ("kafakol_ince_sag", "kafakol_ince_sol"):
        yaz("%s-%s.json" % (b, R["ad"]), b_kafakol_ince(R, b.split("_")[-1]))
    elif b in ("kafakol_sag", "kafakol_sol"):
        yaz("%s-%s%s.json" % (b, R["ad"], ("-s2_%s" % os.environ["TA_S2_MIN"]) if os.environ.get("TA_S2_MIN") else ""), b_kafakol(R, b.split("_")[1]))
    else:
        log("bilinmeyen bolum", b)
    log("bolum", b, "bitti %.0f s" % (time.time() - tb))
log("hepsi bitti")
