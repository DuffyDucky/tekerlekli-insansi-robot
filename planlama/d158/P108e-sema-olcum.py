# P10.8e şema ölçümü (FreeCAD 1.1; FC_SCRIPT=<bu dosya> freecadcmd run_fc.py). Modele dokunmaz; yalnız P108e-olcum/sema-<etiket>.json
# yazar. Etiket: ortam P108E_ETIKET ("once" / "sonra"). Girdi P108e-olcum/sema-girdi-<etiket>.json (P108e-sema-girdi.py).
# Yöntem P108d-olcum.py "sema" bölümüyle aynı (eksen çizgisi Part.makePolygon × gerçek parça distToShape; "uç" = en yakın nokta şemanın
# bir ucuna ≤ 10 mm), tek fark: bütün modüller (taban dahil) üretilmiş montajdan, montaj/robot-montaj.FCStd (Tur != Referans; ev pozu,
# global). P10.8d'de taban kaynaktan kurulmuştu; P10.8d tam taramasından sonra montaj 1.251 gerçek parça, taban kaynağıyla aynı.
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
FC = os.path.join(ROBOT, "tasarim", "freecad")
import FreeCAD as App
import Part
t0 = time.time()
V = App.Vector
ETIKET = os.environ.get("P108E_ETIKET", "olcum")
CIKTI = os.path.join(HERE, "P108e-olcum")


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


def ascii_(s):
    return s.encode("ascii", "replace").decode("ascii")


def yakin(bb, q, pay):
    return not (bb.XMax + pay < q.XMin or q.XMax + pay < bb.XMin or bb.YMax + pay < q.YMin or q.YMax + pay < bb.YMin
                or bb.ZMax + pay < q.ZMin or q.ZMax + pay < bb.ZMin)


doc = App.openDocument(os.path.join(FC, "montaj", "robot-montaj.FCStd"))
GERCEK = []
for o in doc.Objects:
    if o.TypeId != "Part::Feature" or not hasattr(o, "Tur") or o.Tur == "Referans":
        continue
    s = o.Shape.copy()
    s.Placement = o.getGlobalPlacement()
    s = s.copy()
    GERCEK.append(dict(ad=o.Label, modul=getattr(o, "Modul", "?"), s=s, bb=s.BoundBox))
log("gercek parca", len(GERCEK))

sg = json.load(open(os.path.join(CIKTI, "sema-girdi-%s.json" % ETIKET), encoding="utf-8"))["semalar"]
sema = []
for s in sg:
    pts = [V(*p) for p in s["noktalar"]]
    w = Part.makePolygon(pts)
    r = s["r_cizim"]
    bbw = w.BoundBox
    kayit = []
    for q in GERCEK:
        if not yakin(bbw, q["bb"], r + 10.0):
            continue
        dd = w.distToShape(q["s"])
        d = dd[0]
        if d >= r + 5.0:
            continue
        pw = dd[1][0][0]
        ilk = min((pw - pts[0]).Length, (pw - pts[-1]).Length)
        kayit.append(dict(d=round(d, 3), parca=ascii_(q["ad"]), modul=q["modul"], yer="uc" if ilk <= 10.0 else "ara",
                          nokta=[round(pw.x, 1), round(pw.y, 1), round(pw.z, 1)], uca_mm=round(ilk, 1)))
    kayit.sort(key=lambda k: k["d"])
    sema.append(dict(kaynak=s["kaynak"], ad=s["ad"], r_cizim=r, nokta=len(pts), noktalar=s["noktalar"],
                     en_dar=kayit[0] if kayit else None, en_dar_ara=next((k for k in kayit if k["yer"] == "ara"), None),
                     eksen_icinde=[k for k in kayit if k["d"] < 1e-3], cizim_icinde=[k for k in kayit if k["d"] < r],
                     cizim_icinde_ara=[k for k in kayit if k["d"] < r and k["yer"] == "ara"], yakin=kayit[:10]))
    log("sema %s/%s: eksen icinde %d, cizim icinde %d (ara %d), en dar %s, en dar ara %s" % (
        s["kaynak"], s["ad"], len(sema[-1]["eksen_icinde"]), len(sema[-1]["cizim_icinde"]), len(sema[-1]["cizim_icinde_ara"]),
        (kayit[0]["d"], kayit[0]["parca"][:40]) if kayit else None,
        (sema[-1]["en_dar_ara"]["d"], sema[-1]["en_dar_ara"]["parca"][:40]) if sema[-1]["en_dar_ara"] else None))
out = dict(etiket=ETIKET, gercek_parca=len(GERCEK), sema=sema, sure_s=round(time.time() - t0, 1))
json.dump(out, open(os.path.join(CIKTI, "sema-%s.json" % ETIKET), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("BITTI", os.path.join(CIKTI, "sema-%s.json" % ETIKET))
