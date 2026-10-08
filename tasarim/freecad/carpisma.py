# Moduller arasi carpisma kontrolu (FreeCAD 1.1). arayuz.MODULLER yerlesimiyle modulleri global koordinata
# koyar, (1) ev pozunda tum modul ciftlerini, (2) her hareketli modulun tum tarama pozlarinda hareketli
# parcalarini diger modullere karsi, (3) henuz cizilmemis modullerin ayrilmis bolgelerini (arayuz.BOLGELER)
# tarar. Yeni modul eklemek: MODUL_YUKLE'ye bir yukleyici ekle (parcalar + hareket + haric listesi).
# Calistir: FC_SCRIPT=<bu dosya> freecadcmd run_fc.py   ->  carpisma-sonuc.json
import os, sys, json, time
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (HERE, os.path.join(HERE, "iskelet"), os.path.join(HERE, "omuz"), os.path.join(HERE, "kabuk")):
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


MODUL_YUKLE = {"iskelet": yukle_iskelet, "omuz_sag": yukle_omuz, "omuz_sol": yukle_omuz, "kabuk": yukle_kabuk}
KONTROL = ["iskelet", "omuz_sag", "omuz_sol", "kabuk"]   # sonraki moduller (taban, kafa, dirsek) buraya eklenir


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
    if MODUL[ad]["hareket"]:
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

# ====================================================================== 4) toplam kutle ve agirlik merkezi (ev pozu)
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
                   hareketli=bool(MODUL[ad]["hareket"])) for ad in KONTROL],
    ayrilmis_bolge=dict(sayi=len(bolge_parca), sahipler=sorted(set(z["sahip"] for z in A.bolgeler(haric=KONTROL)))),
    arayuz_uyumu=uyum,
    ev_pozu_cakisma=statik, ev_pozu_kesisen_cift=n_statik,
    zarf={k: [round(v.XMin, 1), round(v.XMax, 1), round(v.YMin, 1), round(v.YMax, 1), round(v.ZMin, 1), round(v.ZMax, 1)]
          for k, v in zarf.items()},
    tarama=tarama,
    toplam=dict(cakisma=len(statik) + sum(t["cakisan_poz"] for t in tarama.values()),
                eklem_araliginda=len(statik) + sum(t["eklem_araliginda_cakisan"] for t in tarama.values())),
    kutle_g=km, kutle_toplam_g=round(m_top, 1), agirlik_merkezi=[round(cg.x, 2), round(cg.y, 2), round(cg.z, 2)],
    tolerans_mm3=TOL, sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "carpisma-sonuc.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("TOPLAM cakisma (ev pozu + tarama):", out["toplam"]["cakisma"], "| eklem araliginda:", out["toplam"]["eklem_araliginda"],
      "| kutle %.1f g, AM (%.1f, %.1f, %.1f)" % (m_top, cg.x, cg.y, cg.z), "| %.1fs" % (time.time() - t0))
