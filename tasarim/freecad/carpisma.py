# Moduller arasi carpisma kontrolu (FreeCAD 1.1). arayuz.MODULLER yerlesimiyle modulleri global koordinata
# koyar, (1) ev pozunda tum modul ciftlerini, (2) her hareketli modulun tum tarama pozlarinda hareketli
# parcalarini diger modullere karsi, (3) henuz cizilmemis modullerin ayrilmis bolgelerini (arayuz.BOLGELER)
# tarar, (4) kol zincirini (omuz S1 x S2 x dirsek x bilek; dirsek modulu omuzun Kol grubuna bagli) iskelet, kabuk,
# ayrilmis bolgeler ve kendi omuzunun govde/gobegine karsi, iki kolu da birbirine karsi tarar.
# Yeni modul eklemek: MODUL_YUKLE'ye bir yukleyici ekle (parcalar + hareket + haric listesi).
# Calistir: FC_SCRIPT=<bu dosya> freecadcmd run_fc.py   ->  carpisma-sonuc.json
import os, sys, json, time, math
import FreeCAD as App
import Part
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(HERE, "iskelet"), os.path.join(HERE, "omuz"), os.path.join(HERE, "kabuk"),
           os.path.join(HERE, "dirsek")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import arayuz as A
from ortak_lib import V, box

t0 = time.time()
TOL = 0.5   # mm3 (omuz ve iskelet kontrolleriyle ayni)


# ====================================================================== modul yukleyicileri
# Her yukleyici: dict(parcalar=[dict(ad, grup, shape, kutle, merkez)], hareket=None | dict(pozlar, yer(poz, grup) ->
# App.Placement (yerel), sabit_grup, eklem_araligi(poz) -> bool), haric=[parca adi oneki], haric_neden)
def yukle_iskelet():
    import iskelet_parcalar as I
    return dict(parcalar=[dict(ad=p["ad"], grup="sabit", shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"]) for p in I.P],
                hareket=None, haric=[], haric_neden="")


def yukle_omuz():
    import omuz_parcalar as O
    grup = {"Govde": "sabit", "Gobek": "Gobek", "Kol": "Kol"}

    def yer(poz, g):
        phi, th = poz
        if g == "Gobek":
            return O.Pp(phi)
        if g == "Kol":
            return O.Pp(phi).multiply(O.Pr(th))
        return App.Placement()

    return dict(parcalar=[dict(ad=p["ad"], grup=grup[p["grup"]], shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"])
                          for p in O.P],
                hareket=dict(pozlar=[(phi, th) for phi in O.PHIS for th in O.THS], yer=yer,
                             eklem_araligi=lambda poz: -45 <= poz[0] <= 135 and 0 <= poz[1] <= 120,
                             aciklama="omuz_montaj taramasi: one-arka %d...%d, yana %d...%d (5-10 derece adim)" %
                             (min(O.PHIS), max(O.PHIS), min(O.THS), max(O.THS))),
                haric=["Omuz traversi", "Govde kabugu yan yuzu (referans)"],
                haric_neden="travers iskeletin parcasi (arayuz uyumu ayrica kontrol edilir); kabuk duvari kabuk modulunun yer tutucusu")


def yukle_kabuk():
    import kabuk_parcalar as K
    return dict(parcalar=[dict(ad=p["ad"], grup="sabit", shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"]) for p in K.P],
                hareket=None, haric=[], haric_neden="")


def yukle_dirsek(taraf):
    """Dirsek modulu omuzun Kol grubuna bagli: kendi 'hareket'i yok, kol zinciri taramasinda (bolum 4) omuzla birlikte
    surulur (zincir). Generic taramada hedef olarak kullanilmaz (ev pozunda durmaz, kolla birlikte hareket eder)."""
    def yukle():
        import dirsek_parcalar as DP
        return dict(parcalar=[dict(ad=p["ad"], grup=p["grup"], shape=p["shape"], kutle=p["kutle"], merkez=p["merkez"]) for p in DP.P],
                    hareket=None, zincir=dict(omuz="omuz_" + taraf, taraf=taraf), haric=[], haric_neden="")
    return yukle


MODUL_YUKLE = {"iskelet": yukle_iskelet, "omuz_sag": yukle_omuz, "omuz_sol": yukle_omuz, "kabuk": yukle_kabuk,
               "dirsek_sag": yukle_dirsek("sag"), "dirsek_sol": yukle_dirsek("sol")}
KONTROL = ["iskelet", "omuz_sag", "omuz_sol", "kabuk", "dirsek_sag", "dirsek_sol"]   # sonraki moduller (taban, kafa) buraya eklenir


# ====================================================================== global yerlesim
AYNA = App.Matrix()
AYNA.A11 = -1.0


def global_matris(ad):
    (tx, ty, tz), ayna = A.modul_konum(ad)
    T = App.Matrix()
    T.move(V(tx, ty, tz))
    return T, (AYNA if ayna else App.Matrix())


MODUL = {}
for ad in KONTROL:
    d = MODUL_YUKLE[ad]()
    T, R = global_matris(ad)
    for p in d["parcalar"]:
        s = p["shape"].mirror(V(0, 0, 0), V(1, 0, 0)) if R.A11 < 0 else p["shape"].copy()
        s.transformShape(T, True)
        p["g"] = s
        p["gbb"] = s.optimalBoundingBox()      # B-spline yuzlu buyuk parcalarda BoundBox gevsek; suzgec icin siki kutu
        c = p["merkez"]
        p["gmerkez"] = V(-c.x if R.A11 < 0 else c.x, c.y, c.z) + V(T.A14, T.A24, T.A34)
        p["haric"] = any(p["ad"].startswith(h) for h in d["haric"])
    d["T"], d["R"] = T, R
    MODUL[ad] = d
    print("modul", ad, "parca", len(d["parcalar"]), "haric", sum(p["haric"] for p in d["parcalar"]), "%.1fs" % (time.time() - t0))

# henuz cizilmemis modullerin ayrilmis bolgeleri -> sabit sozde modul
bolge_parca = []
for z in A.bolgeler(haric=KONTROL):
    k = box(*z["kutu"])
    for c in z["bosluk"]:
        k = k.cut(box(*c))
    bolge_parca.append(dict(ad="[%s] %s" % (z["sahip"], z["ad"]), grup="sabit", g=k, gbb=k.BoundBox, haric=False, kutle=0))
MODUL["ayrilmis_bolgeler"] = dict(parcalar=bolge_parca, hareket=None, haric=[], haric_neden="")


def poz_matrisi(ad, poz, g):
    """Global koordinatta bir grubun poz donusumu: T R P R T^-1 (R ayna ise de katı donusum kalir)."""
    d = MODUL[ad]
    Pm = d["hareket"]["yer"](poz, g).toMatrix()
    T, R = d["T"], d["R"]
    return T.multiply(R).multiply(Pm).multiply(R).multiply(T.inverse())


def kesisim(a, b, abb, bbb):
    if not abb.intersect(bbb):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


def aktif(d):
    return [p for p in d["parcalar"] if not p["haric"]]


# ====================================================================== 1) arayuz uyumu: omuzun traversi = iskeletin traversi
uyum = []
isk_tr = next(p for p in MODUL["iskelet"]["parcalar"] if p["ad"] == "Omuz traversi")
for ad in ("omuz_sag", "omuz_sol"):
    o_tr = next(p for p in MODUL[ad]["parcalar"] if p["ad"].startswith("Omuz traversi"))
    ortak = o_tr["g"].common(isk_tr["g"]).Volume
    bbd = max(abs(getattr(o_tr["gbb"], k) - getattr(isk_tr["gbb"], k)) for k in ("XMin", "XMax", "YMin", "YMax", "ZMin", "ZMax"))
    uyum.append(dict(modul=ad, hacim_omuz=round(o_tr["g"].Volume, 3), hacim_iskelet=round(isk_tr["g"].Volume, 3),
                     ortak=round(ortak, 3), sinir_kutusu_fark=round(bbd, 6),
                     ayni=abs(ortak - isk_tr["g"].Volume) < 1e-3 and bbd < 1e-6))
print("arayuz uyumu:", [(u["modul"], u["ayni"]) for u in uyum])

# ====================================================================== 2) ev pozunda modul ciftleri
adlar = list(MODUL)
statik = []
n_statik = 0
for i in range(len(adlar)):
    for j in range(i + 1, len(adlar)):
        for a in aktif(MODUL[adlar[i]]):
            for b in aktif(MODUL[adlar[j]]):
                if a["gbb"].intersect(b["gbb"]):
                    n_statik += 1
                v = kesisim(a["g"], b["g"], a["gbb"], b["gbb"])
                if v > TOL or v < 0:
                    statik.append(dict(a=adlar[i], pa=a["ad"], b=adlar[j], pb=b["ad"], hacim=round(v, 2)))
print("ev pozu: %d cakisma (%d sinir kutusu kesisen cift)" % (len(statik), n_statik), "%.1fs" % (time.time() - t0))

# ====================================================================== 3) hareket taramasi
zarf = {}
for ad in adlar:
    d = MODUL[ad]
    if not d["hareket"]:
        continue
    gruplar = sorted(set(p["grup"] for p in aktif(d) if p["grup"] != "sabit"))
    bb = None
    for poz in d["hareket"]["pozlar"]:
        for g in gruplar:
            M = poz_matrisi(ad, poz, g)
            for p in aktif(d):
                if p["grup"] != g:
                    continue
                s = p["g"].copy()
                s.transformShape(M)
                if bb is None:
                    bb = App.BoundBox(s.BoundBox)
                else:
                    bb.add(s.BoundBox)
    zarf[ad] = bb
    print("zarf", ad, "x %.0f...%.0f y %.0f...%.0f z %.0f...%.0f" % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))

# uzaklik icin yuz listesi: sabit hedef parcanin hareket zarflarina (30 mm payli) yakin yuzleri ve sinir kutulari. Her
# pozda yalniz hareketli parcanin 30 mm kutusuna giren yuzlere distToShape: cakismayan iki sekil arasindaki en kucuk uzaklik
# sinirlarda olculdugu icin sonuc ayni, buyuk (B-spline yuzlu) kabuk parcalarinda tarama cok hizlanir.
_zarf30 = []
for _b in zarf.values():
    _z = App.BoundBox(_b)
    _z.enlarge(30)
    _zarf30.append(_z)
for ad in adlar:
    if MODUL[ad]["hareket"] or MODUL[ad].get("zincir"):
        continue
    for q in aktif(MODUL[ad]):
        q["yuz"] = [] if not any(z.intersect(q["gbb"]) for z in _zarf30) else             [(f, f.BoundBox) for f in q["g"].Faces if any(z.intersect(f.BoundBox) for z in _zarf30)]
# kabuk (buyuk sabit kabuk) icin en kucuk bosluk yalniz eklem araligindaki pozlarda olculur; cakisma tum pozlarda
YALNIZ_ARALIKTA = ("kabuk",)

tarama = {}
for ad in adlar:
    d = MODUL[ad]
    if not d["hareket"]:
        continue
    hedef = []          # diger modullerin ev pozu parcalari (hareketli diger modul: zarflar kesisiyorsa ortak tarama)
    ortak_gerekli = []
    for bd in adlar:
        if bd == ad:
            continue
        if MODUL[bd]["hareket"]:
            if zarf[ad].intersect(zarf[bd]):
                ortak_gerekli.append(bd)
            continue     # zarflar ayriksa hicbir pozda carpisamazlar
        if MODUL[bd].get("zincir"):
            continue     # dirsek: kolla birlikte hareket eder, kol zinciri taramasinda (bolum 4)
        hedef += [(bd, p) for p in aktif(MODUL[bd])]
    hareketli = [p for p in aktif(d) if p["grup"] != "sabit"]
    cak = {}
    n_test = 0
    yakin = (1e9, None)     # en kucuk bosluk: 30 mm icindeki adaylar icin distToShape
    ea = d["hareket"]["eklem_araligi"]
    mod_yakin = {}          # hedef modul -> eklem araligindaki en kucuk bosluk
    mod_cak = {}            # hedef modul -> cakisan pozlar
    for poz in d["hareket"]["pozlar"]:
        tasinmis = []
        for p in hareketli:
            s = p["g"].copy()
            s.transformShape(poz_matrisi(ad, poz, p["grup"]))
            tasinmis.append((p, s, s.BoundBox))
        hits = []
        for p, s, sbb in tasinmis:
            bb30 = App.BoundBox(sbb)
            bb30.enlarge(30)
            for bd, q in hedef:
                if not bb30.intersect(q["gbb"]):
                    continue
                v = 0.0
                if sbb.intersect(q["gbb"]):
                    n_test += 1
                    v = kesisim(s, q["g"], sbb, q["gbb"])
                    if v > TOL or v < 0:
                        hits.append((p["ad"], bd, q["ad"], round(v, 1)))
                        mod_cak.setdefault(bd, set()).add(poz)
                if bd in YALNIZ_ARALIKTA and not ea(poz) and not (v > TOL or v < 0):
                    continue
                yz = [f for f, fb in q["yuz"] if bb30.intersect(fb)]
                if yz or v > TOL or v < 0:
                    dd = 0.0 if (v > TOL or v < 0) else s.distToShape(Part.Compound(yz) if len(yz) > 1 else yz[0])[0]
                    if dd < yakin[0]:
                        yakin = (dd, (poz, p["ad"], bd, q["ad"]))
                    if ea(poz) and dd < mod_yakin.get(bd, (1e9,))[0]:
                        mod_yakin[bd] = (dd, (poz, p["ad"], q["ad"]))
        # hareketli diger moduller (zarflari kesisiyorsa): onlarin tum pozlariyla
        for bd in ortak_gerekli:
            for poz2 in MODUL[bd]["hareket"]["pozlar"]:
                for q in [x for x in aktif(MODUL[bd]) if x["grup"] != "sabit"]:
                    s2 = q["g"].copy()
                    s2.transformShape(poz_matrisi(bd, poz2, q["grup"]))
                    for p, s, sbb in tasinmis:
                        v = kesisim(s, s2, sbb, s2.BoundBox)
                        if v > TOL or v < 0:
                            hits.append((p["ad"], bd + "@%s" % (poz2,), q["ad"], round(v, 1)))
        if hits:
            cak[poz] = hits
        n_poz_bitti = d["hareket"]["pozlar"].index(poz) + 1
        if n_poz_bitti % 125 == 0:
            print("  %s %d/%d poz, %.0fs" % (ad, n_poz_bitti, len(d["hareket"]["pozlar"]), time.time() - t0), flush=True)
    tarama[ad] = dict(poz_sayisi=len(d["hareket"]["pozlar"]), cakisan_poz=len(cak),
                      eklem_araliginda_cakisan=sum(1 for k in cak if ea(k)), kesisim_testi=n_test,
                      ortak_tarama=ortak_gerekli, aciklama=d["hareket"]["aciklama"],
                      en_kucuk_bosluk_mm=round(yakin[0], 2), en_yakin=yakin[1],
                      cakismalar={"%s" % (k,): v for k, v in list(cak.items())[:50]},
                      modul_bosluk_eklem_araliginda={k: [round(v[0], 2), v[1]] for k, v in mod_yakin.items()},
                      modul_cakisan_poz={k: sorted([list(x) for x in v]) for k, v in mod_cak.items()},
                      bosluk_notu="kabuk icin en kucuk bosluk yalniz eklem araligindaki pozlarda olculdu (cakisma tum pozlarda)")
    print("tarama", ad, "%d poz, %d cakisan (eklem araliginda %d), %d kesisim testi, en kucuk bosluk %.1f mm %s" %
          (len(d["hareket"]["pozlar"]), len(cak), tarama[ad]["eklem_araliginda_cakisan"], n_test, yakin[0], yakin[1]),
          "%.1fs" % (time.time() - t0))

# ====================================================================== 4) kol zinciri taramasi (omuz S1 x S2 x dirsek x bilek)
# Dirsek modulu omuzun Kol grubuna bagli: UstKol = Pp(phi) Pr(th), OnKol = UstKol Pe(dirsek), El = OnKol Pb(bilek)
# (dirsek_parcalar.grup_yer; Pp/Pr omuz_parcalar ile ayni). Hareketli: dirsek parcalari (omuz parcalari 3. bolumde tarandi).
# Hedef: iskelet, kabuk, ayrilmis bolgeler, iki omuzun govdesi (sabit) ve kendi omuzunun gobegi (Pp(phi)). Omuzun Kol grubu
# dirsek ust grubuna sabit; on kol/el ile Kol grubu arasindaki bagil hareket omuz pozundan bagimsiz ve dirsek_montaj.py'de
# tarandi. Yontem: (a) sinir kutusu on elemesi: hareketli parcanin ev pozu kutusunun 8 kosesi poz matrisiyle tasinir
# (tutucu kutu), hedef kutularina bosluk numpy ile hesaplanir; LIM'den uzak ciftler hic olculmez. (b) tutucu boslugu YAKIN
# altindaki her aday tam olculur (distToShape; buyuk kabuk parcalarinda yalniz yakin yuzlere; temas/gomulme suphesinde
# common hacmi). (c) hedef basina en kucuk bosluk: adaylar tutucu bosluga gore siralanir, dal-sinirla (kutu boslugu bulunan
# en kucuk boslugu gecince durur) tam olculur. (d) kaba izgarada cakisan ya da INCE_ESIK altinda bosluk birakan alt
# pozlarin cevresi ince adimla (omuz 5 derece, dirsek 5, bilek 15) yeniden taranir. Alt poz: UstKol (phi, th),
# OnKol (phi, th, dirsek), El (phi, th, dirsek, bilek); tam poz bulgusu ucunun birlesimi.
import itertools
import dirsek_parcalar as DP
import omuz_parcalar as OP

KOL_ARALIK = ((-45.0, 135.0), (0.0, 120.0), tuple(DP.D["aralik"]), tuple(DP.D["bilek_aralik"]))   # phi, th, dirsek, bilek
KABA = (list(range(-45, 136, 15)), list(range(0, 121, 15)), [0, 30, 60, 90, 105], [-90, 0, 90])
DISI_AL, DISI_BE = [0, 60, 105], [-90, 0, 90]       # aralik disi halka: omuz one-arka -60 / 150, yana -10
YAKIN = 5.0          # mm: tutucu kutu boslugu bunun altindaki her aday tam olculur
INCE_ESIK = 5.0      # mm: bunun altinda bosluk (ya da cakisma) olan alt pozun cevresi ince taranir
LIM = 150.0          # mm: kutu on elemesi (bunun otesindeki ciftlerin boslugu "> LIM" sayilir)
GOMULU = 3.0         # mm: bu mesafenin altinda ve hedef kutusu icindeyse gomulme kontrolu (common)
GRUP_UZ = {"UstKol": 2, "OnKol": 3, "El": 4}
ESIK_YUZ = 40        # bundan cok yuzlu hedefte yalniz yakin yuzlerle mesafe


def kol_araliginda(sp):
    return all(KOL_ARALIK[k][0] - 1e-9 <= v <= KOL_ARALIK[k][1] + 1e-9 for k, v in enumerate(sp))


def np_m(M):
    return np.array([[M.A11, M.A12, M.A13, M.A14], [M.A21, M.A22, M.A23, M.A24], [M.A31, M.A32, M.A33, M.A34]])


def bb6(b):
    return np.array([b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax])


def kose8(b):
    return np.array([[x, y, z, 1.0] for x in (b.XMin, b.XMax) for y in (b.YMin, b.YMax) for z in (b.ZMin, b.ZMax)])


def kutu_tasi(K8, Mn):
    q = K8 @ Mn.T
    return np.concatenate([q.min(0), q.max(0)])


def bosluk_np(b, B):
    d = np.maximum(0.0, np.maximum(B[:, :3] - b[3:], b[:3] - B[:, 3:]))
    return np.sqrt((d * d).sum(1))


def kol_matrisi(ad, g, sp):
    """Global poz matrisi: T R P R T^-1. ad = dirsek_* ya da omuz_*; sp = (phi, th, dirsek, bilek) ya da onun basi."""
    d = MODUL[ad]
    phi, th, al, be = (list(sp) + [0.0, 0.0, 0.0, 0.0])[:4]
    if g in GRUP_UZ:
        Pm = DP.grup_yer(g, phi, th, al, be).toMatrix()
    elif g == "Gobek":
        Pm = OP.Pp(phi).toMatrix()
    elif g == "Kol":
        Pm = OP.Pp(phi).multiply(OP.Pr(th)).toMatrix()
    else:
        Pm = App.Matrix()
    T, R = d["T"], d["R"]
    return T.multiply(R).multiply(Pm).multiply(R).multiply(T.inverse())


def yuz_hazirla(q):
    if "fbb" not in q:
        fs = q["g"].Faces
        q["faces"] = fs
        q["fbb"] = np.array([bb6(f.BoundBox) for f in fs]) if len(fs) > ESIK_YUZ else None


def tam_olc(s, q, B):
    """Hareketli sekil s ile hedef q arasi: (mesafe, cakisma hacmi) ya da B'den uzaksa None."""
    sb = bb6(s.BoundBox)
    if bosluk_np(sb, q["bb"][None, :])[0] >= B:
        return None
    yuz_hazirla(q)
    if q["fbb"] is None:
        hedef_s = q["g"]
    else:
        sec = np.nonzero(bosluk_np(sb, q["fbb"]) < B)[0]
        if len(sec) == 0:
            return None
        hedef_s = q["faces"][sec[0]] if len(sec) == 1 else Part.Compound([q["faces"][i] for i in sec])
    d = s.distToShape(hedef_s)[0]
    v = 0.0
    ic = all(sb[k] >= q["bb"][k] for k in range(3)) and all(sb[k + 3] <= q["bb"][k + 3] for k in range(3))
    if d < 1e-6 or (d < GOMULU and ic and q["g"].Solids):
        v = kesisim(s, q["g"], s.BoundBox, q["gbbF"])
        if v > TOL or v < 0:
            d = 0.0
    return d, v


def kol_tara(taraf):
    om, dr = "omuz_" + taraf, "dirsek_" + taraf
    ts = time.time()
    # --- hedefler: sabit (iskelet, kabuk, bolgeler, iki omuzun govdesi) + kendi omuzunun gobegi (phi ile)
    sabit = []
    for ad in adlar:
        dd = MODUL[ad]
        if dd.get("zincir"):
            continue
        if dd["hareket"]:
            if not ad.startswith("omuz_"):
                continue
            sabit += [dict(mod="%s govde" % ad, ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"])) for q in aktif(dd) if q["grup"] == "sabit"]
        else:
            sabit += [dict(mod=ad, ad=q["ad"], g=q["g"], gbbF=q["gbb"], bb=bb6(q["gbb"])) for q in aktif(dd)]
    SB = np.array([q["bb"] for q in sabit])
    gobek_p = [q for q in aktif(MODUL[om]) if q["grup"] == "Gobek"]
    gobek_cache = {}

    def gobek(phi):
        if phi not in gobek_cache:
            M = kol_matrisi(om, "Gobek", (phi,))
            L = []
            for q in gobek_p:
                s = q["g"].copy()
                s.transformShape(M)
                L.append(dict(mod="%s gobek" % om, ad=q["ad"], g=s, gbbF=s.BoundBox, bb=bb6(s.BoundBox)))
            gobek_cache[phi] = (L, np.array([x["bb"] for x in L]))
        return gobek_cache[phi]

    har = [p for p in aktif(MODUL[dr])]
    for p in har:
        p["K8"] = kose8(p["gbb"])
    mcache = {}

    def M_al(g, sp):
        k = (g, sp)
        if k not in mcache:
            mcache[k] = kol_matrisi(dr, g, sp)
        return mcache[k]

    def hedef(hk, sp):
        return sabit[hk[1]] if hk[0] == "s" else gobek(sp[0])[0][hk[1]]

    def tasi(pi, g, sp):
        s = har[pi]["g"].copy()
        s.transformShape(M_al(g, sp))
        return s

    aday = []           # (tutucu bosluk, g, sp, parca indeksi, hedef anahtari)
    islenen = set()

    def aday_topla(altpozlar):
        n0 = len(aday)
        for g, sp in altpozlar:
            if (g, sp) in islenen:
                continue
            islenen.add((g, sp))
            Mn = np_m(M_al(g, sp))
            GL, GB = gobek(sp[0])
            for pi, p in enumerate(har):
                if p["grup"] != g:
                    continue
                cb = kutu_tasi(p["K8"], Mn)
                gs = bosluk_np(cb, SB)
                for j in np.nonzero(gs < LIM)[0]:
                    aday.append((float(gs[j]), g, sp, pi, ("s", int(j))))
                gg = bosluk_np(cb, GB)
                for j in np.nonzero(gg < LIM)[0]:
                    aday.append((float(gg[j]), g, sp, pi, ("g", int(j))))
        return n0

    olcum = {}          # (g, sp, pi, hk) -> (d, v)

    def olc(c, B):
        k = (c[1], c[2], c[3], c[4])
        if k in olcum:
            return olcum[k]
        r = tam_olc(tasi(c[3], c[1], c[2]), hedef(c[4], c[2]), B)
        if r is not None:
            olcum[k] = r
        return r

    def mod_ad(hk):
        return sabit[hk[1]]["mod"] if hk[0] == "s" else "%s gobek" % om

    en_iyi = {}

    def degerlendir(n0):
        yeni = sorted(aday[n0:], key=lambda c: c[0])
        n_tam = 0
        for c in yeni:                          # (b) YAKIN altindakiler hepsi
            if c[0] >= YAKIN:
                break
            r = olc(c, YAKIN)
            n_tam += 1
            if r is not None and r[0] < en_iyi.get(mod_ad(c[4]), (1e9,))[0]:
                en_iyi[mod_ad(c[4])] = (r[0], c)
        for c in yeni:                          # (c) dal-sinir: hedef modul basina en kucuk bosluk
            m = mod_ad(c[4])
            B = en_iyi.get(m, (LIM,))[0]
            if c[0] >= B:
                continue
            r = olc(c, B)
            n_tam += 1
            if n_tam % 500 == 0:
                print("    %s: %d tam olcum, %.0fs" % (taraf, n_tam, time.time() - ts), flush=True)
            if r is not None and r[0] < B:
                en_iyi[m] = (r[0], c)
        return n_tam

    # --- kaba izgara + aralik disi halka
    kaba = [(phi, th, al, be) for phi in KABA[0] for th in KABA[1] for al in KABA[2] for be in KABA[3]]
    disi = [(phi, th, al, be) for phi in (-60, 150) for th in KABA[1] for al in DISI_AL for be in DISI_BE] + \
           [(phi, -10, al, be) for phi in KABA[0] for al in DISI_AL for be in DISI_BE]

    def alt(poz):
        return [(g, tuple(float(x) for x in poz[:n])) for g, n in GRUP_UZ.items()]

    altlar = sorted(set(a for poz in kaba + disi for a in alt(poz)))
    n0 = aday_topla(altlar)
    n_tam = degerlendir(n0)
    print("kol %s: kaba %d + disi %d tam poz, %d alt poz, %d aday, %d tam olcum %.0fs" % (
        taraf, len(kaba), len(disi), len(altlar), len(aday), n_tam, time.time() - ts), flush=True)

    # --- (d) ince adim: cakisan ya da INCE_ESIK altinda kalan alt pozlarin cevresi
    def isaretli():
        return sorted(set((k[0], k[1]) for k, r in olcum.items() if r[0] < INCE_ESIK or r[1] > TOL or r[1] < 0))

    # yalniz eklem araligindaki isaretli alt pozlar incelenir (aralik disi halka yalniz ornek); ince komsuluk aralik icinde kalir
    isa = [x for x in isaretli() if kol_araliginda(x[1])]
    ADIM_I = ((-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-10, -5, 0, 5, 10), (-15, 0, 15))
    ince = set()
    for g, sp in isa:
        rng = [[sp[k] + dd for dd in ADIM_I[k]] for k in range(len(sp))]
        for q in itertools.product(*rng):
            q = tuple(float(x) for x in q)
            if kol_araliginda(q):
                ince.add((g, q))
    print("kol %s: isaretli alt poz %d (%s), ince aday alt poz %d" % (
        taraf, len(isa), {gg: sum(1 for x in isa if x[0] == gg) for gg in GRUP_UZ}, len(ince)), flush=True)
    ince = sorted(ince - islenen)
    n0 = aday_topla(ince)
    n_tam2 = degerlendir(n0)
    print("kol %s: ince %d alt poz, %d aday, %d tam olcum %.0fs" % (taraf, len(ince), len(aday) - n0, n_tam2, time.time() - ts), flush=True)

    # --- ozet
    def bulgu(k, r):
        g, sp, pi, hk = k
        q = hedef(hk, sp)
        return dict(grup=g, poz=list(sp), parca=har[pi]["ad"], hedef_modul=q["mod"], hedef=q["ad"], bosluk_mm=round(r[0], 2),
                    hacim_mm3=round(r[1], 1), aralikta=kol_araliginda(sp))

    cak = [bulgu(k, r) for k, r in olcum.items() if r[1] > TOL or r[1] < 0]
    yakin_l = sorted([bulgu(k, r) for k, r in olcum.items() if r[0] < YAKIN and not (r[1] > TOL or r[1] < 0)],
                     key=lambda b: b["bosluk_mm"])

    def tam_poz_cak(pozlar):
        cak_alt = set((b["grup"], tuple(b["poz"])) for b in cak)
        return [poz for poz in pozlar if any(a in cak_alt for a in alt(poz))]

    kaba_cak = tam_poz_cak(kaba)
    disi_cak = tam_poz_cak(disi)
    # hedef modul basina en kucuk bosluk (aralik ici / disi ayri)
    mod_min = {}
    cift_min = {}
    for k, r in olcum.items():
        b = bulgu(k, r)
        anah = (b["hedef_modul"], b["aralikta"])
        if r[0] < mod_min.get(anah, (1e9,))[0]:
            mod_min[anah] = (r[0], b)
        if b["aralikta"]:
            anah = (b["hedef_modul"], b["parca"], b["hedef"])
            if r[0] < cift_min.get(anah, (1e9,))[0]:
                cift_min[anah] = (r[0], b)
    moduller = sorted(set(m for m, _ in mod_min))
    sonuc = dict(
        taraf=taraf, omuz=om, dirsek=dr,
        aralik=dict(one_arka=KOL_ARALIK[0], yana=KOL_ARALIK[1], dirsek=KOL_ARALIK[2], bilek=KOL_ARALIK[3]),
        kaba_izgara=dict(one_arka=KABA[0], yana=KABA[1], dirsek=KABA[2], bilek=KABA[3], tam_poz=len(kaba)),
        aralik_disi_halka=dict(aciklama="omuz one-arka -60 ve 150 (yana 0...120) + yana -10 (one-arka -45...135); dirsek %s; bilek %s"
                               % (DISI_AL, DISI_BE), tam_poz=len(disi)),
        alt_poz=dict(kaba=len(altlar), ince=len(ince)), aday=len(aday), tam_olcum=len(olcum),
        cakisan_tam_poz_aralikta=len(kaba_cak), cakisan_tam_poz_aralik_disi=len(disi_cak),
        cakisan_alt_poz_aralikta=len(set((b["grup"], tuple(b["poz"])) for b in cak if b["aralikta"])),
        cakisan_alt_poz_aralik_disi=len(set((b["grup"], tuple(b["poz"])) for b in cak if not b["aralikta"])),
        cakismalar_aralikta=sorted([b for b in cak if b["aralikta"]], key=lambda b: (b["grup"], b["poz"]))[:200],
        cakismalar_aralik_disi=sorted([b for b in cak if not b["aralikta"]], key=lambda b: (b["grup"], b["poz"]))[:200],
        en_kucuk_bosluk_aralikta={m: mod_min[(m, True)][1] for m in moduller if (m, True) in mod_min},
        en_kucuk_bosluk_aralik_disi={m: mod_min[(m, False)][1] for m in moduller if (m, False) in mod_min},
        en_kucuk_ciftler_aralikta={m: [v[1] for v in sorted([v for kk, v in cift_min.items() if kk[0] == m], key=lambda v: v[0])[:6]]
                                   for m in moduller},
        yakin_aralikta=[b for b in yakin_l if b["aralikta"]][:60], yakin_aralikta_sayi=sum(1 for b in yakin_l if b["aralikta"]),
        bosluk_notu="olculmeyen ciftlerin boslugu >= %d mm (sinir kutusu); YAKIN = %.0f mm altindaki her aday tam olculdu" % (LIM, YAKIN),
        sure_s=round(time.time() - ts, 1))
    for m in moduller:
        if (m, True) in mod_min:
            b = mod_min[(m, True)][1]
            print("  %s -> %-22s en kucuk bosluk %.2f mm %s %s / %s" % (taraf, m, b["bosluk_mm"], b["poz"], b["parca"], b["hedef"]))
    print("kol %s: aralikta cakisan tam poz %d / %d, aralik disi %d / %d, %.0fs" % (
        taraf, len(kaba_cak), len(kaba), len(disi_cak), len(disi), time.time() - ts), flush=True)
    return sonuc


kol_tarama = {}
for _t in ("sag", "sol"):
    if "dirsek_" + _t in MODUL:
        kol_tarama[_t] = kol_tara(_t)


# ---------------------------------------------------------------------- kol <-> kol (iki kol ayni anda)
def kol_parcalari(taraf):
    om, dr = "omuz_" + taraf, "dirsek_" + taraf
    L = [(om, p) for p in aktif(MODUL[om]) if p["grup"] in ("Gobek", "Kol")] + [(dr, p) for p in aktif(MODUL[dr])]
    for ad, p in L:
        if "K8" not in p:
            p["K8"] = kose8(p["gbb"])
    return L


def kol_kol():
    ts = time.time()
    KS, KL = kol_parcalari("sag"), kol_parcalari("sol")
    ciftler = []
    for phi in (-45, 0, 45, 90, 135):                     # simetrik: iki kol ayni poz (aynali hareket)
        for th in (0, 60, 120):
            for al in (0, 60, 105):
                for be in (-90, 90):
                    ciftler.append(("simetrik", (phi, th, al, be), (phi, th, al, be)))
    for (a, b) in (((135, 0), (-45, 0)), ((-45, 0), (135, 0)), ((90, 0), (0, 0)), ((135, 120), (-45, 0)), ((0, 120), (135, 0)),
                   ((90, 30), (-45, 60)), ((45, 0), (-45, 0)), ((120, 0), (-30, 0))):   # zit pozlar
        for al in (0, 105):
            for be in (-90, 90):
                ciftler.append(("zit", (a[0], a[1], al, be), (b[0], b[1], 105 - al, -be)))
    for th in (0, 15, 30):                               # iki kol birlikte one uzanir (omuz one 90)
        for al in (0, 30, 60, 90, 105):
            for be in (-90, 0, 90):
                ciftler.append(("birlikte one", (90, th, al, be), (90, th, al, -be)))
                ciftler.append(("birlikte one (bilek ayni)", (90, th, al, be), (90, th, al, be)))
    for phi in (60, 75, 105, 120, 135):
        for al in (0, 60, 105):
            ciftler.append(("birlikte one", (phi, 0, al, 0), (phi, 0, al, 0)))

    def kutular(KX, poz):
        cb = []
        for ad, p in KX:
            g = p["grup"]
            n = GRUP_UZ.get(g, 2 if g == "Kol" else 1)
            M = kol_matrisi(ad, g, tuple(float(x) for x in poz[:n]))
            cb.append((M, kutu_tasi(p["K8"], np_m(M))))
        return cb

    sonuc = []
    for tip, pr, pl in ciftler:
        cr, cl = kutular(KS, pr), kutular(KL, pl)
        BR = np.array([c[1] for c in cr])
        BL = np.array([c[1] for c in cl])
        G = np.sqrt((np.maximum(0.0, np.maximum(BL[None, :, :3] - BR[:, None, 3:], BR[:, None, :3] - BL[None, :, 3:])) ** 2).sum(2))
        v_cak = []

        def dal_sinir(Gm):
            en = (1e9, None)
            sira = np.dstack(np.unravel_index(np.argsort(Gm, axis=None), Gm.shape))[0]
            for i, j in sira:
                if Gm[i, j] >= en[0]:
                    break
                a = KS[i][1]["g"].copy()
                a.transformShape(cr[i][0])
                b = KL[j][1]["g"].copy()
                b.transformShape(cl[j][0])
                d = a.distToShape(b)[0]
                if d < 1e-6:
                    v = kesisim(a, b, a.BoundBox, b.BoundBox)
                    if (v > TOL or v < 0) and (KS[i][1]["ad"], KL[j][1]["ad"]) not in [x[:2] for x in v_cak]:
                        v_cak.append((KS[i][1]["ad"], KL[j][1]["ad"], round(v, 1)))
                if d < en[0]:
                    en = (d, (KS[i][1]["ad"], KL[j][1]["ad"]))
            return en

        en = dal_sinir(G)
        Gd = G.copy()                                   # yalniz dirsek parcalari (ust kol tupunun altindaki her sey)
        Gd[[i for i, (ad, _) in enumerate(KS) if not ad.startswith("dirsek")], :] = 1e9
        Gd[:, [j for j, (ad, _) in enumerate(KL) if not ad.startswith("dirsek")]] = 1e9
        en_d = dal_sinir(Gd)
        sonuc.append(dict(tip=tip, sag=list(pr), sol=list(pl), bosluk_mm=round(en[0], 1), cift=en[1], cakisma=v_cak,
                          dirsek_bosluk_mm=round(en_d[0], 1), dirsek_cift=en_d[1], kutu_bosluk_min=round(float(G.min()), 1)))
    en = min(sonuc, key=lambda s: s["bosluk_mm"])
    en_d = min(sonuc, key=lambda s: s["dirsek_bosluk_mm"])
    print("kol-kol: %d poz cifti, cakisan %d, en kucuk bosluk %.1f mm %s sag %s sol %s; dirsek parcalari arasi %.1f mm %s sag %s sol %s %.0fs" % (
        len(sonuc), sum(1 for s in sonuc if s["cakisma"]), en["bosluk_mm"], en["cift"], en["sag"], en["sol"],
        en_d["dirsek_bosluk_mm"], en_d["dirsek_cift"], en_d["sag"], en_d["sol"], time.time() - ts), flush=True)
    return dict(poz_cifti=len(sonuc), cakisan=sum(1 for s in sonuc if s["cakisma"]), en_kucuk=en, en_kucuk_dirsek=en_d,
                tip_ozet={t: min([s for s in sonuc if s["tip"] == t], key=lambda s: s["bosluk_mm"]) for t in sorted(set(s["tip"] for s in sonuc))},
                pozlar=sonuc, sure_s=round(time.time() - ts, 1),
                not_="hareketli: iki kolun omuz gobegi + ust kol (omuz) + dirsek parcalari; poz = (one-arka, yana, dirsek, bilek), "
                     "sol kolda ayni acilar aynali hareket")


kol_kol_sonuc = kol_kol() if all("dirsek_" + t in MODUL for t in ("sag", "sol")) else None

# ====================================================================== 5) toplam kutle ve agirlik merkezi (ev pozu)
m_top, cg = 0.0, V(0, 0, 0)
km = {}
for ad in KONTROL:
    mm = 0.0
    for p in MODUL[ad]["parcalar"]:
        if p["haric"] or p["kutle"] <= 0:
            continue
        m_top += p["kutle"]
        mm += p["kutle"]
        cg = cg + p["gmerkez"] * p["kutle"]
    km[ad] = round(mm, 1)
cg = cg * (1.0 / m_top)

out = dict(
    moduller=[dict(ad=ad, konum=list(A.MODULLER[ad]["konum"]), ayna=A.MODULLER[ad]["ayna"], parca=len(MODUL[ad]["parcalar"]),
                   haric=[p["ad"] for p in MODUL[ad]["parcalar"] if p["haric"]], haric_neden=MODUL[ad]["haric_neden"],
                   hareketli=bool(MODUL[ad]["hareket"]) or bool(MODUL[ad].get("zincir")),
                   bagli=(MODUL[ad].get("zincir") or {}).get("omuz")) for ad in KONTROL],
    ayrilmis_bolge=dict(sayi=len(bolge_parca), sahipler=sorted(set(z["sahip"] for z in A.bolgeler(haric=KONTROL)))),
    arayuz_uyumu=uyum,
    ev_pozu_cakisma=statik, ev_pozu_kesisen_cift=n_statik,
    zarf={k: [round(v.XMin, 1), round(v.XMax, 1), round(v.YMin, 1), round(v.YMax, 1), round(v.ZMin, 1), round(v.ZMax, 1)]
          for k, v in zarf.items()},
    tarama=tarama,
    kol_tarama=kol_tarama, kol_kol=kol_kol_sonuc,
    toplam=dict(cakisma=len(statik) + sum(t["cakisan_poz"] for t in tarama.values())
                + sum(k["cakisan_tam_poz_aralikta"] + k["cakisan_tam_poz_aralik_disi"] for k in kol_tarama.values())
                + (kol_kol_sonuc["cakisan"] if kol_kol_sonuc else 0),
                eklem_araliginda=len(statik) + sum(t["eklem_araliginda_cakisan"] for t in tarama.values())
                + sum(k["cakisan_tam_poz_aralikta"] + k["cakisan_alt_poz_aralikta"] for k in kol_tarama.values())
                + (kol_kol_sonuc["cakisan"] if kol_kol_sonuc else 0),
                not_="kol taramasinda eklem araliginda = kaba izgarada cakisan tam poz + cakisan (kaba ve ince) alt poz"),
    kutle_g=km, kutle_toplam_g=round(m_top, 1), agirlik_merkezi=[round(cg.x, 2), round(cg.y, 2), round(cg.z, 2)],
    tolerans_mm3=TOL, sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "carpisma-sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("TOPLAM cakisma (ev pozu + tarama):", out["toplam"]["cakisma"], "| eklem araliginda:", out["toplam"]["eklem_araliginda"],
      "| kutle %.1f g, AM (%.1f, %.1f, %.1f)" % (m_top, cg.x, cg.y, cg.z), "| %.1fs" % (time.time() - t0))
