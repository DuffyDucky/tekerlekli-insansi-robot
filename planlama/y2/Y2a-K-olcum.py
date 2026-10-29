# Y2a bagimsiz kontrol olcumleri (scratch kopyada). Yalniz okur.
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(HERE, "..", "..", "tasarim", "freecad")   # planlama/y2 -> proje koku
sys.path.insert(0, os.path.join(R, "montaj")); sys.path.insert(0, R)
import FreeCAD as App, Part
import moduller as MD
A = MD.A
V = App.Vector
OUT = {}
t0 = time.time()
def log(*a): print(*a, "%.1fs" % (time.time() - t0), flush=True)
G = {}
for ad in MD.SIRA:
    d = MD.yukle(ad)
    G[ad] = [(p, MD.global_sekil(p["shape"], ad)) for p in d["parcalar"] if not p["haric"]]
    log("yuklendi", ad, len(G[ad]))
OUT["parca"] = {ad: len(v) for ad, v in G.items()}; OUT["parca_toplam"] = sum(OUT["parca"].values())
OUT["kutle_g"] = round(sum(p["kutle"] for v in G.values() for p, _ in v), 2)
# 1) boy: kafa en ust nokta (optimal bb), tum robot ymin/ymax
def obb(s):
    try: return s.optimalBoundingBox()
    except Exception: return s.BoundBox
ymax = max(obb(g).YMax for v in G.values() for _, g in v if g.Solids)
ymin = min(obb(g).YMin for v in G.values() for _, g in v if g.Solids)
top = sorted(((obb(g).YMax, ad, p["ad"]) for ad, v in G.items() for p, g in v if g.Solids), reverse=True)[:5]
OUT["boy"] = dict(ymax=round(ymax, 3), ymin=round(ymin, 3), en_ust=[(round(a, 3), b, c) for a, b, c in top])
# genislik / derinlik
OUT["zarf"] = dict(x=(round(min(obb(g).XMin for v in G.values() for _, g in v if g.Solids), 1), round(max(obb(g).XMax for v in G.values() for _, g in v if g.Solids), 1)),
                   z=(round(min(obb(g).ZMin for v in G.values() for _, g in v if g.Solids), 1), round(max(obb(g).ZMax for v in G.values() for _, g in v if g.Solids), 1)))
log("boy", OUT["boy"])
# 2) direk, tekerler, Nextion artigi
for p, g in G["iskelet"]:
    if p["ad"].startswith("Govde diregi"):
        b = g.BoundBox; OUT["direk"] = dict(y=(round(b.YMin, 2), round(b.YMax, 2)), L=round(b.YLength, 2), x=(round(b.XMin,1), round(b.XMax,1)), z=(round(b.ZMin,1), round(b.ZMax,1)))
tek = [(p["ad"], g) for p, g in G["taban"] if "teker" in p["ad"].lower() and p["tur"] != "Baglanti"]
OUT["tekerler"] = [(a, [round(c, 1) for c in (g.BoundBox.Center.x, g.BoundBox.Center.y, g.BoundBox.Center.z)], round(g.BoundBox.XLength, 1), round(g.BoundBox.YMin, 2)) for a, g in tek][:12]
OUT["nextion_artigi"] = [p["ad"] for v in G.values() for p, _ in v if "nextion" in p["ad"].lower() or ("ekran" in p["ad"].lower())]
# 3) aku: yerinde ve +75 z
aku = [(p, g) for p, g in G["taban"] if p["ad"].lower().startswith("aku") or "akü" in p["ad"].lower() or p["ad"].lower() == "aku"]
OUT["aku_adaylar"] = [(p["ad"], [round(c, 1) for c in (g.BoundBox.XMin, g.BoundBox.XMax, g.BoundBox.YMin, g.BoundBox.YMax, g.BoundBox.ZMin, g.BoundBox.ZMax)]) for p, g in aku]
sabit = [(ad, p, g) for ad in ("iskelet", "taban", "kabuk") for p, g in G[ad] if g.Solids]
for dz in (0.0, 75.0):
    rows = []
    for pa, ga in aku:
        if pa["tur"] not in ("Satin",) and "aku" not in pa["ad"].lower(): continue
        if pa["ad"].lower() != "aku" and not pa["ad"].lower().startswith("aku ("):
            pass
        s = ga.copy(); s.translate(V(0, 0, dz)); bb = s.BoundBox
        for ad, p, g in sabit:
            if p is pa or p["ad"].lower().startswith("aku"): continue
            if not bb.intersect(g.BoundBox): continue
            try: v = s.common(g).Volume
            except Exception: v = -1
            if v > 1e-3: rows.append((pa["ad"], ad, p["ad"], round(v, 1)))
    OUT["aku_dz_%d" % dz] = rows
    log("aku dz", dz, len(rows))
# 4) tambur ip deligi eksenel genisligi (omuz_sag yerel = omuz modulu shape)
import importlib
for p in MD.yukle("omuz_sag")["parcalar"]:
    if p["ad"] == "S1 kablo tamburu":
        dr = p["shape"]
KK = A.KOL_KABLO["s1"]
OUT["tambur_bb"] = [round(c, 2) for c in (dr.BoundBox.XMin, dr.BoundBox.XMax)]
# ip psi'lerinde radyal dilim: x boyunca 0,02 adim, kanal yaricapinda (r 37...37,5 civari) kutu ile kesisim -> bos x araliklari
import math
res = {}
TBd = KK["tambur"]
for psi in TBd["ip_psi"]:
    for sg in (1, -1):
        for r in (37.5, 38.0, 38.5):
            a = math.radians(sg * psi)
            bos = []
            x = 152.4
            while x <= 159.4:
                # psi=0: radyal +Y; X ekseni etrafinda donus
                y, z = r * math.cos(a), r * math.sin(a)
                ins = dr.isInside(V(x, y, z), 1e-4, True)
                bos.append((round(x, 3), ins))
                x += 0.01
            # bos araliklar (malzeme yok) tambur x 152,5...159,3 icinde
            ar = []; cur = None
            for xx, ins in bos:
                if 152.5 < xx < 159.3 and not ins:
                    cur = [xx, xx] if cur is None else [cur[0], xx]
                elif cur is not None:
                    ar.append(cur); cur = None
            if cur: ar.append(cur)
            res["psi%+d_r%.1f" % (sg * psi, r)] = [(a_[0], a_[1], round(a_[1] - a_[0] + 0.01, 2)) for a_ in ar]
OUT["tambur_delik"] = res
OUT["kk_s1_keys"] = list(KK.keys())
# 5) kafa x sag kol capraz kontrol (yasak kutu aktif=False dayanagi): kol yukarida/ice, kafa pan/tilt
import itertools
MODD = {ad: MD.yukle(ad) for ad in ("omuz_sag", "dirsek_sag", "kafa")}
def yerlesik(ad, poz, gruplar):
    d = MODD[ad]; out = []; cache = {}
    for p in d["parcalar"]:
        if p["haric"] or p["tur"] == "Referans" or p["grup"] == "Referans" or p["grup"] not in gruplar: continue
        if p["grup"] not in cache:
            pl = d["beklenen"](poz, p["grup"]) if d["beklenen"] else None
            cache[p["grup"]] = None if (pl is None or pl.isIdentity()) else MD.global_poz(ad, pl)
        s = MD.global_sekil(p["shape"], ad)
        if cache[p["grup"]] is not None:
            s = s.copy(); s.transformShape(cache[p["grup"]].toMatrix(), True)
        out.append((p["ad"], s))
    return out
EV = dict(one_arka=0.0, yana=5.0, dirsek=0.0, bilek=0.0, pan=0.0, tilt=0.0)
kk = []
en = (1e9, None)
for s1, s2, dr in itertools.product((60.0, 90.0, 120.0, 135.0), (5.0, 30.0, 60.0, 90.0, 117.0), (0.0, 52.5, 80.0, 105.0)):
    if s1 < 120 and s2 == 117.0: s2 = 120.0
    poz = dict(EV, one_arka=s1, yana=s2, dirsek=dr)
    kol = yerlesik("omuz_sag", poz, ("Gobek", "Kol")) + yerlesik("dirsek_sag", poz, ("UstKol", "OnKol", "El"))
    for pn, tl in itertools.product((0.0, 30.0, 45.0, 90.0), (-15.0, 0.0, 15.0)):
        kf = yerlesik("kafa", dict(poz, pan=pn, tilt=tl), ("Boyun", "Bas"))
        for na, sa in kol:
            ba = App.BoundBox(sa.BoundBox); ba.enlarge(10)
            for nb, sb in kf:
                if not ba.intersect(sb.BoundBox): continue
                d_ = sa.distToShape(sb)[0]
                if d_ < 1e-6:
                    v = sa.common(sb).Volume
                    kk.append(((s1, s2, dr, pn, tl), na, nb, round(v, 2)))
                if d_ < en[0]: en = (d_, ((s1, s2, dr, pn, tl), na, nb))
OUT["kafa_kol"] = dict(cakisma=kk[:30], cakisma_n=len(kk), en_kucuk=(round(en[0], 2), en[1]) if en[1] else None)
log("kafa kol", len(kk), OUT["kafa_kol"]["en_kucuk"])
json.dump(OUT, open(os.path.join(HERE, "Y2a-K-olcum.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("bitti")
