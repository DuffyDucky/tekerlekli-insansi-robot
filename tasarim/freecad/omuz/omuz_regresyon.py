# Omuz modulu regresyon kontrolu: omuz_montaj.py'yi calistirir, sayisal ozetini kaydeder, iki ozeti karsilastirir.
# Calistir: FC_SCRIPT=<bu dosya> REG_ETIKET=once|sonra freecadcmd run_fc.py
#   once  -> regresyon/once.json (degisiklikten once alinan referans)
#   sonra -> regresyon/sonra.json + regresyon/fark.json (once ile karsilastirma tablosu)
# Karsilastirilan: parca sayisi, her parcanin adi/grubu/hacmi/sinir kutusu/kati sayisi/gecerliligi/kutlesi/merkezi,
# statik cakisma, gruplar arasi bosluklar, hareket taramasi (875 poz), tork tablosu, BOM.
import os, json, runpy

HERE = os.path.dirname(os.path.abspath(__file__))
ETIKET = os.environ.get("REG_ETIKET", "sonra")
KLASOR = os.path.join(HERE, "regresyon")
os.makedirs(KLASOR, exist_ok=True)

ns = runpy.run_path(os.path.join(HERE, "omuz_montaj.py"), run_name="__main__")
P = ns["P"]


def r(x, n=9):
    return round(float(x), n)


oz = dict(
    parca_sayisi=len(P),
    parcalar=[dict(ad=p["ad"], grup=p["grup"], hacim=r(p["hacim"]), kati=p["kati"], gecerli=p["shape"].isValid(),
                   kutle=r(p["kutle"]), merkez=[r(p["merkez"].x), r(p["merkez"].y), r(p["merkez"].z)],
                   bb=[r(p["bb"].XMin), r(p["bb"].XMax), r(p["bb"].YMin), r(p["bb"].YMax), r(p["bb"].ZMin), r(p["bb"].ZMax)])
              for p in P],
    statik=ns["static"],
    bosluk={k: [r(v[0], 6), v[1], v[2]] for k, v in ns["gaps"].items()},
    kol_gobek={str(k): v for k, v in ns["kol_gobek"].items()},
    gobek_govde={str(k): v for k, v in ns["gobek_govde"].items()},
    kol_govde={"%d,%d" % k: v for k, v in ns["kol_govde"].items()},
    tork={"%d,%d" % k: [r(v[0]), r(v[1])] for k, v in ns["tork"].items()},
    bom=[[k[0], k[1], v] for k, v in sorted(ns["bom"].items())],
)
json.dump(oz, open(os.path.join(KLASOR, ETIKET + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("regresyon ozeti yazildi:", ETIKET, "parca", len(P))

ref = os.path.join(KLASOR, "once.json")
if ETIKET != "once" and os.path.exists(ref):
    a = json.load(open(ref, encoding="utf-8"))
    b = json.load(open(os.path.join(KLASOR, ETIKET + ".json"), encoding="utf-8"))
    satir = []

    def ekle(ad, x, y, sayisal=True):
        if sayisal:
            d = max(abs(float(u) - float(v)) for u, v in zip(x, y)) if isinstance(x, list) else abs(float(x) - float(y))
            satir.append(dict(olcut=ad, once=x, sonra=y, fark=d, ayni=d <= 1e-6))
        else:
            satir.append(dict(olcut=ad, once=x, sonra=y, fark=None, ayni=x == y))

    ekle("parca sayisi", a["parca_sayisi"], b["parca_sayisi"])
    ad_ayni = [p["ad"] for p in a["parcalar"]] == [p["ad"] for p in b["parcalar"]]
    satir.append(dict(olcut="parca adlari ve sirasi", once=len(a["parcalar"]), sonra=len(b["parcalar"]), fark=None, ayni=ad_ayni))
    if ad_ayni:
        dh = max(abs(p["hacim"] - q["hacim"]) for p, q in zip(a["parcalar"], b["parcalar"]))
        db = max(abs(u - v) for p, q in zip(a["parcalar"], b["parcalar"]) for u, v in zip(p["bb"], q["bb"]))
        dk = max(abs(p["kutle"] - q["kutle"]) for p, q in zip(a["parcalar"], b["parcalar"]))
        dm = max(abs(u - v) for p, q in zip(a["parcalar"], b["parcalar"]) for u, v in zip(p["merkez"], q["merkez"]))
        satir.append(dict(olcut="parca hacmi (en buyuk fark, mm3)", once=round(sum(p["hacim"] for p in a["parcalar"]), 3),
                          sonra=round(sum(p["hacim"] for p in b["parcalar"]), 3), fark=dh, ayni=dh <= 1e-6))
        satir.append(dict(olcut="sinir kutusu (en buyuk fark, mm)", once="70 x 6 deger", sonra="70 x 6 deger", fark=db, ayni=db <= 1e-6))
        satir.append(dict(olcut="parca kutlesi (en buyuk fark, g)", once=round(sum(p["kutle"] for p in a["parcalar"]), 3),
                          sonra=round(sum(p["kutle"] for p in b["parcalar"]), 3), fark=dk, ayni=dk <= 1e-6))
        satir.append(dict(olcut="agirlik merkezi (en buyuk fark, mm)", once="70 x 3", sonra="70 x 3", fark=dm, ayni=dm <= 1e-6))
        kv = [(p["kati"], p["gecerli"]) for p in a["parcalar"]] == [(p["kati"], p["gecerli"]) for p in b["parcalar"]]
        satir.append(dict(olcut="kati sayisi + isValid", once="hepsi 1 / gecerli" if all(p["kati"] == 1 and p["gecerli"] for p in a["parcalar"]) else "farkli",
                          sonra="hepsi 1 / gecerli" if all(p["kati"] == 1 and p["gecerli"] for p in b["parcalar"]) else "farkli", fark=None, ayni=kv))
    ekle("statik cakisma", len(a["statik"]), len(b["statik"]))
    for k in a["bosluk"]:
        ekle("bosluk " + k + " (mm)", a["bosluk"][k][0], b["bosluk"][k][0])
    for k in ("kol_gobek", "gobek_govde", "kol_govde"):
        na = sum(1 for v in a[k].values() if v)
        nb = sum(1 for v in b[k].values() if v)
        satir.append(dict(olcut="tarama %s: cakisan poz" % k, once=na, sonra=nb, fark=None, ayni=a[k] == b[k]))
    dt = max(abs(u - v) for k in a["tork"] for u, v in zip(a["tork"][k], b["tork"][k]))
    satir.append(dict(olcut="tork tablosu (%d poz, en buyuk fark kg*cm)" % len(a["tork"]),
                      once=max(max(v) for v in a["tork"].values()), sonra=max(max(v) for v in b["tork"].values()), fark=dt, ayni=dt <= 1e-6))
    satir.append(dict(olcut="BOM", once=len(a["bom"]), sonra=len(b["bom"]), fark=None, ayni=a["bom"] == b["bom"]))
    sonuc = dict(hepsi_ayni=all(s["ayni"] for s in satir), satirlar=satir)
    json.dump(sonuc, open(os.path.join(KLASOR, "fark.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for s in satir:
        print("%-45s %-22s %-22s %-12s %s" % (s["olcut"], str(s["once"])[:22], str(s["sonra"])[:22],
                                             "-" if s["fark"] is None else "%.3g" % s["fark"], "AYNI" if s["ayni"] else "FARKLI"))
    print("SONUC:", "BIREBIR AYNI" if sonuc["hepsi_ayni"] else "FARK VAR")
