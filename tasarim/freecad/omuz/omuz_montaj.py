# Sag omuz modulu (2 eksen) + ust kol baglantisi - FreeCAD 1.1 montaj, carpisma taramasi, tork, BOM
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
# Koordinat: X disari, Y yukari, Z ileri; orijin = omuz traversi (sigma) merkezi = one-arka ekseni uzerinde.
# Parcalar, kutle ve kinematik omuz_parcalar.py'de (carpisma.py de onu kullanir); burada kontroller ve kayit.
import os, sys, json, math, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from omuz_parcalar import *   # noqa

print("parca sayisi", len(P), "%.1fs" % (time.time() - t0))


def moved(p, pl):
    s = p["shape"].copy()
    s.transformShape(pl.toMatrix())
    return s


def overlap(a, b, abb=None, bbb=None):
    abb = abb or a.BoundBox
    bbb = bbb or b.BoundBox
    if not abb.intersect(bbb):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


TOL = 0.5   # mm3

# --- 1) ev pozunda tum ciftler (statik montaj kontrolu). Ev pozu = yazilim ev pozu: S1 0, S2 = yana alt siniri (arayuz.OMUZ;
#        15 Ekim 2026'dan beri 5). S1 kablo tamburu kola S2 ~3,8 derecenin altinda deger (tasarim geregi yumusak dayanak; S2 alt siniri
#        bu yuzden 5): mekanik sifir (S2 0) ayrica bilgi olarak kaydedilir (statik_s2_0), kontrol olcutu degildir.
EV_TH = float(A.OMUZ["yana_aralik"][0])


def _ev(p, th):
    return moved(p, pose_place(p, 0, th)) if p["grup"] == "Kol" else p["shape"]


def statik_ciftler(th):
    sh = [_ev(p, th) for p in P]
    bb = [s_.BoundBox for s_ in sh]
    out_ = []
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            v = overlap(sh[i], sh[j], bb[i], bb[j])
            if v > TOL or v < 0:
                out_.append((P[i]["ad"], P[j]["ad"], round(v, 2)))
    return out_


static = statik_ciftler(EV_TH)
static_s2_0 = statik_ciftler(0.0)
print("statik cakisma (S2 %.0f):" % EV_TH, len(static), static[:10], "; mekanik sifir S2 0 (bilgi):", static_s2_0, "%.1fs" % (time.time() - t0))

# --- 1b) yuva M6 civatalari: uc cekic somunu >= 0,5 mm gecmeli, kanal tabanina degmemeli (duzeltme plani M3)
M6_PAY_MIN = 0.5   # mm (somun payi)
M6_TABAN_PAY_MIN = 0.5   # mm (kanal tabani payi; diger modullerle ayni: eskiden yalniz > 0)
m6_pay = []
_vida = [p for p in P if p["ad"] == "Yuva baglanti civatasi M6x16"]
_somun = [p for p in P if p["ad"] == "Cekic somun M6 (kanal 10)"]
_tabanD = A.OMUZ_YUVA_YZ - (A.SG / 2 - A.KANAL_TABAN)   # kanal tabaninin yuva dis yuzunden derinligi (16,8)
for (pp, dd, ld), vv, ss in zip(SLEEVE, _vida, _somun):
    pv_, dv_ = V(*pp), V(*dd)
    uc = max((q.Point - pv_).dot(dv_) for q in vv["shape"].Vertexes)           # civata ucu, dis yuzden derinlik
    somun_alt = max((q.Point - pv_).dot(dv_) for q in ss["shape"].Vertexes)    # cekic somun alt yuzu
    m6_pay.append(dict(yuz=list(pp), uc_derinlik=round(uc, 3), somun_alt=round(somun_alt, 3), taban=round(_tabanD, 3),
                       somun_pay=round(uc - somun_alt, 3), taban_pay=round(_tabanD - uc, 3)))
m6_ok = all(m["somun_pay"] >= M6_PAY_MIN and m["taban_pay"] >= M6_TABAN_PAY_MIN for m in m6_pay) and len(m6_pay) == 4
print("M6 vida payi (uc - somun alti / kanal tabani - uc):", [(m["somun_pay"], m["taban_pay"]) for m in m6_pay], "OK" if m6_ok else "HATA",
      "%.1fs" % (time.time() - t0))

# --- 2) ev pozunda gruplar arasi en kucuk bosluk
def min_gap(ga, gb, phi=0, th=0):
    best = (1e9, None, None)
    for a in P:
        if a["grup"] != ga or a["tur"] == "Referans" and ga != "Govde":
            continue
        sa = moved(a, pose_place(a, phi, th))
        for b in P:
            if b["grup"] != gb:
                continue
            sb = moved(b, pose_place(b, phi, th))
            bb = sa.BoundBox
            bb.enlarge(15)
            if not bb.intersect(sb.BoundBox):
                continue
            d = sa.distToShape(sb)[0]
            if d < best[0]:
                best = (d, a["ad"], b["ad"])
    return best


gaps = {k: min_gap(*k.split("-"), 0, EV_TH) for k in ("Kol-Gobek", "Kol-Govde", "Gobek-Govde")}
print("ev pozu bosluklar:", gaps, "%.1fs" % (time.time() - t0))

# --- 3) hareket taramasi (PHIS, THS: omuz_parcalar)
govde = [p for p in P if p["grup"] == "Govde"]
gobek = [p for p in P if p["grup"] == "Gobek"]
kol = [p for p in P if p["grup"] == "Kol"]

# kol x gobek: sadece yana acmaya bagli
kol_gobek = {}
for th in THS:
    hits = []
    for a in kol:
        sa = moved(a, Pr(th))
        for b in gobek:
            v = overlap(sa, b["shape"], None, b["bb"])
            if v > TOL:
                hits.append((a["ad"], b["ad"], round(v, 1)))
    kol_gobek[th] = hits
print("kol x gobek bitti %.1fs" % (time.time() - t0))

# gobek x govde: sadece one-arkaya bagli
gobek_govde = {}
for phi in PHIS:
    hits = []
    for a in gobek:
        sa = moved(a, Pp(phi))
        for b in govde:
            v = overlap(sa, b["shape"], None, b["bb"])
            if v > TOL:
                hits.append((a["ad"], b["ad"], round(v, 1)))
    gobek_govde[phi] = hits
print("gobek x govde bitti %.1fs" % (time.time() - t0))

# kol x govde: iki eksene bagli
kol_govde = {}
for phi in PHIS:
    for th in THS:
        pl = Pp(phi).multiply(Pr(th))
        hits = []
        for a in kol:
            sa = moved(a, pl)
            for b in govde:
                v = overlap(sa, b["shape"], None, b["bb"])
                if v > TOL:
                    hits.append((a["ad"], b["ad"], round(v, 1)))
        kol_govde[(phi, th)] = hits
print("kol x govde bitti %.1fs" % (time.time() - t0))

# --- 4) tork (kg*cm): g*mm toplam / 10000
def torques(phi, th):
    tp, tr = 0.0, 0.0
    ax_r = Pp(phi).Rotation.multVec(V(0, 0, 1))
    pts = []
    for p in P:
        if p["grup"] in ("Gobek", "Kol") and p["kutle"] > 0:
            c = pose_place(p, phi, th).multVec(p["merkez"])
            pts.append((p["grup"], p["kutle"], c))
    c = Pp(phi).multiply(Pr(th)).multVec(V(*ALT_KOL["p"]))
    pts.append(("Kol", ALT_KOL["m"], c))
    for g, m, c in pts:
        tp += m * c.z                       # |tau_x| = g * sum(m z)
        if g == "Kol":
            r = c - V(XR, 0, 0)
            f = V(0, -m, 0)
            tr += r.cross(f).dot(ax_r)
    return abs(tp) / 10000.0, abs(tr) / 10000.0


tork = {}
for phi in PHIS:
    for th in THS:
        tork[(phi, th)] = torques(phi, th)
print("tork bitti %.1fs" % (time.time() - t0))

# ====================================================================== kaydet: FCStd (Assembly) + STEP + STL
doc = App.newDocument("OmuzMontaj")
asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
asm.Label = "Sag_Omuz"
jg = asm.newObject("Assembly::JointGroup", "Joints")
jg.Label = "Eklemler"
groups = {}
for g, lab in (("Govde", "Govde_sabit"), ("Gobek", "Omuz_gobegi_doner"), ("Kol", "Ust_kol_doner")):
    gp = asm.newObject("App::Part", g)
    gp.Label = lab
    groups[g] = gp
feat = []
for k, p in enumerate(P):
    o = groups[p["grup"]].newObject("Part::Feature", "P%03d" % k)
    o.Label = p["ad"]
    o.Shape = p["shape"]
    for prop, val in (("Tur", p["tur"]), ("Malzeme", p["malzeme"]), ("Kod", p["kod"]), ("Renk", p["renk"]),
                      ("Not", p["not_"])):
        o.addProperty("App::PropertyString", prop, "Robot")
        setattr(o, prop, val)
    o.addProperty("App::PropertyVector", "Patlat", "Robot")
    o.Patlat = V(*p["patlat"])
    o.addProperty("App::PropertyFloat", "Kutle_g", "Robot")
    o.Kutle_g = round(p["kutle"], 1)
    feat.append(o)
doc.recompute()

try:
    import JointObject
    gj = jg.newObject("App::FeaturePython", "Sabit")
    JointObject.GroundedJoint(gj, groups["Govde"])
    first = {g: next(o for o, p in zip(feat, P) if p["grup"] == g and p["tur"] == "Baski") for g in groups}

    def revolute(name, label, ga, gb, point, rot, amin, amax):
        j = jg.newObject("App::FeaturePython", name)
        JointObject.Joint(j, 1)
        j.Label = label
        j.Reference1 = [groups[ga], [first[ga].Name + ".Face1", first[ga].Name + ".Vertex1"]]
        j.Reference2 = [groups[gb], [first[gb].Name + ".Face1", first[gb].Name + ".Vertex1"]]
        j.Detach1 = True
        j.Detach2 = True
        j.Placement1 = App.Placement(V(*point), rot)
        j.Placement2 = App.Placement(V(*point), rot)
        j.EnableAngleMin = True
        j.AngleMin = amin
        j.EnableAngleMax = True
        j.AngleMax = amax
        return j
    revolute("OmuzOneArka", "Omuz_one_arka (S1)", "Govde", "Gobek", (150, 0, 0), App.Rotation(V(0, 1, 0), -90), *A.OMUZ["one_arka_aralik"])
    revolute("OmuzYanaAcma", "Omuz_yana_acma (S2)", "Gobek", "Kol", (XR, 0, Z_S2), App.Rotation(), *A.OMUZ["yana_aralik"])
    asm.solve()
    doc.recompute()
    joints_ok = True
except Exception as e:
    joints_ok = repr(e)
for g in groups.values():
    g.Placement = App.Placement()
doc.recompute()
doc.saveAs(os.path.join(HERE, "omuz-montaj.FCStd"))

Part.Compound([p["shape"] for p in P if p["tur"] != "Referans"]).exportStep(os.path.join(HERE, "omuz-montaj.step"))
os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
import Mesh, MeshPart
baski = []
for p in P:
    if p["tur"] == "Baski":
        fn = p["ad"].lower().replace(" ", "-") + ".stl"
        m = MeshPart.meshFromShape(Shape=p["shape"], LinearDeflection=0.05, AngularDeflection=0.3)
        m.write(os.path.join(HERE, "stl", fn))
        bb = p["bb"]
        dims = sorted([bb.XLength, bb.YLength, bb.ZLength], reverse=True)
        baski.append(dict(ad=p["ad"], stl="stl/" + fn, olcu=[round(d, 1) for d in dims],
                          sigar=all(d <= 230 for d in dims), kutle=round(p["kutle"], 1),
                          hacim_cm3=round(p["hacim"] / 1000, 1)))

# ====================================================================== analiz json
def pose_free(phi, th):
    return not kol_gobek[th] and not gobek_govde[phi] and not kol_govde[(phi, th)]


bom = {}
for p in P:
    if p["tur"] in ("Satin", "Baglanti") and not p["kod"].startswith("("):
        bom.setdefault((p["tur"], p["kod"]), 0)
        bom[(p["tur"], p["kod"])] += 1
out = dict(
    parca_sayisi=len(P),
    coklu_kati=[(p["ad"], p["kati"]) for p in P if p["kati"] != 1],
    gecersiz=[p["ad"] for p in P if not p["shape"].isValid()],
    statik=static, statik_poz=dict(one_arka=0.0, yana=EV_TH), statik_s2_0=static_s2_0,
    m6_vida_pay=dict(sinir_somun_mm=M6_PAY_MIN, sinir_taban_mm=M6_TABAN_PAY_MIN, ok=m6_ok, yuzler=m6_pay),
    eklem_siniri=dict(one_arka=list(A.OMUZ["one_arka_aralik"]), yana=list(A.OMUZ["yana_aralik"]), kaynak="arayuz.OMUZ"),
    bosluk={k: [round(v[0], 2), v[1], v[2]] for k, v in gaps.items()},
    phis=PHIS, ths=THS,
    kol_gobek={str(k): v for k, v in kol_gobek.items()},
    gobek_govde={str(k): v for k, v in gobek_govde.items()},
    kol_govde={"%d,%d" % k: v for k, v in kol_govde.items()},
    serbest={"%d,%d" % (a, b): pose_free(a, b) for a in PHIS for b in THS},
    tork={"%d,%d" % k: [round(v[0], 2), round(v[1], 2)] for k, v in tork.items()},
    kutle={g: round(sum(p["kutle"] for p in P if p["grup"] == g), 1) for g in ("Govde", "Gobek", "Kol")},
    alt_kol=ALT_KOL,
    bom=[[k[0], k[1], v] for k, v in sorted(bom.items())],
    baski=baski,
    joints_ok=joints_ok,
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "omuz-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("bitti %.1fs" % (time.time() - t0))
