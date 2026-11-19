# Düzeltme turu 1: B-rep yol ölçümü (FreeCAD, salt okunur; kaynak FCStd kaydedilmez; çıktı depo dışı). Tek vaka, tek süreç.
# Ortam: ROBOT, LISTE (brep_liste.json), VAKA, OUT. Modüller tek tek açılır, yalnız listedeki nesnelerin şekli kopyalanır, belge kapanır.
# Ölçüt: ortak hacim > 1 mm³ (kontrolle aynı). Kalk bacağı 1 mm, çık bacağı 2 mm adım. Dinlenmede ortak hacmi olan çift raporlanır.
import os, sys, json, time, traceback
ROBOT = os.environ["ROBOT"]
sys.path.insert(0, os.path.join(ROBOT, "planlama", "adim4"))
OUT = os.environ["OUT"]
log = open(OUT + ".log", "w", encoding="utf-8")


def yaz(*a):
    log.write(" ".join(str(x) for x in a) + "\n"); log.flush()


try:
    import FreeCAD as App
    import m6_yukle as M
    L = json.load(open(os.environ["LISTE"], encoding="utf-8"))[os.environ["VAKA"]]
    V = App.Vector
    istek = {}
    for r in [L["bant"]] + L["tasinan"] + L["engel"]:
        istek.setdefault(r["modul"], {})[r["nesne"]] = r
    S = {}
    t0 = time.time()
    for mod, ns in istek.items():
        d = App.openDocument(os.path.join(M.FC, M.DOSYA[mod]))
        for n, r in ns.items():
            o = d.getObject(n)
            s = o.Shape.copy()
            s.Placement = o.getGlobalPlacement()
            S[r["id"]] = (r, M._global(s, mod))
        App.closeDocument(d.Name)
        yaz("modul", mod, len(ns), "nesne, %.1f s" % (time.time() - t0))
    b = S[L["bant"]["id"]][1]
    bb = b.BoundBox
    yaz("bant", L["bant"]["ad"], "kutu", [round(x, 1) for x in (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax)], "glb", L["kutu_glb"])
    tas = [S[r["id"]][1] for r in L["tasinan"]]
    H = b.fuse(tas) if tas else b
    eng = [(rid, S[rid][0], S[rid][1]) for rid in [r["id"] for r in L["engel"]]]

    def ortak(ofs):
        h = H.copy(); h.translate(ofs)
        hb = h.BoundBox
        out = {}
        for rid, r, e in eng:
            if not hb.intersect(e.BoundBox):
                continue
            try:
                v = h.common(e).Volume
            except Exception as x:
                v = -1
            if v > 1.0 or v < 0:
                out[rid] = (r["ad"], round(v, 1))
        return out

    dinlenme = ortak(V(0, 0, 0))
    yaz("dinlenme", dinlenme)
    sonuc = dict(vaka=os.environ["VAKA"], bant=L["bant"]["ad"], dinlenme=dinlenme, yollar=[])
    for kalk, yon, Lmm in L["yollar"]:
        ar = {}
        kalk = V(*kalk); yon = V(*yon)
        n1 = int(round(kalk.Length))
        u1 = V(kalk);
        if n1:
            u1.normalize()
        for i in range(1, n1 + 1):
            for rid, (ad, v) in ortak(u1 * i).items():
                if rid in dinlenme:
                    continue
                a = ar.setdefault("kalk " + ad, [i, i, 0.0]); a[1] = i; a[2] = max(a[2], v)
        ayr = None
        for j in range(2, int(Lmm) + 1, 2):
            ofs = kalk + yon * j
            h = H.copy(); h.translate(ofs)
            if not any(h.BoundBox.intersect(e.BoundBox) for _, _, e in eng):
                ayr = j
                break
            for rid, (ad, v) in ortak(ofs).items():
                if rid in dinlenme:
                    continue
                a = ar.setdefault("cik " + ad, [j, j, 0.0]); a[1] = j; a[2] = max(a[2], v)
        r = dict(kalk=[kalk.x, kalk.y, kalk.z], yon=[yon.x, yon.y, yon.z], ayrildi_mm=ayr, engel=ar)
        sonuc["yollar"].append(r)
        yaz("YOL", r, "%.0f s" % (time.time() - t0))
        json.dump(sonuc, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    yaz("bitti %.0f s" % (time.time() - t0))
except Exception:
    yaz("HATA", traceback.format_exc())
