# -*- coding: utf-8 -*-
"""Maliyet sayfasinin (viewer-template.html calc()) hesabini Python'da tekrarlar: V3, yazici, yedek dahil, pay.
Kosullu kalemler (secenek "kosullu") ayri toplanir.  py -3 planlama/adim5/maliyet_toplam.py [maliyet.json]
"""
import json, os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
yol = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "maliyet.json")
d = json.load(open(yol, encoding="utf-8"))
def ver_ok(it): return not it.get("ver") or "v3" in it["ver"].split(",")
def on(it, kosullu=False):
    s = it.get("secenek")
    if s and s != d.get("baski", "yazici") and not (kosullu and s == "kosullu"):
        return False
    return ver_ok(it)
def toplam(kosullu=False, filtre=None):
    t = 0.0; by = collections.defaultdict(float)
    for it in d["kalemler"]:
        if on(it, kosullu) and (filtre is None or filtre(it)):
            t += it["adet"] * it["tl"]; by[it.get("kosullu") or it.get("secenek") or it["g"]] += it["adet"] * it["tl"]
    return t, by
ara, by = toplam()
araK, byK = toplam(True)
print("kalem (V3 gorunen): %d" % sum(1 for it in d["kalemler"] if on(it)))
print("ara toplam %.2f  pay %.0f%%  genel %.2f" % (ara, d["pay"] * 100, ara * (1 + d["pay"])))
print("kosullular dahil ara %.2f  genel %.2f" % (araK, araK * (1 + d["pay"])))
for k, v in sorted(byK.items(), key=lambda x: -x[1]): print("  %-12s %10.2f" % (k, v))
