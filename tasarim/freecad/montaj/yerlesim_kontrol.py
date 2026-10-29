# Ana montajin KISA yerlesim kontrolu (Y2a, 1,65 m; 29 Ekim 2026). Tam tarama DEGIL (o Y4'te carpisma.py ile): modulleri
# moduller.py ile global koordinata koyar ve uc hizli kontrol yapar:
#   (1) ev pozu S2 = 5 (yazilim alt siniri; S2 0 aralik disi): tum modul ciftleri arasinda cakisma (> TOL mm3)
#   (2) kol kaba taramasi: sag kol (omuz Gobek + Kol, dirsek UstKol + OnKol + El) S1 x S2 x dirsek kaba izgarasinda; sabit moduller
#       (iskelet, kabuk, taban, kafa ev pozu, sag omuz govdesi) karsisinda. Sol kol X aynasi (geometri aynali, ayni sonuc beklenir).
#   (3) kafa supurmesi: kafa Boyun + Bas pan x tilt izgarasinda; iskelet, kabuk, iki omuz ve iki kol (ev pozu S2 5) karsisinda + en kucuk bosluk.
# Calistir: FC_SCRIPT=<bu dosya> freecadcmd run_fc.py  -> yerlesim-kontrol.json
import os, sys, json, time, itertools
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import moduller as MD
from moduller import V, A

t0 = time.time()
TOL = 0.5          # mm3 (modul kontrolleriyle ayni)
YANA_MIN = A.OMUZ["yana_aralik"][0]
EV = dict(one_arka=0.0, yana=YANA_MIN, dirsek=0.0, bilek=0.0, pan=0.0, tilt=0.0)


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))
    sys.stdout.flush()


MOD = {}
for ad in MD.SIRA:
    d = MD.yukle(ad)
    d["P"] = []
    for p in d["parcalar"]:
        if p["haric"] or p["tur"] == "Referans" or p["grup"] == "Referans":
            continue
        g = MD.global_sekil(p["shape"], ad)
        d["P"].append(dict(ad=p["ad"], grup=p["grup"], g=g))
    MOD[ad] = d
    log("modul", ad, len(d["P"]))


def yer(ad, grup, poz):
    d = MOD[ad]
    if d["beklenen"] is None:
        return None
    pl = d["beklenen"](poz, grup)
    if pl.isIdentity():
        return None
    return MD.global_poz(ad, pl)


def yerlesik(ad, poz, gruplar=None):
    """(ad, parca adi, sekil, bb) listesi; poz modulun gruplarina uygulanir."""
    out = []
    cache = {}
    for p in MOD[ad]["P"]:
        if gruplar is not None and p["grup"] not in gruplar:
            continue
        if p["grup"] not in cache:
            cache[p["grup"]] = yer(ad, p["grup"], poz)
        pl = cache[p["grup"]]
        s = p["g"]
        if pl is not None:
            s = s.copy()
            s.transformShape(pl.toMatrix(), True)
        out.append((ad, p["ad"], s, s.BoundBox))
    return out


def kes(a, b):
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def tara(A_, B_, bosluk=False, esik=15.0):
    """A_ x B_ cakisma listesi (+ istenirse en kucuk bosluk, bb esik mm icinde)."""
    hit, en, n = [], (1e9, None, None), 0
    for (ma, pa, sa, ba) in A_:
        bb = App.BoundBox(ba)
        if bosluk:
            bb.enlarge(esik)
        for (mb, pb, sb, bbb) in B_:
            if not bb.intersect(bbb):
                continue
            if ba.intersect(bbb):
                n += 1
                v = kes(sa, sb)
                if v > TOL or v < 0:
                    hit.append(("%s: %s" % (ma, pa), "%s: %s" % (mb, pb), round(v, 2)))
                    continue
            if bosluk:
                d_ = sa.distToShape(sb)[0]
                if d_ < en[0]:
                    en = (d_, "%s: %s" % (ma, pa), "%s: %s" % (mb, pb))
    return hit, (round(en[0], 2), en[1], en[2]) if en[1] else None, n


out = dict(not_="kisa yerlesim kontrolu (Y2a); tam tarama Y4 (carpisma.py)", tol_mm3=TOL, ev_pozu=EV)

# ---------------------------------------------------------------- (1) ev pozu S2 = 5: modul ciftleri
EVP = {ad: yerlesik(ad, EV) for ad in MD.SIRA}
ev = {}
for a_, b_ in itertools.combinations(MD.SIRA, 2):
    hit, _, n = tara(EVP[a_], EVP[b_])
    ev["%s x %s" % (a_, b_)] = dict(cift=n, cakisma=hit)
    if hit:
        log("EV", a_, b_, len(hit), hit[:4])
out["ev"] = ev
out["ev_cakisma_toplam"] = sum(len(v["cakisma"]) for v in ev.values())
log("(1) ev pozu S2 %g: cakisma %d" % (YANA_MIN, out["ev_cakisma_toplam"]))

# ---------------------------------------------------------------- (2) kol kaba taramasi (sag kol)
S1 = (-45.0, 0.0, 45.0, 90.0, 135.0)
S2 = (YANA_MIN, 45.0, 90.0, 120.0)
DIRSEK = (0.0, 105.0)
KS = A.KOL_KABLO["s1"]["s2_s1_kosul"]          # S1 >= 120 iken S2 <= 117 (yazilim bagimli siniri)
SABIT_KOL = EVP["iskelet"] + EVP["kabuk"] + EVP["taban"] + EVP["kafa"] + yerlesik("omuz_sag", EV, ("Govde",))
kol = []
for s1, s2, dr in itertools.product(S1, S2, DIRSEK):
    if s1 >= KS["s1_min"] and s2 > KS["s2_max"]:
        s2 = KS["s2_max"]
    poz = dict(EV, one_arka=s1, yana=s2, dirsek=dr)
    hareket = yerlesik("omuz_sag", poz, ("Gobek", "Kol")) + yerlesik("dirsek_sag", poz)
    hit, _, n = tara(hareket, SABIT_KOL)
    kol.append(dict(poz=[s1, s2, dr, 0.0], cift=n, cakisma=hit))
    if hit:
        log("KOL", (s1, s2, dr), len(hit), hit[:3])
out["kol_kaba"] = dict(izgara=dict(s1=S1, s2=S2, dirsek=DIRSEK, bilek=0.0, kosul="S1 >= %g iken S2 <= %g" % (KS["s1_min"], KS["s2_max"])),
                       pozlar=kol, cakisan_poz=sum(1 for k in kol if k["cakisma"]))
log("(2) kol kaba: %d poz, cakisan %d" % (len(kol), out["kol_kaba"]["cakisan_poz"]))

# ---------------------------------------------------------------- (3) kafa supurmesi
PAN = (-90.0, -45.0, 0.0, 45.0, 90.0)
TILT = (A.KAFA["tilt_aralik"][0], 0.0, A.KAFA["tilt_aralik"][1])
SABIT_KAFA = EVP["iskelet"] + EVP["kabuk"] + EVP["omuz_sag"] + EVP["omuz_sol"] + EVP["dirsek_sag"] + EVP["dirsek_sol"]
kafa = []
for pn, tl in itertools.product(PAN, TILT):
    poz = dict(EV, pan=pn, tilt=tl)
    hareket = yerlesik("kafa", poz, ("Boyun", "Bas"))
    hit, en, n = tara(hareket, SABIT_KAFA, bosluk=True)
    kafa.append(dict(pan=pn, tilt=tl, cift=n, cakisma=hit, en_kucuk_bosluk=en))
    log("KAFA", (pn, tl), len(hit), en)
out["kafa_supurme"] = dict(pan=PAN, tilt=TILT, pozlar=kafa, cakisan_poz=sum(1 for k in kafa if k["cakisma"]),
                           en_kucuk=min((k["en_kucuk_bosluk"] for k in kafa if k["en_kucuk_bosluk"]), default=None))
log("(3) kafa supurme: %d poz, cakisan %d, en kucuk %s" % (len(kafa), out["kafa_supurme"]["cakisan_poz"], out["kafa_supurme"]["en_kucuk"]))

out["sure_s"] = round(time.time() - t0, 1)
json.dump(out, open(os.path.join(HERE, "yerlesim-kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("bitti")
