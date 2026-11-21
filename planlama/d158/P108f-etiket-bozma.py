# P10.8f: rehber_gorunum.etiket_isle bozma sınaması (FreeCAD'siz, depoya yazmaz). Veri ve robot.glb depodan yalnız okunur; her bozma
# rehber_metin.PARCA_ETIKET'in ya da parça kutularının bellekteki kopyasını bozar, etiket_isle SystemExit vermeli. Sağlam koşu geçmeli.
# Koşu (depo kökünden): py -3 -B -X utf8 planlama/d158/P108f-etiket-bozma.py
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROBOT, "tasarim", "freecad", "rehber"))
import rehber_gorunum as RG  # noqa: E402
import rehber_metin as RM  # noqa: E402

V0 = json.load(open(os.path.join(RG.VERI_DIR, "rehber-veri.json"), encoding="utf-8"))
M = RG.Mesh(V0)
K0 = {pid: (q["bmin"].copy(), q["bmax"].copy()) for pid, q in M.P.items()}
ASIL = copy.deepcopy(RM.PARCA_ETIKET)
A1, A2 = "Bara cıvatası M5x25 DIN 933 (anahtarlı 1)", "Bara cıvatası M5x25 DIN 933 (anahtarlı 2)"
ID = {p["ad"]: p["id"] for p in V0["parcalar"]}


def kos(tanim=None, kutu=None):
    RM.PARCA_ETIKET = tanim if tanim is not None else copy.deepcopy(ASIL)
    try:
        n = RG.etiket_isle(copy.deepcopy(V0), kutu or K0)
        return "gecti (%d yazı)" % n
    except SystemExit as e:
        return "durdu: %s" % e


def takas_x():
    k = dict(K0)
    a, b = ID[A1], ID[A2]
    (amin, amax), (bmin, bmax) = k[a], k[b]
    dx = (bmin[0] + bmax[0]) / 2 - (amin[0] + amax[0]) / 2
    k[a] = (amin + [dx, 0, 0], amax + [dx, 0, 0])
    k[b] = (bmin - [dx, 0, 0], bmax - [dx, 0, 0])
    return k


def bozuk(f):
    t = copy.deepcopy(ASIL)
    f(t)
    return t


BOZMA = [
    ("desen hiçbir parçaya uymuyor", dict(tanim=bozuk(lambda t: t[("B5a", 0)]["desen"].__setitem__(0, (r"^Acil stop dugum", "x"))))),
    ("aynı yazı iki parçaya (numarasız yazı numaralı desende)",
     dict(tanim=bozuk(lambda t: t[("K1", 4)]["desen"].__setitem__(0, (t[("K1", 4)]["desen"][0][0], "A"))))),
    ("iki desen aynı yazıyı veriyor", dict(tanim=bozuk(lambda t: t[("K1", 4)]["desen"].__setitem__(1, (t[("K1", 4)]["desen"][1][0], "A{1}"))))),
    ("numara x sırasında değil (anahtarlı 1 / 2 kutuları yer değiştirdi)", dict(kutu=takas_x())),
    ("alt adım yok (K1.40)", dict(tanim=bozuk(lambda t: t.__setitem__(("K1", 40), t.pop(("K1", 4)))))),
    ("alt adımlı adımda numarasız konum (K1, 0)", dict(tanim=bozuk(lambda t: t.__setitem__(("K1", 0), t.pop(("K1", 4)))))),
    ("parça bu konumda takılı değil (B5a karesinde K1 sonrası parça)", dict(tanim=bozuk(lambda t: t[("B5a", 0)]["desen"].append((r"^ESP32 DevKit", "E"))))),
    ("adım veride yok", dict(tanim=bozuk(lambda t: t.__setitem__(("X9", 0), t[("B5a", 0)])))),
]

if __name__ == "__main__":
    s = kos()
    print("saglam:", s)
    ok = s.startswith("gecti")
    for ad, kw in BOZMA:
        r = kos(**kw)
        yak = r.startswith("durdu")
        ok = ok and yak
        print("%s %s -> %s" % ("YAKALANDI" if yak else "KACTI", ad, r[:160]))
    print("SONUC:", "GECER (%d / %d)" % (len(BOZMA), len(BOZMA)) if ok else "KALDI")
    sys.exit(0 if ok else 1)
