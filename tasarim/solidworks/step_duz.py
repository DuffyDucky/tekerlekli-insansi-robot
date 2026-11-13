# Lale: FCStd montajini SolidWorks icin "duz" STEP'e cevirir: montaj/alt montaj yok, tek urun, tum kati dunya koordinatinda.
# Kullanim: python step_duz.py --kaynak <FCStd/klasor> --cikti <yol.step> [--grup Teker] [--ad "Lale duz"] [--freecad <freecad.exe>]
# Renk: parca "Renk" anahtari step_renkli.RENK tablosundan yuz basina DiffuseColor olarak verilir (saydamlik 0).
import os, sys, json, glob, subprocess, tempfile, time, re, collections, importlib.util

def _renkli():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "step_renkli.py")
    s = importlib.util.spec_from_file_location("step_renkli", p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m

def baslat(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--kaynak", required=True); ap.add_argument("--cikti", required=True)
    ap.add_argument("--dosya"); ap.add_argument("--ad"); ap.add_argument("--grup"); ap.add_argument("--freecad")
    ap.add_argument("--zaman-asimi", type=int, default=1500)
    a = ap.parse_args(argv)
    sr = _renkli()
    fc = sr.freecad_bul(a.freecad)
    tmp = tempfile.mkdtemp(prefix="step_duz_")
    rapor_yol = os.path.join(tmp, "rapor.json")
    sarmal = os.path.join(tmp, "sarmal.py")
    open(sarmal, "w", encoding="utf-8").write("import os\np = os.environ['STEP_DUZ_BETIK']\n"
        "exec(compile(open(p, encoding='utf-8').read(), p, 'exec'), {'__file__': p, '__name__': '__main__'})\n")
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", STEP_DUZ_BETIK=os.path.abspath(__file__),
               STEP_DUZ_ARG=json.dumps(dict(kaynak=os.path.abspath(a.kaynak), cikti=os.path.abspath(a.cikti), dosya=a.dosya, ad=a.ad, grup=a.grup,
                                           rapor=rapor_yol, renk=dict(sr.RENK, **{k: v for k, v in sr.RENK_TABAN.items() if k not in sr.RENK})), ensure_ascii=False))
    p = subprocess.run([fc, sarmal], env=env, cwd=tmp, timeout=a.zaman_asimi, capture_output=True)
    if not os.path.exists(rapor_yol):
        print((p.stdout + p.stderr).decode("utf-8", "replace")[-3000:]); return 1
    r = json.load(open(rapor_yol, encoding="utf-8"))
    for s in r["ozet"]: print(s)
    if r.get("hata"): print("HATA:", r["hata"]); return 1
    return 0

def isci():
    import FreeCAD as App, FreeCADGui as Gui, Part, ImportGui
    arg = json.loads(os.environ["STEP_DUZ_ARG"])
    rapor = dict(ozet=[], hata=None); ozet = rapor["ozet"].append
    try:
        kaynak = arg["kaynak"]
        if os.path.isdir(kaynak):
            fc = sorted(glob.glob(os.path.join(kaynak, "*.FCStd")))
            if arg.get("dosya"): fc = [f for f in fc if os.path.basename(f).lower() == arg["dosya"].lower()]
            kaynak = fc[0]
        App.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/STEP").SetString("Scheme", "AP214")
        doc = App.openDocument(kaynak)
        asm = next((o for o in doc.Objects if o.TypeId == "Assembly::AssemblyObject"), None)
        kokler = [o for o in asm.Group if o.TypeId in ("App::Part", "Part::Feature")] if asm else [o for o in doc.Objects if o.TypeId in ("App::Part", "Part::Feature") and not o.InList]
        if arg.get("grup"): kokler = [k for k in kokler if arg["grup"].lower() in k.Label.lower()]
        gorulen, parcalar = set(), []
        def gez(o):
            if o.Name in gorulen: return
            gorulen.add(o.Name)
            if o.TypeId == "Part::Feature": parcalar.append(o)
            for c in getattr(o, "Group", []): gez(c)
        for k in kokler: gez(k)
        renk = arg["renk"]; gri = renk["gri"]
        katilar, renkler, ren_say = [], [], collections.Counter()
        bb_kaynak = App.BoundBox()
        for o in parcalar:
            sh = o.Shape.copy()
            sh.Placement = o.getGlobalPlacement()
            rgb = renk.get(getattr(o, "Renk", "") or "gri", gri)
            for s in sh.Solids:
                katilar.append(s)
                renkler += [tuple(rgb[:3]) + (1.0,)] * len(s.Faces)
                ren_say[tuple(int(round(x * 255)) for x in rgb[:3])] += 1
            bb_kaynak.add(sh.BoundBox)
        ozet("parca %d, kati %d, yuz %d" % (len(parcalar), len(katilar), len(renkler)))
        ozet("kaynak sinir kutusu (dunya): X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f" % (bb_kaynak.XMin, bb_kaynak.XMax, bb_kaynak.YMin, bb_kaynak.YMax, bb_kaynak.ZMin, bb_kaynak.ZMax))
        ad = (arg.get("ad") or "Lale-duz").replace("'", "")
        d1 = App.newDocument("Duz")
        f = d1.addObject("Part::Feature", "Duz"); f.Label = ad
        f.Shape = Part.makeCompound(katilar)
        d1.recompute()
        vo = Gui.getDocument(d1.Name).getObject(f.Name)
        vo.Transparency = 0
        vo.DiffuseColor = renkler
        Gui.updateGui()
        cikti = arg["cikti"]
        if os.path.exists(cikti): os.remove(cikti)
        ImportGui.export([f], cikti)
        txt = open(cikti, encoding="utf-8", errors="surrogateescape", newline="").read()
        ozet("STEP: %s (%.1f MB)" % (cikti, os.path.getsize(cikti) / 1048576.0))
        ozet("PRODUCT=%d NEXT_ASSEMBLY_USAGE_OCCURRENCE=%d MANIFOLD_SOLID_BREP=%d BREP_WITH_VOIDS=%d STYLED_ITEM=%d SURFACE_STYLE_TRANSPARENT=%d ayri COLOUR_RGB=%d" % (
            len(re.findall(r"^#\d+ = PRODUCT\(", txt, re.M)), txt.count("NEXT_ASSEMBLY_USAGE_OCCURRENCE"), txt.count("MANIFOLD_SOLID_BREP("),
            txt.count("BREP_WITH_VOIDS("), txt.count("STYLED_ITEM("), txt.count("SURFACE_STYLE_TRANSPARENT"),
            len(set(re.findall(r"COLOUR_RGB\('[^']*',([^)]*)\)", txt.replace("\n", ""))))))
        App.closeDocument(d1.Name); App.closeDocument(doc.Name)
        d2 = App.newDocument("Geri"); ImportGui.insert(cikti, d2.Name)
        g2 = Gui.getDocument(d2.Name)
        y = [o for o in d2.Objects if o.TypeId == "Part::Feature" and o.Shape and not o.Shape.isNull() and o.Shape.Solids]
        bb = App.BoundBox(); ks = 0; rc = collections.Counter()
        for o in y:
            bb.add(o.Shape.BoundBox); ks += len(o.Shape.Solids)
            try:
                dc = g2.getObject(o.Name).DiffuseColor
                for c in dc: rc[tuple(int(round(x * 255)) for x in c[:3])] += 1
            except Exception as e: pass
        ozet("geri alinan: nesne %d, kati %d, sinir kutusu X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f (yukseklik %.1f)" % (len(y), ks, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, bb.ZLength))
        ozet("geri alinan yuz-rengi: %d farkli renk %s ; beklenen kati-rengi: %d farkli" % (len(rc), dict(rc.most_common(6)), len(ren_say)))
    except Exception:
        import traceback; rapor["hata"] = traceback.format_exc()
    json.dump(rapor, open(arg["rapor"], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    sys.stdout.flush(); os._exit(0)

if __name__ == "__main__":
    try:
        import FreeCAD; icinde = True
    except ImportError:
        icinde = False
    isci() if icinde else sys.exit(baslat(sys.argv[1:]))
