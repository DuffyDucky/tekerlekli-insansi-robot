# P10.8d: taban-analiz.json özet farkı (HEAD ↔ çalışma ağacı). Düz Python, salt okunur.
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108d-analiz-fark.py
import json, os, subprocess, sys

ROBOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
YOL = "tasarim/freecad/taban/taban-analiz.json"
once = json.loads(subprocess.run(["git", "-C", ROBOT, "show", "HEAD:" + YOL], capture_output=True, check=True).stdout.decode("utf-8"))
sonra = json.load(open(os.path.join(ROBOT, YOL), encoding="utf-8"))


def ozet(d):
    bk = d["baglanti_kontrol"]
    r = dict(parca=d["parca_sayisi"], referans=d["referans_sayisi"], baski=d["baski_sayisi"], lazer=d["lazer_sayisi"],
             gecersiz=len(d["gecersiz"]), coklu_kati=len(d["coklu_kati"]), ic_cakisma=len(d["ic_cakisma"]), cift=d["cift_sayisi"],
             baglanti=len(bk), baglanti_hata=sum(1 for b in bk if not b.get("tamam")), kutle_g=d["kutle_g"], kutle_payli_g=d["kutle_payli_g"],
             am=d["agirlik_merkezi"], am_payli=d["agirlik_merkezi_payli"], step_kati=d["step_kati"], joints_ok=d["joints_ok"],
             bolge=json.dumps(d["bolge"], ensure_ascii=False)[:300])
    for k in ("iskelet", "kabuk"):
        v = d[k]
        r[k] = {a: (len(b) if isinstance(b, list) else b) for a, b in v.items()} if isinstance(v, dict) else v
    rb = d.get("robot", {})
    r["robot_kutle_am"] = {k: rb[k] for k in ("tabansiz_kutle_g", "tabansiz_am") if k in rb}
    r["donus"] = json.dumps(d.get("donus"), ensure_ascii=False)[:400]
    return r


a, b = ozet(once), ozet(sonra)
for k in a:
    isaret = "  " if a[k] == b[k] else "≠ "
    print("%s%-14s HEAD %s" % (isaret, k, json.dumps(a[k], ensure_ascii=False)[:220]))
    if a[k] != b[k]:
        print("  %-14s ŞİMDİ %s" % ("", json.dumps(b[k], ensure_ascii=False)[:220]))
yeni = sorted({p["ad"] for p in sonra["parcalar"]} - {p["ad"] for p in once["parcalar"]})
gitti = sorted({p["ad"] for p in once["parcalar"]} - {p["ad"] for p in sonra["parcalar"]})
print("yeni parça %d, giden %d" % (len(yeni), len(gitti)))
for x in yeni + ["- " + g for g in gitti]:
    print("   ", x)
hata = [x for x in sonra["baglanti_kontrol"] if not x.get("tamam")]
print("bağlantı hatası:", [x["ad"] for x in hata])
print("yeni kartların bağlantıları:", [(x["ad"][:50], x["tamam"]) for x in sonra["baglanti_kontrol"]
                                       if "dugum" in x["ad"] or "Dagitim karti C" in x["ad"] or "On sarj" in x["ad"]])
