# K2 (2. ajan): kaset govdesi ve kapagi +x'ten AYRI AYRI kaydirilirken gobek (tambur dahil) ve kol zinciri ile kesin cakisma
# (common hacmi) ve en kucuk mesafe. K2-tarama montaj on taramasi (nokta bulutu) S1 -45'te t 15'te 0,009 vermisti. Yalniz okur.
# Cikti: K2-kaydir.json
import os, sys, math, time, json, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("k2_ortak", os.path.join(HERE, "K2-ortak.py"))
O = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(O)
import numpy as np
import FreeCAD as App
import Part
A, V, log, tasi = O.A, O.V, O.log, O.tasi
t0 = time.time()
OMU = O.ac("omuz/omuz-montaj.FCStd")
KAB = O.kabuk_yerel(O.ac("kabuk/kabuk-montaj.FCStd"))
DIR = O.ac("dirsek/dirsek-montaj.FCStd")
GOB = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Gobek"]
KOL = [(p["ad"], p["shape"]) for p in OMU if p["grup"] == "Kol"] + [(p["ad"], p["shape"]) for p in DIR if p["grup"] == "UstKol"]
KG = {p["ad"]: p["shape"] for p in KAB}
OUT = dict(tarih=time.strftime("%Y-%m-%dT%H:%M:%S"))
sat = []
for phi in (-45.0, 0.0, 90.0, 135.0):
    hed = [(a, tasi(s, O.Pp(phi))) for a, s in GOB] + [(a, tasi(s, O.Pp(phi).multiply(O.Pr(5.0)))) for a, s in KOL]
    for parca in ("S1 kaset govdesi sag", "S1 kaset kapagi sag"):
        ilk, enk = None, (1e9, None, None)
        for t in list(np.arange(0.0, 30.01, 0.5)) + [35.0, 40.0, 50.0, 60.0, 80.0, 100.0]:
            s = KG[parca].copy()
            s.translate(V(float(t), 0, 0))
            bb = App.BoundBox(s.BoundBox)
            bb.enlarge(2)
            for a, q in hed:
                if not bb.intersect(q.BoundBox):
                    continue
                d = s.distToShape(q)[0]
                if d < enk[0]:
                    enk = (round(d, 3), float(t), a)
                if d < 1e-6:
                    v = s.common(q).Volume
                    if v > 1e-3 and ilk is None:
                        ilk = (float(t), a, round(v, 3))
        sat.append(dict(phi=phi, S2=5.0, parca=parca, ilk_cakisma=ilk, en_kucuk=enk))
        log(sat[-1], "%.0fs" % (time.time() - t0))
        OUT["kaydirma"] = sat
        O.kaydet("K2-kaydir.json", OUT)
O.kaydet("K2-kaydir.json", OUT)
log("bitti %.0fs" % (time.time() - t0))
