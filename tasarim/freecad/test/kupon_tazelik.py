# Kupon tazeligi denetimi (P10.8a duzeltme 1, 19.11.2026). FreeCAD gerekmez, depoya yazmaz.
# Kupon betikleri kaynak parcadan olcer, ama kaynak degisince kupon betik yeniden kosulana kadar eski kalir. Bu denetim:
#   - yanak (kafa/yanak-kuponu.json) ve bant (kabuk/bant-kuponu.json): kayitli kaynak FCStd md5'i <-> bugunku FCStd md5'i,
#     kayitli STL md5'i <-> bugunku STL md5'i;
#   - M7 (test/m7-kupon-sonuc.json): kaynak dirsek-montaj.FCStd md5'i, kupon STL md5'leri ve kayitli arayuz degerleri <-> bugunku
#     arayuz.py (P10.8c: D / E onarildi; "BILINEN ESKI" istisnasi kalkti, her fark ESKI);
#   - etek on bandi kuponu (kabuk/etek-kuponu.json, P10.8c): yanak / bant gibi kaynak FCStd ve STL md5'i.
# Cikis: 0 = taze, 1 = en az bir ESKI / YOK. --kati P10.8c'den beri etkisiz (bilinen eski yok), uyumluluk icin kabul edilir.
# Calistirma (depo kokunden): py -3 tasarim/freecad/test/kupon_tazelik.py
#   --bozma-denemesi: M7 arayuz karsilastirmasinin bozma ornekleri (silinen anahtar, degisen deger; P10.8c duzeltme turu 1).
# Zincire bagli degil (carpisma_kos.py / regresyon.py bunu cagirmaz).
import hashlib, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FC = os.path.dirname(HERE)
KOK = os.path.normpath(os.path.join(FC, "..", ".."))
KATI = "--kati" in sys.argv


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def yol(rel):
    return os.path.join(KOK, *rel.split("/"))


sonuc = []          # (durum, kupon, ayrinti)  durum: TAZE / ESKI / YOK


def kaynakli(ad, js):
    p = os.path.join(FC, *js.split("/"))
    if not os.path.exists(p):
        sonuc.append(("YOK", ad, js + " yok"))
        return
    d = json.load(open(p, encoding="utf-8"))
    k = d["kaynak"]
    if not os.path.exists(yol(k["fcstd"])):
        sonuc.append(("ESKI", ad, "kaynak FCStd yok: " + k["fcstd"]))
    else:
        bug = md5(yol(k["fcstd"]))
        sonuc.append(("TAZE" if bug == k["md5"] else "ESKI", ad, "kaynak %s md5 kayit %s / bugun %s" % (k["fcstd"], k["md5"][:8], bug[:8])))
    for pr in d.get("parcalar", []):
        s = pr.get("stl")
        if not s:
            continue
        if not os.path.exists(yol(s)):
            sonuc.append(("ESKI", ad, "STL yok: " + s))
            continue
        bug = md5(yol(s))
        sonuc.append(("TAZE" if bug == pr.get("stl_md5") else "ESKI", ad, "STL %s md5 kayit %s / bugun %s" % (s, str(pr.get("stl_md5"))[:8], bug[:8])))


kaynakli("yanak (K54)", "kafa/yanak-kuponu.json")
kaynakli("bant (K55)", "kabuk/bant-kuponu.json")
kaynakli("etek on bandi (K55)", "kabuk/etek-kuponu.json")      # P10.8c

# M7: kaynak FCStd + STL md5 (P10.8c) ve arayuz karsilastirmasi. P10.8c'de D / E bolumu onarildi (planlama/d158/P108c-gunluk.md § 3),
# M7_YALNIZ_C kipi ve "BILINEN ESKI" istisnasi kalkti: her fark ESKI.
sp = importlib.util.spec_from_file_location("arayuz_tazelik", os.path.join(FC, "arayuz.py"))
A = importlib.util.module_from_spec(sp)
sp.loader.exec_module(A)
m = json.load(open(os.path.join(HERE, "m7-kupon-sonuc.json"), encoding="utf-8"))
if "yalniz_c" in m:
    sonuc.append(("ESKI", "M7 D1 / D2 / E", "m7-kupon-sonuc.json yalniz_c kaydi tasiyor (D / E eski kosudan): tam kip kosulmali"))
k = m.get("kaynak")
if not k:
    sonuc.append(("ESKI", "M7 D1 / D2", "m7-kupon-sonuc.json kaynak FCStd md5'i yok (P10.8c oncesi kayit)"))
elif not os.path.exists(yol(k["fcstd"])):
    sonuc.append(("ESKI", "M7 D1 / D2", "kaynak FCStd yok: " + k["fcstd"]))
else:
    bug = md5(yol(k["fcstd"]))
    sonuc.append(("TAZE" if bug == k["md5"] else "ESKI", "M7 D1 / D2", "kaynak %s md5 kayit %s / bugun %s" % (k["fcstd"], k["md5"][:8], bug[:8])))
for kp in m["kuponlar"]:
    s_ = "tasarim/freecad/" + kp["stl"]
    if not os.path.exists(yol(s_)):
        sonuc.append(("ESKI", "M7", "STL yok: " + s_))
    elif "stl_md5" not in kp:
        sonuc.append(("ESKI", "M7", "STL md5 kaydi yok: " + s_))
    else:
        bug = md5(yol(s_))
        sonuc.append(("TAZE" if bug == kp["stl_md5"] else "ESKI", "M7", "STL %s md5 kayit %s / bugun %s" % (s_, kp["stl_md5"][:8], bug[:8])))
YOK_ = "(arayuz.py'de yok)"


def arayuz_fark(kayit, A):
    """kayitli arayuz blogu <-> bugunku arayuz modulu. P10.8c duzeltme turu 1 (P108c-kontrol D4): bugunku arayuz.py'den silinen anahtar
    (ust duzey ya da sozluk ici) sessizce atlanmaz, fark sayilir."""
    out = []
    for k_, v in kayit.items():
        if not hasattr(A, k_):
            out.append((k_, v, YOK_))
            continue
        bug = json.loads(json.dumps(getattr(A, k_)))
        if isinstance(v, dict) and isinstance(bug, dict):
            for kk, vv in v.items():
                if kk not in bug:
                    out.append(("%s.%s" % (k_, kk), vv, YOK_))
                elif bug[kk] != vv:
                    out.append(("%s.%s" % (k_, kk), vv, bug[kk]))
        elif bug != v:
            out.append((k_, v, bug))
    return out


if "--bozma-denemesi" in sys.argv:
    # arayuz_fark bozma ornekleri (depoya yazmaz; bugunku arayuz modulunun kopyasi uzerinde)
    import copy, types
    def kopya(**degis):
        ns = types.SimpleNamespace(**{k: copy.deepcopy(getattr(A, k)) for k in m["arayuz"] if hasattr(A, k)})
        for k, f in degis.items():
            f(ns)
        return ns
    denemeler = [
        ("temiz kopya (fark 0 olmali)", kopya(), False),
        ("DIRSEK['catal_dis_kol'] silindi", kopya(a=lambda ns: ns.DIRSEK.pop("catal_dis_kol")), True),
        ("TUP_PIM_R silindi (ust duzey)", kopya(a=lambda ns: delattr(ns, "TUP_PIM_R")), True),
        ("GECME['tup_pim'] 0,25 -> 0,3", kopya(a=lambda ns: ns.GECME.__setitem__("tup_pim", 0.3)), True),
    ]
    ok = 0
    for ad, ns, bek in denemeler:
        n = len(arayuz_fark(m["arayuz"], ns))
        iyi = (n > 0) == bek
        ok += iyi
        print("  %-40s %s (%d fark)" % (ad, ("YAKALANDI" if bek else "TEMIZ") if iyi else "KACTI", n))
    print("arayuz bozma denemesi: %d / %d" % (ok, len(denemeler)))
    sys.exit(0 if ok == len(denemeler) else 1)
fark = arayuz_fark(m["arayuz"], A)
if not fark:
    sonuc.append(("TAZE", "M7 (C / D1 / D2 / E)", "arayuz degerleri bugunku arayuz.py ile ayni"))
for ad, vv, b in fark:
    sonuc.append(("ESKI", "M7 D1 / D2 / E" if ad.startswith("DIRSEK") else "M7", "arayuz.%s kayit %s / bugun %s" % (ad, vv, b)))

for d, a, x in sonuc:
    print("%-12s %-22s %s" % (d, a, x))
kotu = [s for s in sonuc if s[0] in ("ESKI", "YOK")]
print("SONUC:", "ESKI VAR (%d)" % len(kotu) if kotu else "TAZE (%d denetim)" % len(sonuc))
sys.exit(1 if kotu else 0)
