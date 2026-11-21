import os, sys, json
R = sys.argv[1]
sys.path.insert(0, os.path.join(R, "tasarim", "freecad", "rehber"))
import rehber_kablo as RK
TB = RK.Tablo()
out = []
for kaynak, adlar in RK.kaynak_yollari().items():
    for ad in adlar:
        pts = RK.sema_noktalari(kaynak, ad)
        k = ad if ad in TB.K else None
        out.append(dict(kaynak=kaynak, ad=ad, r_cizim=TB.yaricap(k) if k else RK.R_VARSAYILAN, noktalar=[list(map(float, p)) for p in pts]))
json.dump(dict(semalar=out), open(sys.argv[2], "w", encoding="utf-8"), indent=1)
print(len(out), [(s["kaynak"], s["ad"], len(s["noktalar"])) for s in out])
