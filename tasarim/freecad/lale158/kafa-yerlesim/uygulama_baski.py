# -*- coding: utf-8 -*-
# Lale 1,58 m - secim B + R1: yeni/degisen baski parcalari KL.baski_analiz ile (freecadcmd). Yalniz uygulama-baski.json yazar.
# FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
import os, sys, json, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LALE = os.path.dirname(HERE)
UST = os.path.dirname(LALE)
for p_ in (LALE, UST, os.path.join(UST, "kabuk"), os.path.join(UST, "kafa")):
    if p_ not in sys.path:
        sys.path.insert(0, p_)
import arayuz as A
import kabuk_parcalar as K
import kafa_lib as KL

t0 = time.time()
ALAN = ("ad", "olcu", "sigar", "destek_sorun_sayi", "desteksiz", "destek_sorun", "cikinti_orani", "kutle_g", "sure_saat", "ofset_uyari")
S = dict(tarih="2026-11-05", yontem="kafa_lib.baski_analiz, doluluk arayuz.KABUK_DOLULUK", parca={})
for ad in ("Ust arka servis kapagi", "Hoparlor kabi on halka", "Hoparlor kabi arka (flansli)", "Govde orta bandi sag"):
    d = K.PARCA[ad]
    r = KL.baski_analiz(ad, K.P[d["indeks"]]["shape"], d["yukari"], A.KABUK_DOLULUK)
    S["parca"][ad] = {k: r[k] for k in ALAN}
    S["parca"][ad]["yon"] = d["yon"]
    print(ad, r["olcu"], "destek", r["destek_sorun_sayi"], "desteksiz", r["desteksiz"], "kutle", r["kutle_g"], flush=True)
S["sure_s"] = round(time.time() - t0, 1)
json.dump(S, open(os.path.join(HERE, "uygulama-baski.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("BITTI", flush=True)
