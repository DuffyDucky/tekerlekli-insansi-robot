# M6 analizi: modul FCStd dosyalarini YALNIZ OKUR, parcalari global koordinata (ev pozu) tasir. CAD'e yazmaz.
# Yerlesim arayuz.MODULLER'den (montaj/moduller.py ile ayni kural: sol = X aynasi, sonra tasima).
import os, sys
import FreeCAD as App

FC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tasarim", "freecad")
if FC not in sys.path:
    sys.path.insert(0, FC)
import arayuz as A

V = App.Vector
DOSYA = {"iskelet": "iskelet/iskelet-montaj.FCStd", "omuz_sag": "omuz/omuz-montaj.FCStd", "omuz_sol": "omuz/omuz-montaj.FCStd",
         "kabuk": "kabuk/kabuk-montaj.FCStd", "dirsek_sag": "dirsek/dirsek-montaj.FCStd", "dirsek_sol": "dirsek/dirsek-montaj.FCStd",
         "kafa": "kafa/kafa-montaj.FCStd", "taban": "taban/taban-montaj.FCStd"}
HARIC = {"omuz_sag": ("Omuz traversi", "Govde kabugu yan yuzu (referans)"),
         "omuz_sol": ("Omuz traversi", "Govde kabugu yan yuzu (referans)")}


def _global(shape, ad):
    (tx, ty, tz), ayna = A.modul_konum(ad)
    s = shape.mirror(V(0, 0, 0), V(1, 0, 0)) if ayna else shape.copy()
    T = App.Matrix()
    T.move(V(tx, ty, tz))
    s.transformShape(T, True)
    return s


def yukle(moduller=None):
    moduller = moduller or list(DOSYA)
    P, acik = [], {}
    for ad in moduller:
        yol = os.path.join(FC, DOSYA[ad])
        if yol not in acik:
            acik[yol] = App.openDocument(yol)
        d = acik[yol]
        for o in d.Objects:
            if o.TypeId != "Part::Feature" or not hasattr(o, "Tur"):
                continue
            if any(o.Label.startswith(h) for h in HARIC.get(ad, ())):
                continue
            s = o.Shape.copy()
            s.Placement = o.getGlobalPlacement()
            g = [x.Label for x in o.InList if x.TypeId == "App::Part"]
            P.append(dict(modul=ad, grup=g[0] if g else "", ad=o.Label, kod=o.Kod, tur=o.Tur, malzeme=o.Malzeme,
                          shape=_global(s, ad)))
    for d in acik.values():
        App.closeDocument(d.Name)
    return P
