# Kupon tazeligi denetimi (P10.8a duzeltme 1, 19.11.2026). FreeCAD gerekmez, depoya yazmaz.
# Kupon betikleri kaynak parcadan olcer, ama kaynak degisince kupon betik yeniden kosulana kadar eski kalir. Bu denetim:
#   - yanak (kafa/yanak-kuponu.json) ve bant (kabuk/bant-kuponu.json): kayitli kaynak FCStd md5'i <-> bugunku FCStd md5'i,
#     kayitli STL md5'i <-> bugunku STL md5'i;
#   - M7 (test/m7-kupon-sonuc.json): kayitli arayuz degerleri <-> bugunku arayuz.py. Fark arayuz_fark_bugun kaydiyla (anahtar + kayitli
#     eski deger + o gunku deger) tam ayniysa BILINEN ESKI (cikisi bozmaz); degilse YENI ESKIME.
# Cikis: 0 = taze (bilinen eski olabilir), 1 = en az bir ESKI / YENI ESKIME / YOK. --kati: bilinen eski de 1 verir.
# Calistirma (depo kokunden): py -3 tasarim/freecad/test/kupon_tazelik.py [--kati]
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


sonuc = []          # (durum, kupon, ayrinti)  durum: TAZE / ESKI / BILINEN ESKI / YOK


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

# M7: arayuz karsilastirmasi
sp = importlib.util.spec_from_file_location("arayuz_tazelik", os.path.join(FC, "arayuz.py"))
A = importlib.util.module_from_spec(sp)
sp.loader.exec_module(A)
m = json.load(open(os.path.join(HERE, "m7-kupon-sonuc.json"), encoding="utf-8"))
# bilinen eskilik: m7-kupon-sonuc.json arayuz_fark_bugun (anahtar -> kayit / bugun), yalniz_c kipinde yazilir. Bir fark ancak anahtar,
# kayitli eski deger VE o gunku "bugun" degeri tam tutarsa BILINEN ESKI; bugunku deger kayittakinden farkliysa ya da kayitta olmayan
# bir anahtar degistiyse YENI ESKIME (cikis 1). (P10.8a kontrol T1-2: anahtar adiyla eslemek yeni eskimeyi gizliyordu.)
bilinen = m.get("arayuz_fark_bugun", {}) if "yalniz_c" in m else {}
fark = []
for k, v in m["arayuz"].items():
    bug = json.loads(json.dumps(getattr(A, k, None)))
    if isinstance(v, dict) and isinstance(bug, dict):
        for kk, vv in v.items():
            if kk in bug and bug[kk] != vv:
                fark.append(("%s.%s" % (k, kk), vv, bug[kk]))
    elif bug is not None and bug != v:
        fark.append((k, v, bug))
if not fark:
    sonuc.append(("TAZE", "M7 (C / D1 / D2 / E)", "arayuz degerleri bugunku arayuz.py ile ayni"))
for ad, vv, b in fark:
    kb = bilinen.get(ad)
    if kb is not None and kb.get("kayit") == vv and kb.get("bugun") == b:
        durum, ek = "BILINEN ESKI", " (m7-kupon-sonuc.json arayuz_fark_bugun ile ayni)"
    elif kb is not None:
        durum, ek = "YENI ESKIME", " (kayitli bilinen fark: kayit %s / o gun %s; bugun farkli)" % (kb.get("kayit"), kb.get("bugun"))
    else:
        durum, ek = "YENI ESKIME", " (arayuz_fark_bugun'da yok)"
    sonuc.append((durum, "M7 D1 / D2 / E" if ad.startswith("DIRSEK") else "M7", "arayuz.%s kayit %s / bugun %s%s" % (ad, vv, b, ek)))

for d, a, x in sonuc:
    print("%-12s %-22s %s" % (d, a, x))
kotu = [s for s in sonuc if s[0] in ("ESKI", "YOK", "YENI ESKIME") or (KATI and s[0] == "BILINEN ESKI")]
print("SONUC:", "ESKI VAR (%d)" % len(kotu) if kotu else "TAZE" + (" (bilinen eski: %d)" % sum(s[0] == "BILINEN ESKI" for s in sonuc)
                                                                        if any(s[0] == "BILINEN ESKI" for s in sonuc) else ""))
sys.exit(1 if kotu else 0)
