# K3 regresyon (sistem Python'u, FreeCAD gerekmez). Y1b oncesi (HEAD 102f246) analiz JSON'lari ile simdiki: parca sayisi, kutle,
# baski, BOM, statik; eklem_sinirlari.json <-> uretici (arayuz.eklem_sinirlari) ve bagimli sinir semantigi; taslak-170 kutle.
# Yalniz okur. Cikti: K3-regresyon.json
import os, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(HERE, "..", ".."))
F = os.path.join(KOK, "tasarim", "freecad")
sys.path.insert(0, F)
import arayuz as A
HEAD = "102f246"
OUT = dict(head=HEAD)


def git_json(rel):
    r = subprocess.run(["git", "show", "%s:%s" % (HEAD, rel)], cwd=KOK, capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))


def simdi(rel):
    return json.load(open(os.path.join(KOK, rel), encoding="utf-8"))


def kisa(v, n=500):
    s = json.dumps(v, default=str, ensure_ascii=False)
    return v if len(s) < n else "(uzun %d)" % len(s)


def fark(a, b, yol="", out=None, derin=6):
    out = [] if out is None else out
    if derin == 0:
        if a != b:
            out.append((yol, kisa(a, 200), kisa(b, 200)))
        return out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            fark(a.get(k), b.get(k), yol + "/" + str(k), out, derin - 1)
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and len(a) < 400:
        for i, (p, q) in enumerate(zip(a, b)):
            fark(p, q, yol + "[%d]" % i, out, derin - 1)
    elif a != b:
        out.append((yol, kisa(a, 200), kisa(b, 200)))
    return out


def parca_listesi(d):
    for k in ("parcalar", "parca", "bom"):
        if k in d and isinstance(d[k], list):
            return d[k]
    return []


def ad_kutle(lst):
    out = {}
    for p in lst:
        if isinstance(p, dict):
            ad = p.get("ad") or p.get("Ad") or p.get("parca")
            m = p.get("kutle") if p.get("kutle") is not None else p.get("kutle_g")
            if ad is not None:
                out.setdefault(ad, []).append(m)
    return out


for mod, rel in (("omuz", "tasarim/freecad/omuz/omuz-analiz.json"), ("kabuk", "tasarim/freecad/kabuk/kabuk-analiz.json"),
                 ("dirsek", "tasarim/freecad/dirsek/dirsek-analiz.json"), ("omuz_baski", "tasarim/freecad/omuz/omuz-baski.json"),
                 ("taslak_kutle", "tasarim/freecad/taslak-170/kutle.json"), ("taslak_analiz", "tasarim/freecad/taslak-170/taslak-analiz.json")):
    a, b = git_json(rel), simdi(rel)
    r = dict(anahtar_eklenen=sorted(set(b) - set(a)), anahtar_silinen=sorted(set(a) - set(b)),
             degisen_ust_anahtar=sorted(k for k in set(a) & set(b) if a[k] != b[k]))
    pa, pb = ad_kutle(parca_listesi(a)), ad_kutle(parca_listesi(b))
    r["parca_sayisi"] = [len(parca_listesi(a)), len(parca_listesi(b))]
    r["parca_eklenen"] = sorted(set(pb) - set(pa))
    r["parca_silinen"] = sorted(set(pa) - set(pb))
    r["kutle_degisen_parca"] = [(k, pa[k], pb[k]) for k in sorted(set(pa) & set(pb)) if pa[k] != pb[k]]
    ayr = fark(a, b)
    r["fark_sayisi"] = len(ayr)
    r["fark"] = [q for q in ayr if not any(s in q[0] for s in ("/sure", "/tarih", "/log", "/zaman", "_s", "/baslangic", "/bitis"))][:250]
    OUT[mod] = r
    print("==", mod, "parca", r["parca_sayisi"], "eklenen", r["parca_eklenen"], "silinen", r["parca_silinen"])
    print("   ust anahtar degisen:", r["degisen_ust_anahtar"])
    print("   kutle degisen:", ascii(r["kutle_degisen_parca"])[:800])
    for q in r["fark"][:60]:
        print("   ", ascii(q)[:260])

# kabuk BOM (csv)
r = subprocess.run(["git", "diff", HEAD, "--", "tasarim/freecad/kabuk/kabuk-bom.csv"], cwd=KOK, capture_output=True)
OUT["kabuk_bom_diff"] = r.stdout.decode("utf-8", "replace").splitlines()[-12:]
print("kabuk bom diff:", ascii(OUT["kabuk_bom_diff"]))

# eklem sinirlari: json == uretici; uretici --kontrol; bagimli semantik
es = json.load(open(os.path.join(KOK, "kod", "ortak", "eklem_sinirlari.json"), encoding="utf-8"))
uret = json.loads(json.dumps(A.eklem_sinirlari()))
OUT["eklem_json_uretici_ayni"] = (uret == es)
OUT["eklem_json_fark"] = fark(uret, es)[:20]
k = subprocess.run([sys.executable, os.path.join(KOK, "kod", "ortak", "eklem_sinirlari_uret.py"), "--kontrol"], cwd=KOK, capture_output=True)
OUT["uretici_kontrol"] = dict(kod=k.returncode, cikti=(k.stdout + k.stderr).decode("utf-8", "replace")[-600:])
esk = git_json("kod/ortak/eklem_sinirlari.json")
OUT["eklem_json_head_fark"] = fark(esk, es)[:40]
bag = es.get("bagimli", [])
sem = []
e = es["eklemler"]
for b in bag:
    (ks, kv), = b["kosul"].items()
    (ss, sv), = b["sinir"].items()
    sem.append(dict(ad=b["ad"], taraf=b["taraf"], kosul=(ks, kv), sinir=(ss, sv), kosul_ust_eklem_max=kv[1] == e[ks]["max"],
                    sinir_alt_eklem_min=sv[0] == e[ss]["min"], ayni_taraf=ks[0] == ss[0] == b["taraf"],
                    s2_max=sv[1], s1_esik=kv[0], kol_kablo=A.KOL_KABLO["s1"]["s2_s1_kosul"]))
OUT["bagimli"] = sem
OUT["eklemler_head_ayni"] = (esk["eklemler"] == es["eklemler"])
OUT["yasak_kol_kosulu"] = es["kafa_kol_yasak"]["sag_kol"]["kol_kosulu"]
print("eklem json == uretici:", OUT["eklem_json_uretici_ayni"], "uretici --kontrol:", OUT["uretici_kontrol"]["kod"], ascii(OUT["uretici_kontrol"]["cikti"][-200:]))
print("eklem json HEAD farki:", ascii(OUT["eklem_json_head_fark"])[:1500])
print("bagimli:", ascii(sem))
print("eklemler HEAD ile ayni:", OUT["eklemler_head_ayni"], "yasak kol kosulu:", OUT["yasak_kol_kosulu"])
# bagimli siniri okuyan kod var mi (yazilim tarafi)
hit = []
for kok, dirs, files in os.walk(os.path.join(KOK, "kod")):
    for f in files:
        if f.endswith((".py", ".cpp", ".h", ".ino", ".js", ".ts")):
            t = open(os.path.join(kok, f), encoding="utf-8", errors="replace").read()
            if "bagimli" in t or "eklem_sinirlari.json" in t:
                hit.append((os.path.relpath(os.path.join(kok, f), KOK), "bagimli" in t))
OUT["bagimli_okuyan_kod"] = hit
print("eklem_sinirlari.json / bagimli okuyan kod:", hit)
json.dump(OUT, open(os.path.join(HERE, "K3-regresyon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
