# Iskelet modulu regresyon kontrolu (omuz_regresyon.py'nin esdegeri). iskelet_parcalar.py'yi import eder (dosya
# yazmaz: FCStd/STEP/analiz dokunulmaz), sayisal ozetini kaydeder, iki ozeti karsilastirir.
# Calistir: FC_SCRIPT=<bu dosya> REG_ETIKET=once|sonra freecadcmd run_fc.py
#   once  -> regresyon/once.json (ortak dosyalar degismeden once)
#   sonra -> regresyon/sonra.json + regresyon/fark.json (once ile karsilastirma)
# Karsilastirilan: parca sayisi, her parcanin adi/grubu/hacmi/sinir kutusu/kati sayisi/gecerliligi/kutlesi/merkezi,
# parca ici cakisma, baglanti listesi (govde + elemanlar), toplam kutle ve agirlik merkezi, ayrilmis bolge ihlali.
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import iskelet_parcalar as I
import arayuz as A
from ortak_lib import box

ETIKET = os.environ.get("REG_ETIKET", "sonra")
KLASOR = os.path.join(HERE, "regresyon")
os.makedirs(KLASOR, exist_ok=True)
P, BAG = I.P, I.BAG
TOL = 0.5


def r(x, n=9):
    return round(float(x), n)


cak = []
for i in range(len(P)):
    for j in range(i + 1, len(P)):
        if P[i]["bb"].intersect(P[j]["bb"]):
            v = P[i]["shape"].common(P[j]["shape"]).Volume
            if v > TOL:
                cak.append([P[i]["ad"], P[j]["ad"], r(v, 3)])
ihlal = []
for z in A.bolgeler(haric=("iskelet", "omuz_sag", "omuz_sol")):
    kb = box(*z["kutu"])
    for c in z["bosluk"]:
        kb = kb.cut(box(*c))
    for p in P:
        if p["bb"].intersect(kb.BoundBox):
            v = p["shape"].common(kb).Volume
            if v > TOL:
                ihlal.append([z["ad"], p["ad"], r(v, 2)])
M = sum(p["kutle"] for p in P)
cg = [sum(getattr(p["merkez"], k) * p["kutle"] for p in P) / M for k in "xyz"]
oz = dict(
    parca_sayisi=len(P),
    parcalar=[dict(ad=p["ad"], grup=p["grup"], hacim=r(p["hacim"]), kati=p["kati"], gecerli=p["shape"].isValid(),
                   kutle=r(p["kutle"]), merkez=[r(p["merkez"].x), r(p["merkez"].y), r(p["merkez"].z)],
                   bb=[r(p["bb"].XMin), r(p["bb"].XMax), r(p["bb"].YMin), r(p["bb"].YMax), r(p["bb"].ZMin), r(p["bb"].ZMax)])
              for p in P],
    cakisma=cak,
    baglanti=[[b["ad"], b["tip"], P[b["govde"]]["ad"], [P[e]["ad"] for e in b["eleman"]]] for b in BAG],
    kutle=r(M), agirlik_merkezi=[r(v) for v in cg],
    bolge_ihlal=ihlal,
)
json.dump(oz, open(os.path.join(KLASOR, ETIKET + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("iskelet regresyon ozeti yazildi:", ETIKET, "parca", len(P))

ref = os.path.join(KLASOR, "once.json")
if ETIKET != "once" and os.path.exists(ref):
    a = json.load(open(ref, encoding="utf-8"))
    b = json.load(open(os.path.join(KLASOR, ETIKET + ".json"), encoding="utf-8"))
    satir = []

    def ekle(ad, x, y, fark, ayni):
        satir.append(dict(olcut=ad, once=x, sonra=y, fark=fark, ayni=ayni))

    ekle("parca sayisi", a["parca_sayisi"], b["parca_sayisi"], abs(a["parca_sayisi"] - b["parca_sayisi"]),
         a["parca_sayisi"] == b["parca_sayisi"])
    ad_ayni = [(p["ad"], p["grup"]) for p in a["parcalar"]] == [(p["ad"], p["grup"]) for p in b["parcalar"]]
    ekle("parca adlari, gruplari ve sirasi", len(a["parcalar"]), len(b["parcalar"]), None, ad_ayni)
    if ad_ayni:
        Z = list(zip(a["parcalar"], b["parcalar"]))
        dh = max(abs(p["hacim"] - q["hacim"]) for p, q in Z)
        db = max(abs(u - v) for p, q in Z for u, v in zip(p["bb"], q["bb"]))
        dk = max(abs(p["kutle"] - q["kutle"]) for p, q in Z)
        dm = max(abs(u - v) for p, q in Z for u, v in zip(p["merkez"], q["merkez"]))
        n = len(Z)
        ekle("parca hacmi (en buyuk fark, mm3)", round(sum(p["hacim"] for p in a["parcalar"]), 3),
             round(sum(p["hacim"] for p in b["parcalar"]), 3), dh, dh <= 1e-6)
        ekle("sinir kutusu (en buyuk fark, mm)", "%d x 6 deger" % n, "%d x 6 deger" % n, db, db <= 1e-6)
        ekle("parca kutlesi (en buyuk fark, g)", round(a["kutle"], 3), round(b["kutle"], 3), dk, dk <= 1e-6)
        ekle("parca agirlik merkezi (en buyuk fark, mm)", "%d x 3" % n, "%d x 3" % n, dm, dm <= 1e-6)
        kv = [(p["kati"], p["gecerli"]) for p in a["parcalar"]] == [(p["kati"], p["gecerli"]) for p in b["parcalar"]]
        ekle("kati sayisi + isValid", "hepsi 1 / gecerli" if all(p["kati"] == 1 and p["gecerli"] for p in a["parcalar"]) else "farkli",
             "hepsi 1 / gecerli" if all(p["kati"] == 1 and p["gecerli"] for p in b["parcalar"]) else "farkli", None, kv)
    dcg = max(abs(u - v) for u, v in zip(a["agirlik_merkezi"], b["agirlik_merkezi"]))
    ekle("toplam agirlik merkezi (mm)", a["agirlik_merkezi"], b["agirlik_merkezi"], dcg, dcg <= 1e-6)
    ekle("parca ici cakisma", len(a["cakisma"]), len(b["cakisma"]), None, a["cakisma"] == b["cakisma"])
    ekle("baglantilar (govde + elemanlar)", len(a["baglanti"]), len(b["baglanti"]), None, a["baglanti"] == b["baglanti"])
    ekle("ayrilmis bolge ihlali", len(a["bolge_ihlal"]), len(b["bolge_ihlal"]), None, not a["bolge_ihlal"] and not b["bolge_ihlal"])
    sonuc = dict(hepsi_ayni=all(s["ayni"] for s in satir), satirlar=satir,
                 not_="bolge ihlali: iki durumda da iskelet ayrilmis bolgelere girmiyor (bolge listesi kabuk modulunde degisti)")
    json.dump(sonuc, open(os.path.join(KLASOR, "fark.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for s in satir:
        print("%-42s %-22s %-22s %-10s %s" % (s["olcut"], str(s["once"])[:22], str(s["sonra"])[:22],
                                             "-" if s["fark"] is None else "%.3g" % s["fark"], "AYNI" if s["ayni"] else "FARKLI"))
    print("SONUC:", "BIREBIR AYNI" if sonuc["hepsi_ayni"] else "FARK VAR")
