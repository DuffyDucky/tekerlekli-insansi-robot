# K2 kontrolu 3: regresyon (sistem Python'u, FreeCAD gerekmez). Analiz JSON'larini HEAD (c299754) ile karsilastirir, eklem siniri
# tutarliligini ve "yana 0" / "3.0" kalintilarini tarar. Yalniz okur. Cikti: K2-regresyon.json
import os, sys, json, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(HERE, "..", ".."))
F = os.path.join(KOK, "tasarim", "freecad")
sys.path.insert(0, F)
import arayuz as A
HEAD = "c299754"
OUT = {}


def git_json(rel):
    r = subprocess.run(["git", "show", "%s:%s" % (HEAD, rel)], cwd=KOK, capture_output=True)
    return json.loads(r.stdout.decode("utf-8"))


def simdi(rel):
    return json.load(open(os.path.join(KOK, rel), encoding="utf-8"))


def parcalar(d):
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
                 ("dirsek", "tasarim/freecad/dirsek/dirsek-analiz.json")):
    a, b = git_json(rel), simdi(rel)
    r = dict(anahtar_eklenen=sorted(set(b) - set(a)), anahtar_silinen=sorted(set(a) - set(b)))
    for k in ("parca_sayisi", "baski_sayisi", "gecersiz", "coklu_kati", "statik", "cakisma", "iskelet_cakisma", "kutle", "kutle_g",
              "kutle_grup", "agirlik_merkezi", "bosluk", "eklem_siniri", "m6_vida_pay"):
        if k in a or k in b:
            va, vb = a.get(k), b.get(k)
            if va != vb:
                r[k] = dict(once=va if len(json.dumps(va, default=str)) < 600 else "(uzun)", sonra=vb if len(json.dumps(vb, default=str)) < 600 else "(uzun)")
    pa, pb = ad_kutle(parcalar(a)), ad_kutle(parcalar(b))
    r["parca_eklenen"] = sorted(set(pb) - set(pa))
    r["parca_silinen"] = sorted(set(pa) - set(pb))
    deg = []
    for k in sorted(set(pa) & set(pb)):
        if pa[k] != pb[k]:
            deg.append((k, pa[k], pb[k]))
    r["kutle_degisen_parca"] = deg
    r["degisen_ust_anahtar"] = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    if "bom" in a:
        def bm(x):
            out = {}
            for q in x:
                if isinstance(q, dict):
                    key = q.get("kod") or q.get("ad") or json.dumps(q, sort_keys=True)
                else:
                    key = json.dumps(q[:-1] if len(q) > 1 else q, ensure_ascii=True)
                out[key] = q
            return out
        ba, bb = bm(a["bom"]), bm(b["bom"])
        r["bom_eklenen"] = [bb[k] for k in sorted(set(bb) - set(ba))]
        r["bom_silinen"] = sorted(set(ba) - set(bb))
        r["bom_degisen"] = [(k, ba[k], bb[k]) for k in sorted(set(ba) & set(bb)) if ba[k] != bb[k]]
    if "baski" in a:
        def bk(x):
            return {(q.get("parca") or q.get("ad")) if isinstance(q, dict) else str(q[0]): q for q in x}
        ka, kb = bk(a["baski"]), bk(b["baski"])
        r["baski_eklenen"] = sorted(set(kb) - set(ka))
        r["baski_degisen"] = [(k, {f: (ka[k].get(f), kb[k].get(f)) for f in set(ka[k]) | set(kb[k]) if ka[k].get(f) != kb[k].get(f) and
                                   len(json.dumps(ka[k].get(f), default=str)) < 120}) if isinstance(ka[k], dict) else (k, ka[k], kb[k])
                              for k in sorted(set(ka) & set(kb)) if ka[k] != kb[k]]
    if mod == "omuz":
        ya = A.OMUZ["yana_aralik"]
        def serb(d):
            return {k: v for k, v in d["serbest"].items()}
        sa, sb = serb(a), serb(b)
        r["serbest_farkli_poz"] = [(k, sa.get(k), sb.get(k)) for k in sorted(set(sa) | set(sb)) if sa.get(k) != sb.get(k)][:20]
        r["statik_s2_0"] = b.get("statik_s2_0")
        ta, tb = a["tork"], b["tork"]
        r["tork_max_once_sonra"] = [max(abs(v[0]) for v in ta.values()), max(abs(v[0]) for v in tb.values()),
                                    max(abs(v[1]) for v in ta.values()), max(abs(v[1]) for v in tb.values())]
    OUT[mod] = r

# eklem sinirlari tutarliligi
es = json.load(open(os.path.join(KOK, "kod", "ortak", "eklem_sinirlari.json"), encoding="utf-8"))
uret = A.eklem_sinirlari()
OUT["eklem_sinirlari_json_uretici_ayni"] = (json.loads(json.dumps(uret)) == es)
if not OUT["eklem_sinirlari_json_uretici_ayni"]:
    fark = []
    def cmp(x, y, yol=""):
        if isinstance(x, dict) and isinstance(y, dict):
            for k in set(x) | set(y):
                cmp(x.get(k), y.get(k), yol + "/" + str(k))
        elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
            for i, (p, q) in enumerate(zip(x, y)):
                cmp(p, q, yol + "[%d]" % i)
        elif x != y:
            fark.append((yol, x, y))
    cmp(json.loads(json.dumps(uret)), es)
    OUT["eklem_sinirlari_fark"] = fark[:20]
OUT["OMUZ_yana"] = list(A.OMUZ["yana_aralik"])
OUT["json_r_s2"] = [es["eklemler"]["r_s2"]["min"], es["eklemler"]["r_s2"]["max"]]
OUT["json_l_s2"] = [es["eklemler"]["l_s2"]["min"], es["eklemler"]["l_s2"]["max"]]
OUT["yasak_kol_kosulu"] = es["kafa_kol_yasak"]["sag_kol"]["kol_kosulu"]
for rel in ("tasarim/freecad/montaj/eklem-dogrulama.json", "tasarim/freecad/omuz/omuz-analiz.json"):
    try:
        d = simdi(rel)
        OUT["sinir_" + os.path.basename(rel)] = d.get("eklem_siniri") or d.get("sinir") or {k: d[k] for k in list(d)[:0]}
    except Exception as e:
        OUT["sinir_" + os.path.basename(rel)] = str(e)

# kalinti taramasi (kod + uretilmis kod disi rapor metinleri ayri)
desen = [r"yana[ _]?0\b", r"yana\s*0\s*[.…]", r"\(0,\s*0,\s*0,\s*0\)", r"yana_aralik.*3\.0", r"\b3\.0\s*,\s*120", r"alt sinir[^\n]{0,20}\b3\b",
         r"sinir 0\)", r"Y0 \(3\)", r"\(3 derece", r"yana 3\b", r"3\.\.\.120", r"3…120", r"0\.\.\.120", r"0…120"]
kal = []
for kok, dirs, files in os.walk(os.path.join(KOK)):
    if any(x in kok for x in (".git", "__pycache__", "node_modules", os.sep + "test", "adim4", "regresyon", "onceki")):
        continue
    for f in files:
        if not f.endswith((".py", ".json", ".md", ".html")) or f.startswith("K2-") or f.endswith(".step"):
            continue
        p = os.path.join(kok, f)
        if os.path.getsize(p) > 3e6:
            continue
        try:
            txt = open(p, encoding="utf-8").read()
        except Exception:
            continue
        for i, line in enumerate(txt.splitlines(), 1):
            for d in desen:
                if re.search(d, line):
                    kal.append((os.path.relpath(p, KOK), i, d, line.strip()[:160]))
                    break
OUT["kalinti"] = kal
json.dump(OUT, open(os.path.join(HERE, "K2-regresyon.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
for m in ("omuz", "kabuk", "dirsek"):
    print(m, ascii({k: v for k, v in OUT[m].items() if k not in ("kutle_degisen_parca", "bom_degisen", "baski_degisen", "bom_eklenen")})[:1500])
    for k in ("bom_eklenen", "bom_silinen", "bom_degisen", "baski_eklenen", "baski_degisen"):
        print("  ", k, ascii(OUT[m].get(k))[:1500])
print("eklem json == uretici:", OUT["eklem_sinirlari_json_uretici_ayni"], OUT.get("eklem_sinirlari_fark"))
print("yasak kol kosulu", OUT["yasak_kol_kosulu"])
print("kalinti", len(kal))
kod = [k for k in kal if k[0].startswith(("tasarim", "kod")) and k[0].endswith(".py")]
print("kod kalintisi", len(kod))
for k in kod:
    print("  ", ascii(k))
