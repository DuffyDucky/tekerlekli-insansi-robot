# Y0f: FreeCAD ana montajından fizik modeli için ham veri çıkarır (FreeCAD 1.1 Python'u ile çalışır).
#
# Okur:  tasarim/freecad/montaj/robot-montaj.FCStd (ÖNCE geçici klasöre KOPYALANIR; CAD klasörüne hiçbir şey yazılmaz)
# Yazar: kod/fizik/model/cad_govdeler.json  (22 montaj grubu: kütle, AM, CAD katılarından atalet tensörü, sınır kutusu,
#                                            parça listesi; her parçanın ağdaki üçgen aralığı)
#        $LALE_HAM/<grup>.stl (ham ağ, CAD mm, global; OneDrive DIŞINDA önbellek, depoya girmez: onlarca MB)
#
# Atalet: her parçanın katıları için FreeCAD `Solid.MatrixOfInertia` (birim yoğunlukta, katının kendi AM'sinde;
# kutu ve L şekliyle denetlendi: köşegen dışı terimler -∫xy dm kuralında) parçanın montajdaki kütlesiyle
# (`Kutle_g`) ölçeklenir: parça içinde yoğunluk TEKDÜZE varsayılır. Grup tensörü paralel eksen teoremiyle toplanır.
# Çalıştırma (yolda "ü" olduğu için ASCII başlatıcıyla; tasarim/freecad/README.md "Çalıştırma"):
#   kod/fizik/model_uret.py --cad bunu kendisi çağırır. Elle:
#   FC_SCRIPT=<bu dosya> LALE_FCSTD=<FCStd> LALE_CIKTI=<kod/fizik/model> freecadcmd %USERPROFILE%\.robot-cad\run_fc.py
import json
import os
import shutil
import struct
import tempfile
import time

import FreeCAD as App
import MeshPart

t0 = time.time()
FCSTD = os.environ["LALE_FCSTD"]
CIKTI = os.environ["LALE_CIKTI"]
SAPMA_MM = float(os.environ.get("LALE_AG_SAPMA_MM", "1.0"))      # ağ doğrusal sapması (mm)
HAM = os.environ["LALE_HAM"]
os.makedirs(HAM, exist_ok=True)

gecici = tempfile.mkdtemp(prefix="lale-fizik-")
kopya = os.path.join(gecici, "robot-montaj.FCStd")
shutil.copy2(FCSTD, kopya)
doc = App.openDocument(kopya)


def mat3(m):
    return [[m.A11, m.A12, m.A13], [m.A21, m.A22, m.A23], [m.A31, m.A32, m.A33]]


def dondur_tensor(R, I):
    # R I R^T
    RI = [[sum(R[i][k] * I[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return [[sum(RI[i][k] * R[j][k] for k in range(3)) for j in range(3)] for i in range(3)]


def paralel(I, m, d):
    # tensörü AM'den d kadar ötedeki noktaya taşı: I + m (|d|^2 E - d d^T)
    d2 = d[0] ** 2 + d[1] ** 2 + d[2] ** 2
    return [[I[i][j] + m * ((d2 if i == j else 0.0) - d[i] * d[j]) for j in range(3)] for i in range(3)]


gruplar = {}
feats = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
for o in feats:
    g = o.getParentGeoFeatureGroup()
    gad = g.Name if g else "_yok"
    G = gruplar.setdefault(gad, dict(etiket=g.Label if g else "", parca=[], sekiller=[]))
    kutle = float(getattr(o, "Kutle_g", 0.0) or 0.0)
    sl = o.Shape.Solids
    # o.Shape kendi Placement'ını taşır; yalnız üst grubun yerleşimi uygulanır (ana_montaj.py § 3 ile aynı)
    P = o.getGlobalPlacement().multiply(o.Placement.inverse())
    R = mat3(P.Rotation.toMatrix())
    if kutle <= 0 or not sl:
        G["parca"].append(dict(ad=o.Label, kutle_g=kutle, kati=len(sl), not_="kütlesiz ya da katısız (referans)"))
        continue
    vt = sum(s.Volume for s in sl)
    c = App.Vector(0, 0, 0)
    for s in sl:
        c = c + s.CenterOfMass * (s.Volume / vt)
    I = [[0.0] * 3 for _ in range(3)]
    for s in sl:
        ms = kutle * s.Volume / vt
        Is = [[v * kutle / vt for v in row] for row in mat3(s.MatrixOfInertia)]   # birim yoğunluk -> g·mm²
        dc = s.CenterOfMass - c
        Is = paralel(Is, ms, (dc.x, dc.y, dc.z))
        I = [[I[i][j] + Is[i][j] for j in range(3)] for i in range(3)]
    cg = P.multVec(c)
    Ig = dondur_tensor(R, I)
    bb = o.Shape.BoundBox
    bbg = [P.multVec(App.Vector(x, y, z)) for x in (bb.XMin, bb.XMax) for y in (bb.YMin, bb.YMax) for z in (bb.ZMin, bb.ZMax)]
    G["parca"].append(dict(ad=o.Label, tur=getattr(o, "Tur", ""), kod=getattr(o, "Kod", ""), kutle_g=round(kutle, 4),
                           hacim_mm3=round(vt, 3), merkez=[round(cg.x, 4), round(cg.y, 4), round(cg.z, 4)],
                           atalet_g_mm2=[[round(v, 2) for v in r] for r in Ig],
                           kutu=[[round(min(p.x for p in bbg), 2), round(min(p.y for p in bbg), 2), round(min(p.z for p in bbg), 2)],
                                 [round(max(p.x for p in bbg), 2), round(max(p.y for p in bbg), 2), round(max(p.z for p in bbg), 2)]]))
    sk = o.Shape.copy()
    sk.Placement = P.multiply(o.Placement)       # şekil + üst grup = global
    G["sekiller"].append(sk)

cikti = dict(kaynak=os.path.relpath(FCSTD, os.path.dirname(os.path.dirname(os.path.dirname(CIKTI)))).replace("\\", "/"),
             birim="mm, g, g*mm^2; CAD global: +X robotun kendi solu (K65), +Y yukari, +Z ileri; ev pozu (eklem acilari 0)",
             atalet_yontemi="FreeCAD Solid.MatrixOfInertia (AM'de, birim yogunluk) x Kutle_g / hacim; parca ici yogunluk tekduze varsayimi; grup = paralel eksen toplami",
             ag_sapma_mm=SAPMA_MM, gruplar={})
toplam_m, toplam_c = 0.0, [0.0, 0.0, 0.0]
for gad, G in sorted(gruplar.items()):
    pp = [p for p in G["parca"] if "merkez" in p]
    m = sum(p["kutle_g"] for p in pp)
    c = [sum(p["kutle_g"] * p["merkez"][i] for p in pp) / m for i in range(3)] if m else [0.0, 0.0, 0.0]
    I = [[0.0] * 3 for _ in range(3)]
    for p in pp:
        d = [p["merkez"][i] - c[i] for i in range(3)]
        Ip = paralel(p["atalet_g_mm2"], p["kutle_g"], d)
        I = [[I[i][j] + Ip[i][j] for j in range(3)] for i in range(3)]
    kutu = [[min(p["kutu"][0][i] for p in pp) for i in range(3)], [max(p["kutu"][1][i] for p in pp) for i in range(3)]] if pp else None
    # kaba görsel ağ: global CAD mm, ikili STL
    ucgen = 0
    yol = os.path.join(HAM, gad + ".stl")
    with open(yol, "wb") as f:
        f.write(b"Lale Y0f kaba ag (CAD mm, global)".ljust(80, b" "))
        f.write(struct.pack("<I", 0))
        kutleli = [p for p in G["parca"] if "merkez" in p]
        for p, sk in zip(kutleli, G["sekiller"]):
            msh = MeshPart.meshFromShape(Shape=sk, LinearDeflection=SAPMA_MM, AngularDeflection=0.5, Relative=False)
            p["ucgen"] = [ucgen, msh.CountFacets]
            for fc in msh.Facets:
                n = fc.Normal
                f.write(struct.pack("<12fH", n.x, n.y, n.z, *[v for pt in fc.Points for v in pt], 0))
                ucgen += 1
        f.seek(80)
        f.write(struct.pack("<I", ucgen))
    cikti["gruplar"][gad] = dict(etiket=G["etiket"], kutle_g=round(m, 4), am_mm=[round(v, 4) for v in c],
                                 atalet_am_g_mm2=[[round(v, 1) for v in r] for r in I], kutu_mm=kutu,
                                 parca_sayisi=len(G["parca"]), kutleli_parca=len(pp), ag_ucgen=ucgen,
                                 parcalar=G["parca"])
    toplam_m += m
    for i in range(3):
        toplam_c[i] += m * c[i]
    print("grup %-20s %4d parca %10.2f g  ucgen %7d  %.1fs" % (gad, len(G["parca"]), m, ucgen, time.time() - t0))
cikti["toplam"] = dict(kutle_g=round(toplam_m, 3), am_mm=[round(v / toplam_m, 4) for v in toplam_c], parca=len(feats))
App.closeDocument(doc.Name)
shutil.rmtree(gecici, ignore_errors=True)
with open(os.path.join(CIKTI, "cad_govdeler.json"), "w", encoding="utf-8") as f:
    json.dump(cikti, f, ensure_ascii=False, indent=1)
print("TOPLAM %.2f g AM %s parca %d  %.1fs" % (toplam_m, cikti["toplam"]["am_mm"], len(feats), time.time() - t0))
