# P10.8f: parça etiketi ölçümü (rehber_gorunum.etiket_isle → app.js ETK). F10d uç etiketi ölçümüyle aynı çekim: Chrome DevTools
# (F10a Cdp), ?adim=…&cekim=1&sahne=1 (1200 x 720, yazdırma karesi) ve ?adim=…&cekim=1 (1400 x 900, etkileşimli), açık tema.
# Kural: verideki her yazı iki kipte de çizilmeli (cizilmedi boş, DOM g.etk sayısı = veri), kutu güvenli alanın içinde, parça
# etiketi kutuları birbiriyle ve uç etiketi kutularıyla çakışmaz. Yalnız okur; JSON'u verilen yola yazar.
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108f-etiket-olc.py [--rehber DIR] [--json YOL] [--png DIR]
import argparse, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
spec = importlib.util.spec_from_file_location("f10d", os.path.join(HERE, "F10d-dogrula.py"))
F10D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(F10D)


def konumlar(V):
    for a in V["adimlar"]:
        if a.get("etiket"):
            yield a["i"], 0, a
        for j, g in enumerate(a.get("sira_grup") or [], 1):
            if g.get("etiket"):
                yield a["i"], j, g


def ust(a, b):
    return a["x0"] < b["x1"] and b["x0"] < a["x1"] and a["y0"] < b["y1"] and b["y0"] < a["y1"]


def degerlendir(olc, V):
    hata = []
    for s, j, g in konumlar(V):
        ad = F10D.adr(s, j)
        bek = sorted(u["t"] for u in g["etiket"])
        for kip in ("sahne", "etk"):
            o = (olc.get(ad) or {}).get(kip) or {}
            ciz = o.get("ciz") or []
            if sorted(u["t"] for u in ciz) != bek:
                hata.append("%s %s: çizilen %s, veri %s; çizilmeyen %s" % (ad, kip, sorted(u["t"] for u in ciz), bek,
                                                                         [(u["t"], u["neden"]) for u in o.get("cizilmedi") or []]))
            if o.get("dom") != len(ciz):
                hata.append("%s %s: DOM g.etk %s ≠ çizilen %d" % (ad, kip, o.get("dom"), len(ciz)))
            for u in ciz:
                k, al = u["kutu"], u["alan"]
                if k["x0"] < al["x0"] - 0.5 or k["x1"] > al["x1"] + 0.5 or k["y0"] < al["y0"] - 0.5 or k["y1"] > al["y1"] + 0.5:
                    hata.append("%s %s: %s kutusu güvenli alanın dışında" % (ad, kip, u["t"]))
            for i, u in enumerate(ciz):
                for q in ciz[i + 1:]:
                    if ust(u["kutu"], q["kutu"]):
                        hata.append("%s %s: %s ile %s çakışıyor" % (ad, kip, u["t"], q["t"]))
                for q in o.get("uc_kutu") or []:
                    if ust(u["kutu"], q):
                        hata.append("%s %s: %s uç etiketi %s ile çakışıyor" % (ad, kip, u["t"], q["n"]))
    return hata


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehber", default=os.path.join(ROBOT, "rehber"))
    ap.add_argument("--json")
    ap.add_argument("--png", metavar="DIR", help="iki kipin karesini de DIR/<adres>-{sahne,etk}.png olarak yaz (DevTools çekimi)")
    g = ap.parse_args()
    kok = os.path.abspath(g.rehber)
    V = json.load(open(os.path.join(kok, "veri", "rehber-veri.json"), encoding="utf-8"))
    c = F10D.Cdp(F10D.tarayici(), "p108f")
    olc = {}
    try:
        for s, j, _g in konumlar(V):
            ad = F10D.adr(s, j)
            c.boyut(1200, 720)
            c.git(F10D.url(kok, "?adim=%s&cekim=1&sahne=1&tema=light" % ad))
            sahne = c.js("RehberTest.etiket()") or {}
            if g.png:
                c.goruntu(os.path.join(g.png, "%s-sahne.png" % ad.replace(".", "-")))
            c.boyut(1400, 900)
            c.git(F10D.url(kok, "?adim=%s&cekim=1&tema=light" % ad))
            etk = c.js("RehberTest.etiket()") or {}
            if g.png:
                c.goruntu(os.path.join(g.png, "%s-etk.png" % ad.replace(".", "-")))
            olc[ad] = dict(sahne=sahne, etk=etk)
    finally:
        c.kapat()
    hata = degerlendir(olc, V)
    r = dict(konum=len(olc), yazi=sum(len(x["etiket"]) for _s, _j, x in konumlar(V)), hata=hata, olcum=olc, gecti=not hata)
    if g.json:
        json.dump(r, open(g.json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for ad, o in olc.items():
        for kip in ("sahne", "etk"):
            x = o[kip]
            print("  %-6s %-5s tuval %sx%s çizilen %d, çizilmeyen %s" % (ad, kip, round(x.get("tuval", {}).get("w", 0)),
                  round(x.get("tuval", {}).get("h", 0)), len(x.get("ciz") or []),
                  [(u["t"], u["neden"], round(u.get("x", -1)), round(u.get("y", -1))) for u in x.get("cizilmedi") or []]))
    for h in hata:
        print("  HATA", h)
    print("parca etiketi: %d konum, %d yazi; hata %d -> %s" % (r["konum"], r["yazi"], len(hata), "GECTI" if not hata else "KALDI"))
    sys.exit(0 if not hata else 2)


if __name__ == "__main__":
    main()
