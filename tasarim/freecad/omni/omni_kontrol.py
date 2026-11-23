# On omni teker + gobek adaptoru - tasarim ajani kontrolleri (freecadcmd). 1. asama: yalniz kendi parcalari ve cevresi.
# FC_SCRIPT=<bu dosya> freecadcmd run_fc.py  -> omni-kontrol.json, omni-bom.csv, omni-montaj.FCStd, omni-on-teker.step, stl/
# OMNI_KIP=lastik: TABAN_OMNI=0 geri donusunu sinar (taban_parcalar lastik on tekerle kurulur) -> lastik-geri-donus.json (baska dosya yazmaz).
# Yapilan: yeni parcalarin gecerliligi / tek kati; yeni parcalar x taban parcalari cakisma; baglanti kontrolleri (taban_montaj ile ayni
# olcutler: dayanma, eksen hizasi, dis / insert kavramasi); teker cevresi bosluklari (donen zarf ve statik sekil): etek (kabuk STEP),
# iskelet (STEP), taban parcalari (plaka, braket, motor civatalari, sonarlar), zemin; adaptor baski analizi (X2D).
# YAPILMAYAN (2. asama): carpisma.py / carpisma_kos.py taramasi, taban_montaj.py yeniden uretimi, ana montaj (montaj/) ve regresyon.
import os, sys, json, math, time, csv
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "taban")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
KIP = os.environ.get("OMNI_KIP", "")
if KIP == "lastik":
    os.environ["TABAN_OMNI"] = "0"
import arayuz as A
import taban_parcalar as TP
import taban_lib as L
from taban_parcalar import P, BAG

V = App.Vector
t0 = time.time()
TOL = 0.5          # mm3 (taban_montaj ile ayni)
TEMAS = 0.01       # mm


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


def r2(x, n=2):
    return None if x is None else round(x, n)


# ---------------------------------------------------------------------- geri donus kipi (lastik on teker)
if KIP == "lastik":
    on = [p["ad"] for p in P if p["grup"] == "Tahrik" and ("(on sag)" in p["ad"] or "(on sol)" in p["ad"]) and ("Teker" in p["ad"] or "Omni" in p["ad"])]
    out = dict(kip="TABAN_OMNI=0", omni_aktif=TP.OMNI, parca=len(P), gercek=sum(1 for p in P if p["tur"] != "Referans"), baglanti=len(BAG),
               on_tekerler=on, gecersiz=[p["ad"] for p in P if not p["shape"].isValid()], coklu=[p["ad"] for p in P if p["kati"] != 1],
               baski=sorted(TP.BASKI), toplam_kutle_g=round(sum(p["kutle"] for p in P), 1))
    json.dump(out, open(os.path.join(HERE, "lastik-geri-donus.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log("lastik geri donus", out["omni_aktif"], out["parca"], out["on_tekerler"])
    raise SystemExit(0)

assert TP.OMNI, "omni kapali: arayuz.TABAN['omni']['aktif'] ya da TABAN_OMNI"
IDX = {p["ad"]: k for k, p in enumerate(P)}
OLC = L.omni_olcu()
log("taban parca", len(P), "omni kose", sorted(TP.OMNI_I))

# ---------------------------------------------------------------------- 1) yeni parcalar: gecerlilik, kati, kutle
YENI = set()
for key, oi in TP.OMNI_I.items():
    YENI.update([oi["teker"], oi["adaptor"]] + oi["m3"] + oi["pul3"] + oi["insert"])
yeni_ozet = [dict(ad=P[i]["ad"], gecerli=P[i]["shape"].isValid(), kati=P[i]["kati"], kutle_g=round(P[i]["kutle"], 1),
                  hacim_mm3=round(P[i]["hacim"], 1)) for i in sorted(YENI)]
gecersiz = [y["ad"] for y in yeni_ozet if not y["gecerli"] or y["kati"] != 1]
log("yeni parca", len(YENI), "gecersiz/coklu", gecersiz)


# ---------------------------------------------------------------------- 2) yeni parcalar x tum taban parcalari (cakisma)
def kes(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


cak, n_cift, temas = [], 0, []
for i in sorted(YENI):
    for j, q in enumerate(P):
        if j == i or q["tur"] == "Referans" or (j in YENI and j < i):
            continue
        if not P[i]["bb"].intersect(q["bb"]):
            continue
        n_cift += 1
        v = kes(P[i]["shape"], q["shape"])
        if v > TOL or v < 0:
            cak.append((P[i]["ad"], q["ad"], round(v, 3)))
log("yeni x taban cift", n_cift, "cakisma", cak)


# ---------------------------------------------------------------------- 3) baglantilar (taban_montaj.py 2. bolum olcutleri)
def eksen_sapma(sh, r, p, u):
    en = None
    for f in sh.Faces:
        s = f.Surface
        if s.__class__.__name__ != "Cylinder" or abs(s.Radius - r) > 1e-3:
            continue
        if s.Axis.cross(u).Length > 1e-6:
            continue
        d = (s.Center - p).cross(u).Length
        en = d if en is None else min(en, d)
    return en


bag_k = []
for b in BAG:
    if not (b["ad"].startswith("Omni") or (b["ad"].startswith("Kaplin - motor mili (on"))):
        continue
    o = b["olcu"]
    s = dict(ad=b["ad"], tip=b["tip"], olcu={k: round(v, 3) if isinstance(v, float) else v for k, v in o.items()}, hata=[], aciklama=b["aciklama"])
    tm = []
    for (i, j) in b["temas"]:
        d = P[i]["shape"].distToShape(P[j]["shape"])[0]
        tm.append(round(d, 4))
        if d > TEMAS:
            s["hata"].append("dayanmiyor: %s / %s (%.3f mm)" % (P[i]["ad"], P[j]["ad"], d))
    s["temas_mm"] = tm
    if b["eksen"]:
        p, u, liste = b["eksen"]
        es = []
        for (i, r) in liste:
            e = eksen_sapma(P[i]["shape"], r, p, u)
            es.append(None if e is None else round(e, 6))
            if e is None or e > 1e-4:
                s["hata"].append("eksen: %s r %.2f (%s)" % (P[i]["ad"], r, e))
        s["eksen_mm"] = es
    d = o.get("d", 0)
    if b["tip"] == "dis" and (o["kavrama"] < d or o["kavrama"] > o["delik"] - 0.5):
        s["hata"].append("dis kavramasi %.2f (delik %.1f)" % (o["kavrama"], o["delik"]))
    if b["tip"] == "insert" and (o["kavrama"] < d or o["kavrama"] > o["insert_boy"] + 2.5):
        s["hata"].append("insert kavramasi %.2f" % o["kavrama"])
    if b["tip"] == "mil" and o["kavrama"] < 1.5 * d:
        s["hata"].append("mil kavramasi %.1f" % o["kavrama"])
    s["tamam"] = not s["hata"]
    bag_k.append(s)
log("baglanti", sum(1 for s in bag_k if s["tamam"]), "/", len(bag_k), [s["ad"] + ": " + "; ".join(s["hata"]) for s in bag_k if not s["tamam"]])

# ---------------------------------------------------------------------- 4) bosluklar (sag on kose; sol ayna)
KEY = (1, 1)
oi = TP.OMNI_I[KEY]
DON = TP.TEKER_DONEN[KEY]                                    # donen grup (teker, adaptor, kaplin, civatalar)
YENI_DON = [i for i in DON if i != oi["kaplin"]]            # bosluk olcumu: kaplin lastik tekerle ortak, motor milini sarar (haric)
grup = Part.makeCompound([P[i]["shape"] for i in YENI_DON])
X0, YA, ZW = TP.X_OMNI, A.AX, TP.Z_WH
w = A.TABAN["omni"]["en"]
Ad = A.TABAN["omni"]["adaptor"]
# donen zarf: her yeni donen parcanin eksen etrafinda supurdugu hacim = parca basina halka (x araligi, ic / dis yaricap; yaricaplar
# ucgenlenmis yuzey noktalarindan, teker ve adaptor analitik). Statik parcalara bosluk bu zarftan olculur (donus konumundan bagimsiz).
def zarf():
    dil = []
    for i in YENI_DON:
        sh = P[i]["shape"]
        bb = sh.BoundBox
        pts = sh.tessellate(0.05)[0]
        rr = [math.hypot(q.y - YA, q.z - ZW) for q in pts]
        rmin, rmax = min(rr), max(rr)
        if i == oi["teker"]:
            rmin, rmax = A.TABAN["omni"]["tahmin"]["gobek_delik_d"] / 2, A.TABAN["omni"]["cap"] / 2
        elif i == oi["adaptor"]:
            rmin, rmax = (L.KAP["af"] + Ad["altigen_pay"]) / 2, Ad["flans_d"] / 2
        elif rmin < 1.0:
            rmin = 0.0
        dil.append((bb.XMin, bb.XMax, rmax, P[i]["ad"], rmin))
    sil = []
    for (x0, x1, r, _, ri) in dil:
        c = Part.makeCylinder(r, x1 - x0, V(x0, YA, ZW), V(1, 0, 0))
        if ri > 0.05:
            c = c.cut(Part.makeCylinder(ri, x1 - x0 + 2, V(x0 - 1, YA, ZW), V(1, 0, 0)))
        sil.append(c)
    return sil[0].fuse(sil[1:]).removeSplitter(), dil


ZARF, ZARF_DIL = zarf()
log("zarf", round(ZARF.BoundBox.XMin, 2), round(ZARF.BoundBox.XMax, 2), round(ZARF.BoundBox.YMin, 2), round(ZARF.BoundBox.YMax, 2))


def en_yakin(sh, adaylar, genis=80.0):
    gb = App.BoundBox(sh.BoundBox)
    gb.enlarge(genis)
    out = []
    for ad, q in adaylar:
        if not gb.intersect(q.BoundBox):
            continue
        d, pr, _ = sh.distToShape(q)
        out.append(dict(parca=ad, bosluk_mm=round(d, 2), nokta_teker=[round(c, 1) for c in pr[0][0]], nokta_diger=[round(c, 1) for c in pr[0][1]]))
    return sorted(out, key=lambda x: x["bosluk_mm"])


# 4a) taban parcalari (donen grup ve kosenin donmeyenleri haric degil: motor, braket, civatalar statik -> zarfa karsi)
statik = [(p["ad"], p["shape"]) for k, p in enumerate(P) if p["tur"] != "Referans" and k not in DON]   # kaplin de haric (donen)
taban_yakin = en_yakin(ZARF, statik, 60.0)
log("taban yakin", [(t["parca"][:34], t["bosluk_mm"]) for t in taban_yakin[:8]])
taban_yakin_statik = en_yakin(grup, statik, 60.0)[:8]
# on sensorler (HC-SR04 + tutucular): sag on zarftan uzaklik (tum ucu, genis pencere)
sensor = en_yakin(ZARF, [(n, s) for n, s in statik if n.startswith("HC-SR04") or n.startswith("Sonar")], 600.0)
log("sensor", [(t["parca"], t["bosluk_mm"]) for t in sensor[:4]])


# 4b) etek / kabuk (kabuk STEP) ve iskelet (STEP): adlarla (Import.insert) ya da adsiz (Part.read)
def step_parcalari(yol, filtre, onek):
    try:
        import Import
        d = App.newDocument("omni_tmp")
        Import.insert(yol, d.Name)
        out = []
        for o in d.Objects:
            if o.TypeId == "Part::Feature" and o.Shape.Solids:
                s = o.Shape.copy()
                s.Placement = o.getGlobalPlacement()
                s = s.copy()
                if filtre(s):
                    out.append(("%s %s" % (onek, o.Label.split()[-1]), s))
        App.closeDocument(d.Name)
        if out:
            return out, "Import.insert"
    except Exception as e:
        log("Import.insert olmadi", e)
    sh = Part.read(yol)
    return [("%s %d" % (onek, k), s) for k, s in enumerate(sh.Solids) if filtre(s)], "Part.read"


bolge = App.BoundBox(ZARF.BoundBox)
bolge.enlarge(90.0)
yakin_f = lambda s: s.BoundBox.intersect(bolge)
kabuk_yol = os.path.join(UST, "kabuk", "kabuk-montaj.step")
isk_yol = os.path.join(UST, "iskelet", "iskelet-montaj.step")
kab, kab_yontem = step_parcalari(kabuk_yol, yakin_f, "Kabuk/etek katisi")
isk, isk_yontem = step_parcalari(isk_yol, yakin_f, "Iskelet katisi")
log("kabuk yakin kati", len(kab), kab_yontem, "iskelet", len(isk), isk_yontem)
etek_yakin = en_yakin(ZARF, kab, 90.0)
isk_yakin = en_yakin(ZARF, isk, 90.0)
kabuk_cak = [(a, round(kes(grup, s), 3)) for a, s in kab if kes(grup, s) > TOL]
isk_cak = [(a, round(kes(grup, s), 3)) for a, s in isk if kes(grup, s) > TOL]


# yon bazinda etek bosluklari: tekerin (zarfin) +x, +z, +y yonunde etege uzaklik (zarf yuzeyinden isin)
def isin(p, u, hedef, L=150.0):
    seg = Part.LineSegment(p, p + u * L).toShape()
    en = None
    for a, s in hedef:
        if not seg.BoundBox.intersect(s.BoundBox):
            continue
        d = seg.distToShape(s)
        if d[0] < 1e-6:
            # ilk kesisim: segmentin kati yuzleriyle kesisim noktalarindan p'ye en yakini
            sec = seg.section(s)
            pts = [v.Point for v in sec.Vertexes] or [d[1][0][0]]
            t = min((q - p).Length for q in pts)
            if en is None or t < en[0]:
                en = (t, a)
    return en


ro = A.TABAN["omni"]["cap"] / 2
yon = {}
for ad_y, p0, u in (("yan (+x, teker dis yuzunden, aks yuksekliginde)", V(X0 + w / 2, YA, ZW), V(1, 0, 0)),
                    ("yan (+x, M3 basi dis yuzunden)", V(OLC["m3_bas_dis_x"], YA + A.TABAN["omni"]["tahmin"]["pcd"] / 2 * math.sin(math.radians(45)), ZW + A.TABAN["omni"]["tahmin"]["pcd"] / 2 * math.cos(math.radians(45))), V(1, 0, 0)),
                    ("on (+z, aks yuksekliginde)", V(X0, YA, ZW + ro), V(0, 0, 1)),
                    ("ust (+y, teker tepesinden)", V(X0, YA + ro, ZW), V(0, 1, 0)),
                    ("ic (-x, teker ic yuzunden, aks ustu 45)", V(X0 - w / 2, YA + 45, ZW), V(-1, 0, 0))):
    r = isin(p0, u, kab + isk + [(n, s) for n, s in statik if s.BoundBox.intersect(bolge)])
    yon[ad_y] = None if r is None else dict(bosluk_mm=round(r[0], 2), parca=r[1])
log("yon bosluklari", yon)

# lastik on teker ile karsilastirma (ayni etek): lastik dis yuzu 245, etek ic yuzu ETEK_A - KABUK_T
lastik = dict(yan_mm=A.ETEK_A - A.KABUK_T - (A._X_WH + A.TEKER_W / 2), on_mm=A.ETEK_B - A.KABUK_T - (TP.Z_WH + A.TEKER_D / 2),
              not_="arayuz ETEK_A / ETEK_B (analitik, lastik 125 x 58 x 216)")

# 4c) zemin
obb = grup.optimalBoundingBox() if hasattr(grup, "optimalBoundingBox") else grup.BoundBox
zemin = dict(teker_alt_y=round(P[oi["teker"]]["shape"].optimalBoundingBox().YMin, 3), aks_y=YA, teker_yaricap=ro,
             analitik=OLC["zemin_y"],
             not_="aks yuksekligi AX 62,5 ortak (motor braketi); O127 omni CAD'de zeminin %.1f mm altina iner. Gercekte on uc %.1f mm "
                  "yukselir, egim atan(%.1f / %.0f) = %.2f derece (fizik modeli ONERI-ADAY ile ayni kabul)" % (
                      -OLC["zemin_y"], -OLC["zemin_y"], -OLC["zemin_y"], 2 * TP.Z_WH,
                      math.degrees(math.atan(-OLC["zemin_y"] / (2 * TP.Z_WH)))))
ic_yuz = dict(flans_motor_yuzu_x=OLC["flans_motor_yuzu_x"], motor_civata_bas_x=TP.X_BR + L.BRK["t"] + L.DIN912_T[3][1], braket_x=TP.X_BR + L.BRK["t"],
              flans_m3_bas_bosluk=round(OLC["flans_motor_yuzu_x"] - (TP.X_BR + L.BRK["t"] + L.DIN912_T[3][1]), 2),
              flans_braket_bosluk=round(OLC["flans_motor_yuzu_x"] - (TP.X_BR + L.BRK["t"]), 2),
              kaplin_acik_boy=round(OLC["kaplin_acik"], 2))
log("ic yuz", ic_yuz, "zemin", zemin["teker_alt_y"])

# ---------------------------------------------------------------------- 5) baski analizi (adaptor, sag)
ad_a = P[oi["adaptor"]]["ad"]
bd = TP.BASKI[ad_a]
bas = L.baski_analiz(ad_a, P[oi["adaptor"]]["shape"], bd["yukari"], TP.DOLULUK)
bas["yon"] = bd["yon"]
bas["adet"] = 2
log("baski", bas.get("olcu"), bas.get("sigar"), bas.get("cikinti_orani"), bas.get("destek_sorun_sayi"))

# ---------------------------------------------------------------------- 6) dosyalar: FCStd (gorsel icin), STEP, STL, BOM, json
RENK_TUR = {}
doc = App.newDocument("omni_montaj")


def ekle(ad, sh, renk, tur, patlat=(0, 0, 0), grup_ad="Omni"):
    o = doc.addObject("Part::Feature", "P%03d" % len(doc.Objects))
    o.Label = ad
    o.Shape = sh
    for pr, v in (("Renk", renk), ("Tur", tur), ("Grup", grup_ad)):
        o.addProperty("App::PropertyString", pr, "Lale")
        setattr(o, pr, v)
    o.addProperty("App::PropertyVector", "Patlat", "Lale")
    o.Patlat = V(*patlat)
    return o


# on iki kose: donen grup + motor, braket, braket civatalari; on yarinin plakasi, sonarlar, kat (baglam)
kose_ad = {}
for key in sorted(TP.OMNI_I):
    sx, sz = key
    k = "%s %s" % (TP.SZ(sz), TP.SX(sx))
    for i, p in enumerate(P):
        if p["tur"] == "Referans":
            continue
        if ("(%s" % k) in p["ad"] or ("(teker %s)" % k) in p["ad"] or ("(braket %s" % k) in p["ad"] or ("(motor %s" % k) in p["ad"] or ("(omni %s" % k) in p["ad"]:
            kose_ad[i] = "Kose"
baglam = {}
for i, p in enumerate(P):
    if i in kose_ad or p["tur"] == "Referans":
        continue
    bb = p["bb"]
    if bb.ZMax > 60 and bb.YMin < 230 and bb.XMax > 0:       # sag on ceyrek, katin ustu haric
        baglam[i] = "Baglam"
for i, p in enumerate(P):                                    # arka sag kose (yan gorunumde lastik arka teker)
    if i not in kose_ad and p["grup"] == "Tahrik" and "arka sag" in p["ad"]:
        baglam[i] = "Baglam"
for i, g in list(kose_ad.items()) + list(baglam.items()):
    p = P[i]
    ekle(p["ad"], p["shape"], p["renk"], p["tur"] if g == "Kose" else "Baglam", p["patlat"], g)
# etek (kabuk STEP'ten, yakin katilar) ve iskelet yakin katilari: baglam
for a, s in kab:
    ekle("Etek: " + a, s, "etek", "Baglam_etek", grup_ad="Etek")
for a, s in isk:
    ekle("Iskelet: " + a, s, "alu", "Baglam_iskelet", grup_ad="Iskelet")
# kesit (aks duzlemi z = ZW, on yarisi kaldirilmis): sag on kose donen grup + motor + braket
kes_kutu = Part.makeBox(400, 400, 200, V(0, -50, ZW))
for i in DON + [IDX["Motor JGB37-520 (on sag)"], IDX["Motor braketi L 37 mm (on sag)"]]:
    try:
        c = P[i]["shape"].cut(kes_kutu)
        if c.Volume > 1e-3:
            ekle("Kesit: " + P[i]["ad"], c, P[i]["renk"], "Kesit", grup_ad="Kesit")
    except Exception as e:
        log("kesit olmadi", P[i]["ad"], e)
doc.recompute()
fc = os.path.join(HERE, "omni-montaj.FCStd")
doc.saveAs(fc)
# STEP: sag on kose (donen grup + motor + braket + civatalar), mm
step_ob = [o for o in doc.Objects if o.Grup == "Kose" and "on sag" in o.Label]
Part.export(step_ob, os.path.join(HERE, "omni-on-teker.step"))
os.makedirs(os.path.join(HERE, "stl"), exist_ok=True)
import Mesh, MeshPart
ash = P[oi["adaptor"]]["shape"].copy()
ash.transformShape(App.Placement(V(0, 0, 0), App.Rotation(bd["yukari"], V(0, 0, 1))).toMatrix(), True)
ash.translate(V(-ash.BoundBox.Center.x, -ash.BoundBox.Center.y, -ash.BoundBox.ZMin))
m = MeshPart.meshFromShape(Shape=ash, LinearDeflection=0.02, AngularDeflection=0.2)
m.write(os.path.join(HERE, "stl", "omni-gobek-adaptoru.stl"))
App.closeDocument(doc.Name)
log("FCStd", round(os.path.getsize(fc) / 1024), "KB", "STEP", len(step_ob))

# parca / baglanti listesi (robot basina, on iki kose) + cikan parcalar
say = {}
for key, o2 in TP.OMNI_I.items():
    for i in [o2["teker"], o2["adaptor"]] + o2["m3"] + o2["pul3"] + o2["insert"]:
        p = P[i]
        kk = (p["tur"], p["kod"], p["malzeme"])
        say.setdefault(kk, [0, 0.0])
        say[kk][0] += 1
        say[kk][1] += p["kutle"]
bom = [dict(degisim="eklenir", tur=t, kalem=kod, malzeme=mz, adet=n, kutle_g=round(g, 1)) for (t, kod, mz), (n, g) in sorted(say.items())]
bom.append(dict(degisim="cikar (on iki kose)", tur="Satin", kalem="Arazi tekerlegi 125 x 58", malzeme="Kaucuk + plastik", adet=2,
                kutle_g=round(2 * L.TEK["kutle_g"], 1)))
bom.append(dict(degisim="ayni (on iki kose)", tur="Satin", kalem="12 mm altigen kaplin x 30, O6 + M4x16 DIN 912 + M4 pul (lastik tekerdeki gibi)",
                malzeme="Pirinc / celik", adet=2, kutle_g=None))
bom.append(dict(degisim="alinmaz (secenek)", tur="Satin", kalem="Nexus 6 mm gobek 18007 (adaptor yerine; motor mili D 6 mm, kaplin kalkar)",
                malzeme="Al", adet=0, kutle_g=None))
with open(os.path.join(HERE, "omni-bom.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    wr = csv.writer(fh, delimiter=";")
    wr.writerow(["Degisim", "Tur", "Kalem", "Malzeme", "Adet", "Toplam kutle (g)"])
    for b in bom:
        wr.writerow([b["degisim"], b["tur"], b["kalem"], b["malzeme"], b["adet"], "" if b["kutle_g"] is None else ("%.1f" % b["kutle_g"])])

kutle_fark = sum(b["kutle_g"] for b in bom if b["degisim"] == "eklenir") - 2 * L.TEK["kutle_g"]
taban_kutle = sum(p["kutle"] for p in P)
geri = None
gy = os.path.join(HERE, "lastik-geri-donus.json")
if os.path.exists(gy):
    geri = json.load(open(gy, encoding="utf-8"))

out = dict(
    asama="1 (tasarim ajani; resmi carpisma taramasi, taban_montaj / ana montaj regresyonu 2. asamada)",
    olcu=OLC, olcu_not="taban_lib.omni_olcu(): analitik zincir (mm, sag on kose; sol ayna)",
    merkez=dict(omni_x=A.OMNI_X, lastik_x=A._X_WH, iceri_mm=A.OMNI_ICERI, on_iz=A.ON_IZ, arka_iz=A.ARKA_IZ, beklenti_iceri=14.5, beklenti_daralma=29.0,
                fark_iceri=round(A.OMNI_ICERI - 14.5, 6), fark_daralma=round((A.ARKA_IZ - A.ON_IZ) - 29.0, 6),
                cad_teker_merkez_x=round(P[oi["teker"]]["shape"].BoundBox.Center.x, 4),
                cad_teker_ic_yuz_x=round(P[oi["teker"]]["shape"].BoundBox.XMin, 4), cad_teker_dis_yuz_x=round(P[oi["teker"]]["shape"].BoundBox.XMax, 4),
                cad_kaplin_ucu_x=round(P[oi["kaplin"]]["shape"].BoundBox.XMax, 4), cad_mil_ucu_x=round(TP.X_BR + L.JGB["sh_l"], 4),
                cad_adaptor_x=[round(P[oi["adaptor"]]["shape"].BoundBox.XMin, 4), round(P[oi["adaptor"]]["shape"].BoundBox.XMax, 4)]),
    yeni_parca=yeni_ozet, gecersiz=gecersiz, yeni_x_taban=dict(cift=n_cift, cakisma=cak),
    baglanti=bag_k, baglanti_tamam=sum(1 for s in bag_k if s["tamam"]),
    bosluk=dict(zarf_dilim=[dict(x0=r2(a), x1=r2(b), r=r2(c), r_ic=r2(e), parca=d) for a, b, c, d, e in ZARF_DIL],
                taban_zarf=taban_yakin[:12], taban_statik=taban_yakin_statik, sensor=sensor, etek_zarf=etek_yakin[:8], iskelet_zarf=isk_yakin[:6],
                kabuk_cakisma=kabuk_cak, iskelet_cakisma=isk_cak, yon=yon, lastik_karsilastirma=lastik, ic_yuz=ic_yuz, zemin=zemin,
                kaynak=dict(kabuk=os.path.basename(kabuk_yol) + " (" + kab_yontem + ", %d kati)" % len(kab),
                            iskelet=os.path.basename(isk_yol) + " (" + isk_yontem + ", %d kati)" % len(isk))),
    baski=bas, bom=bom, kutle=dict(on_iki_kose_fark_g=round(kutle_fark, 1), taban_toplam_g=round(taban_kutle, 1)),
    tahmin=A.TABAN["omni"]["tahmin"], olculecek=A.TABAN["omni"]["olculecek"], adaptor=A.TABAN["omni"]["adaptor"],
    geri_donus=geri, sure_s=round(time.time() - t0, 1))
json.dump(out, open(os.path.join(HERE, "omni-kontrol.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("yazildi omni-kontrol.json")
