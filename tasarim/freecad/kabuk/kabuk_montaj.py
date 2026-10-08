# Kabuk modulu (V3) - montaj, kontroller, baski analizi, FCStd + STEP + BOM + analiz json
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
# Kontroller: her parca isValid + tek kati; kabuk ici cakisma (0,5 mm3); kabuk <-> iskelet cakisma; ayrilmis bolgeler;
# iskelete baglanti (braket dayanmasi, cekic somun dudak altinda, civata ucu payi, eksen hizasi, isil gomme somun
# kavrama boyu ve dis yuzeye kalan et); bindirme ve ekran civatalari; her baski parcasi icin yaziciya sigma, baski yonu,
# 45 derece cikinti orani, katman katman desteksiz basilabilirlik, tahmini kutle / filament / sure.
import os, sys, json, math, time, csv
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "iskelet")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import kabuk_parcalar as K
import arayuz as A
from ortak_lib import V, box

P, BAG, VIDA = K.P, K.BAG, K.VIDA
t0 = time.time()
TOL = 0.5
TEMAS = 0.01


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))


for p in P:
    p["obb"] = p["shape"].optimalBoundingBox()
log("parca sayisi", len(P), "baglanti", len(BAG), "civata", len(VIDA))


def kes(a, b, abb, bbb):
    if not abb.intersect(bbb):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


# ====================================================================== 1) gecerlilik ve kabuk ici cakisma
gecersiz = [p["ad"] for p in P if not p["shape"].isValid()]
coklu = [(p["ad"], p["kati"]) for p in P if p["kati"] != 1]
cakisma, n_cift = [], 0
for i in range(len(P)):
    for j in range(i + 1, len(P)):
        a, b = P[i], P[j]
        if not a["obb"].intersect(b["obb"]):
            continue
        n_cift += 1
        v = kes(a["shape"], b["shape"], a["obb"], b["obb"])
        if v > TOL or v < 0:
            cakisma.append((a["ad"], b["ad"], round(v, 3)))
log("gecersiz", len(gecersiz), "coklu kati", len(coklu), "kabuk ici cakisma", len(cakisma), "(cift %d)" % n_cift)

# ====================================================================== 2) kabuk <-> iskelet
import iskelet_parcalar as I
for q in I.P:
    q["obb"] = q["shape"].optimalBoundingBox()
isk_cak, n_isk = [], 0
for p in P:
    for q in I.P:
        if p["obb"].intersect(q["obb"]):
            n_isk += 1
            v = kes(p["shape"], q["shape"], p["obb"], q["obb"])
            if v > TOL or v < 0:
                isk_cak.append((p["ad"], q["ad"], round(v, 3)))
log("kabuk-iskelet cakisma", len(isk_cak), "(cift %d)" % n_isk)

# ====================================================================== 3) ayrilmis bolgeler
bolge_ihlal, bolge_n, bolge_bosluk = [], 0, []
for z in A.BOLGELER:
    if z["sahip"] in ("iskelet", "omuz_sag", "omuz_sol"):
        continue          # bu modullerin gercek geometrisi ayrica kontrol ediliyor
    if z["sahip"] == "kabuk" and not z["ad"].startswith("Nextion"):
        continue          # kabugun kendi braket bolgeleri (icinde kabuk braketleri var)
    kb = box(*z["kutu"])
    for c in z["bosluk"]:
        kb = kb.cut(box(*c))
    bolge_n += 1
    en_yakin = (1e9, None)
    for p in P:
        if z["ad"].startswith("Nextion") and p["ad"].startswith("Nextion"):
            continue      # konnektor bolgenin icinde (tasarim geregi)
        if p["obb"].intersect(kb.BoundBox):
            v = p["shape"].common(kb).Volume
            if v > TOL:
                bolge_ihlal.append((z["ad"], z["sahip"], p["ad"], round(v, 2)))
        if p["tur"] == "Baski":
            bbx = App.BoundBox(p["obb"])
            bbx.enlarge(20)
            if bbx.intersect(kb.BoundBox):
                dd = p["shape"].distToShape(kb)[0]
                if dd < en_yakin[0]:
                    en_yakin = (dd, p["ad"])
    if en_yakin[1]:
        bolge_bosluk.append((z["sahip"], z["ad"], round(en_yakin[0], 2), en_yakin[1]))
log("ayrilmis bolge:", bolge_n, "bolge,", len(bolge_ihlal), "ihlal")


# ====================================================================== 4) baglanti kontrolleri
def mesafe(sa, sb):
    return sa.distToShape(sb)[0]


def eksen_disi(sh, nokta, yon):
    c = sh.BoundBox.Center
    d = c - V(*nokta)
    u = V(*yon)
    u.normalize()
    return (d - u * d.dot(u)).Length


IDX = {p["ad"]: k for k, p in enumerate(P)}
PAR = {ad: P[d["indeks"]]["shape"] for ad, d in K.PARCA.items()}
direk = next(q for q in I.P if q["ad"] == "Govde diregi")["shape"]
ray = {1: next(q for q in I.P if q["ad"] == "Sase uzun rayi sag")["shape"], -1: next(q for q in I.P if q["ad"] == "Sase uzun rayi sol")["shape"]}
somun_alti = A.LIP + A.CEKIC_SOMUN["T"]
bag_kontrol = []
for b in BAG:
    k = []
    br = P[b["govde"]]["shape"]
    el = [P[i] for i in b["eleman"]]
    sx = b["sx"]
    parca = PAR[b["parca"]]
    if b["tip"] == "govde":
        prof, nv = direk, V(sx, 0, 0)
        yuzler = [V(sx * A.SG / 2, b["yb"] + dy, 0) for dy in A.KABUK_GOVDE_BRAKET["m6_y"]]
    else:
        prof, nv = ray[sx], V(0, 1, 0)
        yuzler = [V(b["xr"], A.Y_RAIL1, b["zb"])]
    d = mesafe(br, prof)
    k.append(("braket profile dayali", round(d, 4), d <= TEMAS))
    d = mesafe(br, parca)
    k.append(("braket kabuk boss'una dayali (%s)" % b["parca"], round(d, 4), d <= TEMAS))
    for i, yuz in enumerate(yuzler):
        pul, civ, som = el[3 * i], el[3 * i + 1], el[3 * i + 2]
        d = mesafe(som["shape"], prof)
        k.append(("M6 cekic somun dudak altina dayali", round(d, 4), d <= TEMAS))
        uc = max((yuz - v.Point).dot(nv) for v in civ["shape"].Vertexes)
        k.append(("M6 civata ucu yuzden %.1f mm iceride (somun alti %.1f, kanal tabani %.1f)" % (uc, somun_alti, A.KANAL_TABAN),
                  round(uc, 3), somun_alti <= uc < A.KANAL_TABAN))
        ed = eksen_disi(som["shape"], yuz, nv)
        k.append(("M6 civata ekseni somun deligi ekseninde", round(ed, 4), ed < 1e-6))
        d = mesafe(pul["shape"], br)
        k.append(("M6 pul brakete dayali", round(d, 4), d <= TEMAS))
    # kabuk tarafi: isil gomme somun + civata
    ins = el[-1]
    civ = el[-2]
    if b["tip"] == "govde":
        ax, x_agiz = V(sx, 0, 0), sx * b["xw"]
        a_y = K.kesit_param(K.GK, b["yc"])[0][0]
        nok = V(sx * b["xw"], b["yc"], 0)
        dmet = 5
    else:
        ax, x_agiz = V(sx, 0, 0), sx * A.KABUK_ETEK_BRAKET["x_ic"]
        a_y = K.kesit_param(K.EK, A.KABUK_ETEK_BRAKET["m3_y"])[0][0]
        nok = V(sx * A.KABUK_ETEK_BRAKET["x_ic"], A.KABUK_ETEK_BRAKET["m3_y"], b["zb"])
        dmet = 3
    L_ins = A.INSERT[dmet][1]
    uc = max(v.Point.x * sx for v in civ["shape"].Vertexes)
    kavrama = uc - x_agiz * sx
    et = a_y - uc
    k.append(("M%d civata kavramasi %.1f mm (isil gomme somun %.1f, delik %.1f)" % (dmet, kavrama, L_ins, L_ins + 0.5),
              round(kavrama, 3), dmet <= kavrama <= L_ins + 0.5))
    k.append(("M%d civata ucundan kabuk dis yuzune kalan et %.1f mm" % (dmet, et), round(et, 3), et >= 1.0))
    ed = max(eksen_disi(civ["shape"], nok, ax), eksen_disi(ins["shape"], nok, ax))
    k.append(("M%d civata ve isil gomme somun ayni eksende (braket deligi ile)" % dmet, round(ed, 4), ed < 1e-6))
    d = mesafe(ins["shape"], parca)
    k.append(("M%d isil gomme somun boss'ta oturuyor" % dmet, round(d, 4), d <= TEMAS))
    bag_kontrol.append(dict(ad=b["ad"], tip=b["tip"], parca=b["parca"], kontroller=k, tamam=all(x[2] for x in k)))
log("braket kontrol: %d/%d tamam" % (sum(1 for s in bag_kontrol if s["tamam"]), len(bag_kontrol)))

vida_kontrol = []
for v in VIDA:
    if v["tip"] != "bindirme":
        continue
    ins, civ = P[v["i_insert"]], P[v["i_vida"]]
    d_bas = mesafe(civ["shape"], PAR[v["dis"]])
    d_ins = mesafe(ins["shape"], PAR[v["ic"]])
    tip_derin = K.VIDA_L - v["hn"] - K.BAS_BOSLUK
    ok = d_bas <= K.BAS_BOSLUK + TEMAS and d_ins <= TEMAS and 3.0 <= tip_derin <= A.INSERT[3][1] and v["hn"] >= 1.2
    vida_kontrol.append(dict(etiket=v["etiket"], ic=v["ic"], dis=v["dis"], bas_dayali=round(d_bas, 4), insert_oturdu=round(d_ins, 4),
                             kavrama=round(tip_derin, 2), dudak=round(v["hn"], 2), tamam=ok))
ekran_kontrol = []
ekran = P[K.I_EKRAN]["shape"]
for v in VIDA:
    if v["tip"] != "ekran":
        continue
    d = mesafe(ekran, PAR[v["ic"]])
    ekran_kontrol.append(dict(etiket=v["etiket"], parca=v["ic"], pcb_boss_temas=round(d, 4),
                              kavrama=round(6.0 - A.NEXTION["pcb"][2], 2), tamam=d <= TEMAS))
log("bindirme civatasi tamam %d/%d, ekran %d/%d" % (sum(x["tamam"] for x in vida_kontrol), len(vida_kontrol),
                                                     sum(x["tamam"] for x in ekran_kontrol), len(ekran_kontrol)))

# ====================================================================== 5) bosluklar (tasarim olculeri)
teker = [z for z in A.BOLGELER if z["ad"].startswith("Teker")]
etek_parca = [ad for ad in K.PARCA if ad.startswith("Etek")]
teker_bosluk = min(PAR[ad].distToShape(box(*z["kutu"]))[0] for ad in etek_parca for z in teker)
govde_parca = [ad for ad in K.PARCA if not ad.startswith("Etek")]
direk_bosluk = min(PAR[ad].distToShape(direk)[0] for ad in govde_parca)
ekran_cam_bosluk = A.GOGUS_Z + A.KABUK_T / math.cos(math.radians(A.GOGUS_EGIM)) - A.KABUK_T  # yatay
log("teker-etek %.2f mm, direk-govde %.2f mm" % (teker_bosluk, direk_bosluk))

# ====================================================================== 6) baski analizi
import numpy as np
import MeshPart
Y = A.YAZICI
UX, UY, UZ = Y["kullanilabilir"]
BRIDGE = 15.0        # bu boydan uzun desteksiz bolge = destek gerekir (tahmini; 2 mm'den dar seritler hariç)


def baski_analiz(ad, sh, yukari):
    rot = App.Rotation(V(*yukari), V(0, 0, 1))
    s = sh.copy()
    s.transformShape(App.Placement(V(0, 0, 0), rot).toMatrix(), True)
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.25, AngularDeflection=0.35)
    pts, tris = mesh.Topology
    X = np.array([[p.x, p.y, p.z] for p in pts])
    Tn = np.array(tris)
    zmin, zmax = X[:, 2].min(), X[:, 2].max()
    # tablada en iyi yerlesim (Z ekseni etrafinda 0...90 derece)
    en = None
    for th in range(0, 91, 1):
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        x = X[:, 0] * c - X[:, 1] * s_
        y = X[:, 0] * s_ + X[:, 1] * c
        w, h = x.max() - x.min(), y.max() - y.min()
        w, h = max(w, h), min(w, h)
        if en is None or w < en[1]:
            en = (th, w, h)
    sigar = en[1] <= UX and en[2] <= UY and (zmax - zmin) <= UZ
    sigar_cift = en[1] <= Y["kullanilabilir_cift"][1] and en[2] <= Y["kullanilabilir_cift"][0] and (zmax - zmin) <= Y["kullanilabilir_cift"][2]
    # 45 derece cikinti orani (tabla yuzeyi haric)
    a, b, c3 = X[Tn[:, 0]], X[Tn[:, 1]], X[Tn[:, 2]]
    cr = np.cross(b - a, c3 - a)
    alan = 0.5 * np.linalg.norm(cr, axis=1)
    nz = cr[:, 2] / np.maximum(2 * alan, 1e-12)
    zc = (a[:, 2] + b[:, 2] + c3[:, 2]) / 3
    tabla = zc < zmin + 0.05
    cik = (nz < -math.cos(math.radians(45))) & ~tabla
    oran = float(alan[cik].sum() / alan.sum())
    # katman katman destek kontrolu (1 mm katman, 45 derece -> katman basina 1 mm tasma serbest)
    sorun = []
    onceki = None
    n_kat = int((zmax - zmin) // 1.0)
    for kk in range(n_kat):
        z = zmin + 0.5 + kk * 1.0
        try:
            ws = s.slice(V(0, 0, 1), z)
            yuz = Part.makeFace(ws, "Part::FaceMakerBullseye") if ws else None
        except Exception:
            yuz = None
        if yuz is not None and onceki is not None:
            try:
                dest = [f.makeOffset2D(1.0, 0) for f in onceki.Faces]
                dest = dest[0].fuse(dest[1:]) if len(dest) > 1 else dest[0]
                dest.translate(V(0, 0, 1.0))          # onceki katman duzlemi -> bu katman duzlemi (es duzlemde kesim)
                acik = yuz.cut(dest)
            except Exception as e:
                acik = None
                sorun.append(dict(z=round(z - zmin, 1), hata=repr(e)[:80]))
            if acik is not None:
                for f in acik.Faces:
                    if f.Area < 0.5:
                        continue
                    try:
                        dar = f.makeOffset2D(-1.0, 0)
                        dar_alan = sum(g.Area for g in dar.Faces)
                    except Exception:
                        dar_alan = 0.0
                    boy = max(f.BoundBox.XLength, f.BoundBox.YLength)
                    if dar_alan > 0.01 and boy > BRIDGE:
                        sorun.append(dict(z=round(z - zmin, 1), alan=round(f.Area, 1), boy=round(boy, 1)))
        onceki = yuz
    hac = sh.Volume
    kutle = hac / 1000 * A.PETG_RHO * A.KABUK_DOLULUK
    return dict(ad=ad, olcu=[round(en[1], 1), round(en[2], 1), round(zmax - zmin, 1)], tabla_aci=en[0], sigar=bool(sigar),
                sigar_cift=bool(sigar_cift), cikinti_orani=round(oran, 4), cikinti_alan_cm2=round(float(alan[cik].sum()) / 100, 1),
                yuzey_cm2=round(float(alan.sum()) / 100, 1), destek_sorun=sorun[:20], destek_sorun_sayi=len(sorun),
                desteksiz=len(sorun) == 0, hacim_cm3=round(hac / 1000, 1), kutle_g=round(kutle, 0),
                filament_g=round(kutle * 1.05, 0), sure_saat=round(hac * A.KABUK_DOLULUK / A.PETG_HACIM_HIZI / 3600, 1),
                katman=n_kat)


baski = []
for ad, d in K.PARCA.items():
    r = baski_analiz(ad, P[d["indeks"]]["shape"], d["yukari"])
    r["yon"] = d["yon"]
    r["grup"] = d["grup"]
    baski.append(r)
    log("baski %-24s %s sigar=%s cikinti %.3f destek sorunu %d" % (ad, r["olcu"], r["sigar"], r["cikinti_orani"], r["destek_sorun_sayi"]))

# ====================================================================== 7) kutle, agirlik merkezi
M = sum(p["kutle"] for p in P)
CG = V(0, 0, 0)
for p in P:
    CG = CG + p["merkez"] * (p["kutle"] / M)
kutle_grup = {}
for p in P:
    kutle_grup[p["grup"]] = kutle_grup.get(p["grup"], 0.0) + p["kutle"]
kutle_tur = {}
for p in P:
    kutle_tur[p["tur"]] = kutle_tur.get(p["tur"], 0.0) + p["kutle"]
log("kutle %.1f g, AM (%.1f, %.1f, %.1f)" % (M, CG.x, CG.y, CG.z))

# ====================================================================== 8) kaydet: FCStd + STEP + BOM
doc = App.newDocument("KabukMontaj")
kok = doc.addObject("App::Part", "Kabuk")
kok.Label = "Kabuk_V3"
gruplar = {}
for g in sorted(set(p["grup"] for p in P)):
    gp = kok.newObject("App::Part", "G_" + "".join(ch for ch in g.title() if ch.isalnum()))
    gp.Label = g.replace(" ", "_")
    gruplar[g] = gp
BASKI_RENK = {ad: d["renk_baski"] for ad, d in K.PARCA.items()}
for k, p in enumerate(P):
    o = gruplar[p["grup"]].newObject("Part::Feature", "K%03d" % k)
    o.Label = p["ad"]
    o.Shape = p["shape"]
    for prop, val in (("Tur", p["tur"]), ("Malzeme", p["malzeme"]), ("Kod", p["kod"]), ("Renk", p["renk"]), ("Not", p["not_"]),
                      ("BaskiRenk", BASKI_RENK.get(p["ad"], ""))):
        o.addProperty("App::PropertyString", prop, "Robot")
        setattr(o, prop, val)
    o.addProperty("App::PropertyVector", "Patlat", "Robot")
    o.Patlat = V(*p["patlat"])
    o.addProperty("App::PropertyFloat", "Kutle_g", "Robot")
    o.Kutle_g = round(p["kutle"], 1)
doc.recompute()
doc.saveAs(os.path.join(HERE, "kabuk-montaj.FCStd"))
App.closeDocument(doc.Name)
Part.Compound([p["shape"] for p in P]).exportStep(os.path.join(HERE, "kabuk-montaj.step"))
step_kati = len(Part.read(os.path.join(HERE, "kabuk-montaj.step")).Solids)
bom = {}
for p in P:
    key = (p["tur"], p["kod"] if p["tur"] != "Baski" else p["ad"])
    bom.setdefault(key, dict(adet=0, kutle=0.0))
    bom[key]["adet"] += 1
    bom[key]["kutle"] += p["kutle"]
with open(os.path.join(HERE, "kabuk-bom.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Tur", "Kalem", "Adet", "Toplam kutle (g)"])
    for (t, kod), v in sorted(bom.items()):
        w.writerow([t, kod, v["adet"], "%.1f" % v["kutle"]])
log("kayit: STEP kati", step_kati)

# ====================================================================== 9) analiz json
out = dict(
    parca_sayisi=len(P), baski_sayisi=len(K.PARCA),
    gecersiz=gecersiz, coklu_kati=coklu, temizlik=K.TEMIZLIK,
    cakisma=cakisma, cakisma_cift_sayisi=n_cift, tolerans_mm3=TOL,
    iskelet_cakisma=isk_cak, iskelet_cift_sayisi=n_isk,
    bolge=dict(kontrol_edilen=bolge_n, ihlal=bolge_ihlal, en_yakin=bolge_bosluk),
    baglanti=[dict(ad=b["ad"], tip=b["tip"], parca=b["parca"], govde=P[b["govde"]]["ad"], eleman=[P[i]["kod"] for i in b["eleman"]])
              for b in BAG],
    baglanti_kontrol=bag_kontrol, vida_kontrol=vida_kontrol, ekran_kontrol=ekran_kontrol,
    bosluk=dict(teker_etek_mm=round(teker_bosluk, 2), direk_govde_mm=round(direk_bosluk, 2),
                cam_duvar_mm=round(0.106 * math.cos(math.radians(A.GOGUS_EGIM)), 3)),
    baski=baski,
    yazici=dict(A.YAZICI),
    kutle_g=round(M, 1), kutle_grup={k: round(v, 1) for k, v in kutle_grup.items()},
    kutle_tur={k: round(v, 1) for k, v in kutle_tur.items()},
    agirlik_merkezi=[round(CG.x, 2), round(CG.y, 2), round(CG.z, 2)],
    bom=[[t, kod, v["adet"], round(v["kutle"], 1)] for (t, kod), v in sorted(bom.items())],
    step_kati=step_kati,
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "kabuk-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("bitti")
