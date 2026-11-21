# P10.8e: gösterim şemalarının ölçüm girdisi (düz Python; FreeCAD istemez). P108d-sema-girdi.py ile aynı kural, etiketli çıktı.
# Noktalar rehberin tek çözücüsünden (rehber_kablo.sema_noktalari: "taban" = lale158/kablo_yolu_taban.py, "kafa_ici" =
# lale158/kablo_yolu_kafa.py; global ev pozu, mm). Çizim yarıçapı rehberin çizdiği tüp (rehber_kablo.Tablo.yaricap: KESIT_YARICAP,
# "okunur ölçek, gerçek çap değil"). Çıktı: P108e-olcum/sema-girdi-<etiket>.json.
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108e-sema-girdi.py <etiket>
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_kablo as RK  # noqa: E402

ETIKET = sys.argv[1] if len(sys.argv) > 1 else "olcum"
TB = RK.Tablo()
out = []
for kaynak in ("taban", "kafa_ici"):
    for ad in RK.kaynak_yollari()[kaynak]:
        pts = RK.sema_noktalari(kaynak, ad)
        kimlik = ad if ad in TB.K else None
        out.append(dict(kaynak=kaynak, ad=ad, kimlik=kimlik, r_cizim=TB.yaricap(kimlik) if kimlik else RK.R_VARSAYILAN,
                        noktalar=[[round(c, 4) for c in p] for p in pts]))
os.makedirs(os.path.join(HERE, "P108e-olcum"), exist_ok=True)
json.dump(dict(not_="rehber_kablo.sema_noktalari + Tablo.yaricap; 11 taban + 5 kafa içi", etiket=ETIKET, semalar=out),
          open(os.path.join(HERE, "P108e-olcum", "sema-girdi-%s.json" % ETIKET), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(out), "şema:", ", ".join("%s/%s r%.1f" % (s["kaynak"], s["ad"], s["r_cizim"]) for s in out))
