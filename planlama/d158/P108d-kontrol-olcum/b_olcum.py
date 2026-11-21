# P10.8d B: bagimsiz olcum (FreeCAD 1.1, run_fc.py ile). Modele dokunmaz, yalniz B_CIKTI'ya JSON yazar.
# Taban parcalari: B_TABAN (taban-montaj.FCStd, uretilmis dosya). Obur moduller: robot-montaj.FCStd (Modul != taban).
# Yontem A'nin betiginden farkli: izin listesi yok (her temas listelenir), oturma yuz kesisimi (Face.common) ile.
import os, sys, json, time, re
import FreeCAD as App
import Part
V = App.Vector
t0 = time.time()
ROBOT = os.environ["B_ROBOT"]
FC = os.path.join(ROBOT, "tasarim", "freecad")
TABAN = os.environ["B_TABAN"]
CIKTI = os.environ["B_CIKTI"]
SEMA = os.environ.get("B_SEMA")
ESKI12 = os.environ.get("B_ESKI12") == "1"


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


def asc(s):
    return s.encode("ascii", "replace").decode("ascii")


def toplar(doc, modul_filtre=None):
    out = []
    for o in doc.Objects:
        if o.TypeId != "Part::Feature" or o.Shape.isNull() or o.Shape.Volume <= 0:
            continue
        mod = getattr(o, "Modul", "taban")
        if modul_filtre and not modul_filtre(mod):
            continue
        s = o.Shape.copy()
        s.Placement = o.getGlobalPlacement()
        s = s.copy()
        tur = getattr(o, "Tur", None)
        if tur is None:
            tur = "Referans" if o.Label.startswith("Kablo yolu") else "?"
        out.append(dict(ad=o.Label, modul=mod, tur=tur, s=s, bb=s.BoundBox))
    return out


dt = App.openDocument(TABAN)
TB = toplar(dt)
log("taban nesne", len(TB), "referans", sum(1 for q in TB if q["tur"] == "Referans"))
dr = App.openDocument(os.path.join(FC, "montaj", "robot-montaj.FCStd"))
DIS = [q for q in toplar(dr, lambda m: m != "taban") if q["tur"] != "Referans"]
log("dis parca", len(DIS))
GERCEK = [q for q in TB if q["tur"] != "Referans"] + DIS
out = dict(taban=TABAN, taban_nesne=len(TB), taban_referans=sum(1 for q in TB if q["tur"] == "Referans"),
           turler=sorted(set(q["tur"] for q in TB)), dis_parca=len(DIS))


def yakin(a, b, p):
    return not (a.XMax + p < b.XMin or b.XMax + p < a.XMin or a.YMax + p < b.YMin or b.YMax + p < a.YMin or a.ZMax + p < b.ZMin or b.ZMax + p < a.ZMin)


def komsu(sh, esik=3.0, haric=()):
    r = []
    bb = sh.BoundBox
    for q in GERCEK:
        if q["ad"] in haric or not yakin(bb, q["bb"], esik):
            continue
        d = sh.distToShape(q["s"])[0]
        if d < esik:
            v = 0.0
            if d < 1e-3:
                try:
                    v = sh.common(q["s"]).Volume
                except Exception:
                    v = -1.0
            r.append([round(d, 3), asc(q["ad"]), q["modul"], round(v, 3)])
    r.sort()
    return r


def tup(pts, r=2.5):
    pts = [V(*p) for p in pts]
    sh = [Part.makeSphere(r, p) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        if (b - a).Length > 1e-6:
            sh.append(Part.makeCylinder(r, (b - a).Length, a, (b - a).normalize()))
    return sh[0].fuse(sh[1:]).removeSplitter()


# ---- 1) kablo yollari: tam tup (dosyadaki) x her gercek parca (izin listesi yok)
yol = {}
for q in TB:
    m = re.match(r"Kablo yolu (\d+):", q["ad"])
    if not m:
        continue
    n = int(m.group(1))
    k = komsu(q["s"], 3.0)
    yol[n] = dict(hacim=round(q["s"].Volume, 1), bb=[round(x, 2) for x in (q["bb"].XMin, q["bb"].XMax, q["bb"].YMin, q["bb"].YMax, q["bb"].ZMin, q["bb"].ZMax)],
                  temas=[x for x in k if x[0] < 1e-3], yakin_3mm=k[:40])
    log("yol", n, "temas", len(yol[n]["temas"]), [x[:2] for x in yol[n]["temas"][:6]])
out["yol"] = yol

# ---- 1b) yol 12 rehber bolumu (noktalar 0..2) ve yol 11 kat / plaka gecisi
sys.path.insert(0, os.path.join(FC, "taban")); sys.path.insert(0, FC)
import arayuz as A
ESP = None
for q in TB:
    if q["ad"].startswith("ESP32") and "tasiyici" in q["ad"].lower():
        ESP = q
kat = [q for q in TB if q["ad"].startswith("Elektronik kati")]
plaka = [q for q in TB if q["ad"] == "Alt plaka"]
out["kat_ad"] = [q["ad"] for q in kat]
r12 = os.environ.get("B_Y12")
if r12:
    p12 = json.loads(r12)
    t12 = tup(p12)
    out["yol12_rehber"] = dict(noktalar=p12, komsu=komsu(t12, 6.0))
    out["yol12_rehber"]["temas"] = [x for x in out["yol12_rehber"]["komsu"] if x[0] < 1e-3]
    log("yol12 rehber", out["yol12_rehber"]["komsu"][:6])
for n in (11, 12):
    for q in TB:
        if q["ad"].startswith("Kablo yolu %d:" % n):
            out.setdefault("gecis", {})[str(n)] = {p["ad"]: round(q["s"].distToShape(p["s"])[0], 3) for p in kat + plaka}
if r12:
    out["gecis"]["12 rehber"] = {p["ad"]: round(t12.distToShape(p["s"])[0], 3) for p in kat + plaka}

# ---- 2) oturma (yuz kesisimi): panel ustu burc tabanlari, panel alti vida basi ust yuzleri
pan = [q for q in TB if q["ad"] == "Guc paneli (arka kat)"][0]
pbb = pan["bb"]


def yuzler(sh, y, yon):
    return [f for f in sh.Faces if abs(f.BoundBox.YMax - y) < 1e-4 and abs(f.BoundBox.YMin - y) < 1e-4
            and f.Surface.__class__.__name__ == "Plane" and f.normalAt(*f.Surface.parameter(f.CenterOfMass)[:2]).y * yon > 0.99]


pan_ust = yuzler(pan["s"], pbb.YMax, 1)
pan_alt = yuzler(pan["s"], pbb.YMin, -1)
oturma = []
for q in TB:
    if not re.search(r"\((On sarj karti|Acil stop dugum karti|Dagitim karti C)", q["ad"]):
        continue
    if q["ad"].startswith("Burc") and abs(q["bb"].YMin - pbb.YMax) < 0.01:
        fs = yuzler(q["s"], q["bb"].YMin, -1)
        tam = sum(f.Area for f in fs)
        des = sum(f.common(g).Area for f in fs for g in pan_ust)
    elif q["ad"].startswith("Vida") and q["ad"].endswith("alt)") and abs(q["bb"].YMax - pbb.YMin) < 0.01:
        fs = yuzler(q["s"], q["bb"].YMax, 1)
        tam = sum(f.Area for f in fs)
        des = sum(f.common(g).Area for f in fs for g in pan_alt)
    else:
        continue
    oturma.append(dict(parca=asc(q["ad"]), xz=[round(q["bb"].Center.x, 2), round(q["bb"].Center.z, 2)], tam=round(tam, 3), panelde=round(des, 3),
                       oran=round(des / tam, 3) if tam else None))
out["oturma"] = oturma
log("oturma", [(o["parca"][-30:], o["oran"]) for o in oturma])

# ---- 3) panel alti vida basi / civata x aku, kayis
aku = [q for q in TB if q["ad"].startswith(("Aku LiFePO4", "Aku kayisi"))]
alt = []
for q in TB:
    if q["tur"] != "Baglanti" or q["bb"].YMax > pbb.YMin + 0.5 or q["bb"].YMax < pbb.YMin - 0.5:
        continue
    if not (pbb.XMin - 1 < q["bb"].Center.x < pbb.XMax + 1 and pbb.ZMin - 1 < q["bb"].Center.z < pbb.ZMax + 1):
        continue
    d = min((q["s"].distToShape(a["s"])[0], asc(a["ad"])) for a in aku)
    alt.append(dict(parca=asc(q["ad"]), d=[round(d[0], 3), d[1]]))
alt.sort(key=lambda r: r["d"][0])
out["alt_bas"] = alt[:20]
log("alt bas", [(a["parca"][-40:], a["d"]) for a in alt[:5]])

# ---- 4) yeni kartlar: zarf, komsular, yollar, DAGITIM_C noktasi, M5 kat civatalari
yeni = {}
tuple_ = [(q["ad"], q["s"]) for q in TB if q["ad"].startswith("Kablo yolu")]
m5 = [q for q in TB if q["ad"].startswith("Civata M5x12 (kat")]
for q in TB:
    if not q["ad"].startswith(("Acil stop dugum karti", "Dagitim karti C")):
        continue
    b = q["bb"]
    grup = [g for g in TB if g["ad"] == q["ad"] or g["ad"].endswith("(%s 0)" % q["ad"]) or q["ad"] in g["ad"]]
    kom = komsu(q["s"], 10.0, haric=[g["ad"] for g in grup])
    yollar = sorted([(round(g["s"].distToShape(t)[0], 3), asc(ad)[:14]) for g in grup for ad, t in tuple_ if yakin(g["bb"], t.BoundBox, 15)])
    grup_kom = []
    for g in grup:
        if g["ad"] == q["ad"]:
            continue
        for x in komsu(g["s"], 3.0, haric=[h["ad"] for h in grup] + ["Guc paneli (arka kat)"]):
            grup_kom.append([asc(g["ad"])[-28:]] + x)
    grup_kom.sort(key=lambda x: x[1])
    ust = [(round(m["s"].distToShape(g["s"])[0], 2), asc(m["ad"])) for m in m5 for g in grup]
    xz = [(asc(m["ad"]), not (b.XMax < m["bb"].XMin or m["bb"].XMax < b.XMin or b.ZMax < m["bb"].ZMin or m["bb"].ZMax < b.ZMin)) for m in m5]
    r = dict(bb=[round(x, 2) for x in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)], hacim=round(q["s"].Volume, 1), grup_sayisi=len(grup),
             komsu_10mm=kom[:10], grup_komsu_3mm=grup_kom[:10], yol_en_yakin=yollar[:6], m5_en_yakin=min(ust), m5_xz_ortusme=[x for x in xz if x[1]])
    if q["ad"].startswith("Dagitim"):
        r["DAGITIM_C_nokta_mm"] = round(Part.Vertex(V(100, 192, -60)).distToShape(q["s"])[0], 3)
    yeni[asc(q["ad"])] = r
    log("yeni", q["ad"][:20], r["bb"], kom[:3], yollar[:3])
out["yeni"] = yeni

# ---- 5) semalar (eksen cizgisi) x gercek parcalar
if SEMA:
    sg = json.load(open(SEMA, encoding="utf-8"))["semalar"]
    res = []
    for s in sg:
        pts = [V(*p) for p in s["noktalar"]]
        w = Part.makePolygon(pts)
        r = s["r_cizim"]
        kay = []
        for q in GERCEK:
            if not yakin(w.BoundBox, q["bb"], r + 2):
                continue
            dd = w.distToShape(q["s"])
            if dd[0] < r:
                pw = dd[1][0][0]
                uc = min((pw - pts[0]).Length, (pw - pts[-1]).Length)
                ic = q["s"].isInside(pw, 1e-3, True) if dd[0] < 1e-3 else False
                kay.append([round(dd[0], 3), asc(q["ad"]), q["modul"], round(uc, 1), [round(pw.x, 1), round(pw.y, 1), round(pw.z, 1)]])
        kay.sort()
        res.append(dict(ad=s["ad"], kaynak=s["kaynak"], r=r, eksen_ici=[k for k in kay if k[0] < 1e-3], cizim_ici=kay[:12]))
        log("sema", s["ad"], "eksen", [(k[1][:30], k[3]) for k in kay if k[0] < 1e-3][:4])
    out["sema"] = res

out["sure_s"] = round(time.time() - t0, 1)
json.dump(out, open(CIKTI, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("BITTI", CIKTI)
