# P10.8d: rehber_kablo'nun CAD'e bağlı denetimleri (salt okunur; taban-analiz.json'u okur, hiçbir dosyaya yazmaz, rehber üretmez).
# Amaç: taban_parcalar.py değişikliğinin rehber tarafında neyi değiştirdiğini önce / sonra görmek (rehber paketi P10.8e'ye bilgi).
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108d-rehber-denetim.py [etiket]  -> P108d-olcum/rehber-<etiket>.json
import os, sys, json, inspect

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_kablo as RK  # noqa: E402

etiket = sys.argv[1] if len(sys.argv) > 1 else "olcum"
out = {}
for ad in sorted(n for n in dir(RK) if n.endswith("_denetle")):
    f = getattr(RK, ad)
    if any(p.default is inspect.Parameter.empty for p in inspect.signature(f).parameters.values()):
        out[ad] = "atlandı (zorunlu argüman)"
        continue
    try:
        r = f()
    except Exception as e:  # denetim kendi hatasını verirse kaydet, sürdür
        out[ad] = "HATA: %r" % (e,)
        continue
    if isinstance(r, tuple) and len(r) == 2 and all(isinstance(x, list) for x in r):
        out[ad] = dict(hata=r[0], bilgi=r[1])
    elif isinstance(r, list):
        out[ad] = dict(hata=r)
    else:
        out[ad] = repr(r)[:400]
os.makedirs(os.path.join(HERE, "P108d-olcum"), exist_ok=True)
json.dump(out, open(os.path.join(HERE, "P108d-olcum", "rehber-%s.json" % etiket), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for ad, r in out.items():
    if isinstance(r, dict):
        print("%-28s hata %3d  bilgi %3d" % (ad, len(r["hata"]), len(r.get("bilgi", []))))
    else:
        print("%-28s %s" % (ad, r[:100]))
