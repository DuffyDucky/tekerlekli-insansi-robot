# Düzeltme turu 1: B-rep ölçümü için engel listesi (FreeCAD'siz). Bandın alt adımında yerinde olan ve yol koridoruna giren parçalar
# (robot.glb kutusundan, 2 mm pay) → (modül, nesne adı, etiket) listesi. Eşleme: rehber_gorunum.cad_parcalar sırası = veri sırası.
import os, sys, json
import numpy as np
ROBOT, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_sira as RS, rehber_gorunum as RGo

VERI = os.path.join(ROBOT, "rehber", "veri")
V = json.load(open(os.path.join(VERI, "rehber-veri.json"), encoding="utf-8"))
D = RS.Denetim(V, os.path.join(VERI, "robot.glb"))
C = RGo.cad_parcalar()
assert len(C) == len(V["parcalar"])
CID = {p["id"]: c for p, c in zip(V["parcalar"], C)}
P, K, A = D.P, D.ID, V["adimlar"]

# (ad, adım, grup, band id, yollar: [(kalk vektörü mm, çık birim yönü, çık mm)])
IS = [("etek_on_sag", "F1", "Ön sağ bant", "p0223", [((0, 0, 0), (0, 0, 1), 200), ((0, 0, 10), (1, 0, 0), 240)]),
      ("etek_on_sol", "F1", "Ön sol bant", "p0224", [((0, 0, 0), (0, 0, 1), 200), ((0, 0, 10), (-1, 0, 0), 240)]),
      ("omuz_sag", "F4", "Omuz bandı sağ", "p0215", [((0, 16, 0), (1, 0, 0), 180), ((0, 24, 0), (1, 0, 0), 180)]),
      ("omuz_sol", "F4", "Omuz bandı sol, ön dikiş", "p0216", [((0, 16, 0), (-1, 0, 0), 170), ((0, 24, 0), (-1, 0, 0), 170)]),
      ("gogus_sol", "F3", "Göğüs bandı sol + y 1095 braketi", "p0214", [((0, 16, 0), (-1, 0, 0), 170)])]
out = {}
for ad, kod, g, pid, yollar in IS:
    s = next(i for i, a in enumerate(A) if a["kod"] == kod)
    for gad, tz, ids, izin in D.durumlar(s):
        if gad == g:
            break
    h = K[pid]
    grup = set(int(x) for x in ids)
    lo, hi = P[h]["bmin"], P[h]["bmax"]
    clo, chi = lo.copy(), hi.copy()
    for kalk, yon, L in yollar:
        k = np.asarray(kalk, float); u = np.asarray(yon, float)
        for q in (k, k + u * L):
            clo = np.minimum(clo, lo + q); chi = np.maximum(chi, hi + q)
    E = [int(e) for e in np.nonzero(izin)[0] if e != h and e not in grup and not D.ref[e]
         and np.all(P[e]["bmax"] >= clo - 2) and np.all(P[e]["bmin"] <= chi + 2)]
    # bandın kendi grubundaki ısıl gömmeler bantla birlikte taşınır (kontrolle aynı)
    tasinan = [int(x) for x in ids if int(x) != h and "Isıl gömme" in P[int(x)]["ad"]]
    def ref(i):
        c = CID[P[i]["id"]]
        return dict(id=P[i]["id"], modul=c["modul"], nesne=c["nesne"], etiket=c["etiket"], ad=P[i]["ad"])
    out[ad] = dict(bant=ref(h), tasinan=[ref(i) for i in tasinan], engel=[ref(i) for i in E], yollar=yollar,
                   kutu_glb=[[round(float(x), 2) for x in lo], [round(float(x), 2) for x in hi]])
    print(ad, "engel", len(E), "taşınan", len(tasinan), sorted({CID[P[i]["id"]]["modul"] for i in E}))
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
