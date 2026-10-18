# K2: kabuk-montaj.FCStd (09:21) arayuz.py (09:26) ve kablo_yolu.py'den (09:31) eski: kaset geometrisinin bagli oldugu turetilmis
# degerler guncel kaynaktan yeniden hesaplanir ve kabuk-analiz.json s1_kaset ile karsilastirilir. Dosya yazmaz (yalniz K2-tazelik.json).
import os, sys, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(HERE, "..", "..", "tasarim", "freecad"))
sys.path.insert(0, R); sys.path.insert(0, os.path.join(R, "dirsek"))
import arayuz as A
import kablo_yolu as KY
S1 = A.KOL_KABLO["s1"]
O = KY.s1_olcu(A.KOL_KABLO)
U = KY.s1_poz(A.KOL_KABLO, A.OMUZ["one_arka_aralik"][1], O)
psi_a = U["psi_U"] + O["U"]["delta"]
u2 = [(q.y, q.z) for q in U["u_nokta"]]
pm = S1["duvar"]["pim"]
ps = U["u_uc_psi"]
while True:
    c = KY.psi_yz(ps, pm["r"])
    if min(math.hypot(c[0] - a, c[1] - b) for a, b in u2) >= O["kalinlik"] / 2 + pm["bosluk"] + pm["post_r"] + 0.5:
        break
    ps += 0.5
an = json.load(open(os.path.join(R, "kabuk", "kabuk-analiz.json"), encoding="utf-8"))["s1_kaset"]
out = dict(guncel=dict(psi_a=psi_a, psi_uc=U["u_uc_psi"], pim_psi=ps), fcstd_analiz=dict(psi_a=an["psi_a"], psi_uc=an["psi_uc"], pim_psi=an["pim_psi"]),
           ayni=bool(abs(psi_a - an["psi_a"]) < 1e-6 and abs(ps - an["pim_psi"]) < 1e-6 and abs(U["u_uc_psi"] - an["psi_uc"]) < 1e-6),
           arayuz_duvar=S1["duvar"], dikme=S1["dikme"])
json.dump(out, open(os.path.join(HERE, "K2-tazelik.json"), "w", encoding="utf-8"), indent=1, default=str)
print(json.dumps(out, default=str)[:800])
