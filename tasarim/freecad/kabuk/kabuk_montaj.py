# Kabuk modulu (V3) - montaj, kontroller, baski analizi, FCStd + STEP + BOM + analiz json
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
# Kontroller: her parca isValid + tek kati; kabuk ici cakisma (0,5 mm3); kabuk <-> iskelet cakisma; ayrilmis bolgeler;
# iskelete baglanti (braket dayanmasi, cekic somun dudak altinda, M6 civata ucu: somun ustunu >= 0,5 ve kanal tabanina >= 0,5 mm, eksen hizasi, isil gomme somun
# kavrama boyu ve dis yuzeye kalan et); bindirme ve ekran civatalari; her baski parcasi icin yaziciya sigma, baski yonu,
# bindirme boslugu (dil <-> komsu dis yari >= 0,15 mm), 45 derece cikinti orani, katman katman desteksiz basilabilirlik, tahmini kutle / filament / sure.
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
    if z["sahip"] == "kabuk":
        continue          # kabugun kendi braket bolgeleri (icinde kabuk braketleri var; Nextion bolgesi 1,65 m'de yok)
    kb = box(*z["kutu"])
    for c in z["bosluk"]:
        kb = kb.cut(box(*c))
    bolge_n += 1
    en_yakin = (1e9, None)
    for p in P:
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
somun_alti = A.LIP + A.CEKIC_SOMUN["T"]      # cekic somunun kanal icindeki (tabana bakan) yuzu, profil yuzunden (9,3)
# F (14 Ekim 2026): iskelet / taban / omuz ile ayni kalici kural. Vida ucu somun ustunu en az SOMUN_GECME gecmeli (kavrama / uc somundan
# sivisin) ve kanal tabanina en az TABAN_PAY kalmali (uzunluk toleransinda degmesin). Bu kontrol 'degmiyor' ile yetinen eski kontrolun yerine
# gecti: govde braketi M6x16 + pul'da uc tabana 0,4 mm kaliyordu.
SOMUN_GECME = 0.5
TABAN_PAY = 0.5
m6_pay = []          # (braket, delik, uc, somun_pay, taban_pay, ok)
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
        m = b["m6"][i]
        pul, civ, som = (P[m["pul"]] if m["pul"] is not None else None), P[m["civata"]], P[m["somun"]]
        d = mesafe(som["shape"], prof)
        k.append(("M6 cekic somun dudak altina dayali", round(d, 4), d <= TEMAS))
        uc = max((yuz - v.Point).dot(nv) for v in civ["shape"].Vertexes)
        uc_yuzden = uc          # yuz = profil yuzu (direk +-X yuzu / ray ust yuzu): uc zaten profil yuzunden derinlik
        sp, tp = uc_yuzden - somun_alti, A.KANAL_TABAN - uc_yuzden
        k.append(("M6 civata ucu profil yuzunden %.1f mm iceride: somun ustunu %.1f mm geciyor (sart >= %.1f), kanal tabanina %.1f mm (sart >= %.1f)"
                  % (uc_yuzden, sp, SOMUN_GECME, tp, TABAN_PAY), round(uc_yuzden, 3), sp >= SOMUN_GECME - 1e-6 and tp >= TABAN_PAY - 1e-6))
        m6_pay.append(dict(braket=b["ad"], tip=b["tip"], delik=i, uc_mm=round(uc_yuzden, 3), vida=civ["kod"], pul=pul is not None,
                           somun_pay_mm=round(sp, 3), taban_pay_mm=round(tp, 3), tamam=bool(sp >= SOMUN_GECME - 1e-6 and tp >= TABAN_PAY - 1e-6)))
        ed = eksen_disi(som["shape"], yuz, nv)
        k.append(("M6 civata ekseni somun deligi ekseninde", round(ed, 4), ed < 1e-6))
        if pul is not None:
            d = mesafe(pul["shape"], br)
            k.append(("M6 pul brakete dayali", round(d, 4), d <= TEMAS))
        else:
            d = mesafe(civ["shape"], br)
            k.append(("M6 civata (pulsuz) basi brakete dayali", round(d, 4), d <= TEMAS))
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
log("M6 vida payi: %d delik, en az somun gecme %.2f (sart >= %.1f), en az kanal tabani payi %.2f (sart >= %.1f)" % (
    len(m6_pay), min(x["somun_pay_mm"] for x in m6_pay), SOMUN_GECME, min(x["taban_pay_mm"] for x in m6_pay), TABAN_PAY))

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
log("bindirme civatasi tamam %d/%d (Nextion ekrani yok: ekran civatasi kontrolu kaldirildi)" % (
    sum(x["tamam"] for x in vida_kontrol), len(vida_kontrol)))
# S1 kablo kaseti (15 Ekim 2026): kapak havsasindaki M3x8 basi kapaga dayali, isil gomme somun boss'ta oturmus, kavrama >= d ve
# <= isil gomme somun deligi, kaset govdesi (arka plaka) kabuk omuz yuzune oturmus, kapak govdeye oturmus.
kaset_kontrol = []
for v in VIDA:
    if v["tip"] != "kaset":
        continue
    ins, civ = P[v["i_insert"]], P[v["i_vida"]]
    sx = 1 if v["sag"] else -1
    d_bas = mesafe(civ["shape"], PAR[v["kapak"]])
    d_ins = mesafe(ins["shape"], PAR[v["ic"]])
    uc = min(q.Point.x * sx for q in civ["shape"].Vertexes)
    kavrama = v["p_yuz"].x * sx - uc
    d_gov = mesafe(PAR[v["govde"]], PAR[v["ic"]])
    d_kap = mesafe(PAR[v["kapak"]], PAR[v["govde"]])
    ok = d_bas <= TEMAS and d_ins <= TEMAS and 3.0 <= kavrama <= A.INSERT[3][1] + 0.5 and d_gov <= TEMAS and d_kap <= TEMAS
    kaset_kontrol.append(dict(etiket=P[v["i_vida"]]["ad"], parca=v["ic"], bas_dayali=round(d_bas, 4), insert_oturdu=round(d_ins, 4),
                              kavrama=round(kavrama, 2), govde_kabuga=round(d_gov, 4), kapak_govdeye=round(d_kap, 4), tamam=bool(ok)))
log("S1 kaseti civatasi tamam %d/%d" % (sum(x["tamam"] for x in kaset_kontrol), len(kaset_kontrol)), [(x["etiket"], x["kavrama"]) for x in kaset_kontrol])

# ====================================================================== 5) bosluklar (tasarim olculeri)
teker = [z for z in A.BOLGELER if z["ad"].startswith("Teker")]
etek_parca = [ad for ad in K.PARCA if ad.startswith("Etek")]
teker_bosluk = min(PAR[ad].distToShape(box(*z["kutu"]))[0] for ad in etek_parca for z in teker)
govde_parca = [ad for ad in K.PARCA if not ad.startswith("Etek")]
direk_bosluk = min(PAR[ad].distToShape(direk)[0] for ad in govde_parca)
log("teker-etek %.2f mm, direk-govde %.2f mm" % (teker_bosluk, direk_bosluk))

# ====================================================================== 5b) bindirme boslugu (M5, 14 Ekim 2026)
# Dil (bir parcanin ic yarisi) komsunun dis yarisinin arkasina uzanir; arayuz.KABUK_BINDIRME_BOSLUK (0,25 mm) kadar iceri cekilmistir.
# Kontrol: dil <-> komsunun dis yarisi en kisa mesafe >= BINDIRME_BOSLUK_MIN. Iki olcum:
#   duvar  = dil (boss ve delik oncesi sekil) <-> komsu dis yarisi: tasarlanan duvar boslugu (sart bu olcume uygulanir)
#   son    = ayni, boss ve deliklerden sonraki gercek parcalarla: bindirme civatasi bosslari orta yuzeye kadar iner, komsunun
#            dis yarisina dayanir (sikistirma, tasarim geregi) -> 0 beklenir, sart uygulanmaz, bilgi icin.
BINDIRME_BOSLUK_MIN = 0.15
ON_SEKIL = {}
for (bant, sag), sh in K.GOVDE.items():
    ON_SEKIL["Arka servis kapagi" if bant == "kapak" else "%s %s" % (K.GOVDE_AD[bant], "sag" if sag else "sol")] = (sh, K.S_dis)
for (bant, sag), sh in K.ETEK.items():
    ON_SEKIL["%s %s" % (K.ETEK_AD[bant], "sag" if sag else "sol")] = (sh, K.Se_dis)
for yer, sh in K.ETEK_DOLGU.items():
    ON_SEKIL["Etek dolgu seridi %s" % yer] = (sh, K.Se_dis)
dis_yari = {}
bindirme_bosluk = []
for ad_b, (_, s_dis) in ON_SEKIL.items():
    dis_yari[ad_b] = s_dis.common(K.DIS_HUCRE[ad_b])
for ad_a, (sh_a, _) in ON_SEKIL.items():
    for ad_b in ON_SEKIL:
        if ad_a == ad_b or not ON_SEKIL[ad_a][1] is ON_SEKIL[ad_b][1]:
            continue            # govde ve etek ayri zarflar
        bb = App.BoundBox(PAR[ad_b].BoundBox)
        bb.enlarge(0.5)
        if not PAR[ad_a].BoundBox.intersect(bb):
            continue
        dil = sh_a.common(K.DIS_HUCRE[ad_b])
        if dil.Volume < 1.0:
            continue            # bu komsuya dil yok (alin birlesim)
        d_duvar = dil.distToShape(dis_yari[ad_b])[0]
        d_son = PAR[ad_a].common(K.DIS_HUCRE[ad_b]).distToShape(dis_yari[ad_b])[0]
        bindirme_bosluk.append(dict(dil=ad_a, komsu=ad_b, dil_hacim_mm3=round(dil.Volume, 0), duvar_bosluk_mm=round(d_duvar, 4),
                                    son_bosluk_mm=round(d_son, 4), tamam=d_duvar >= BINDIRME_BOSLUK_MIN - 1e-6))
bindirme_en_az = min(b["duvar_bosluk_mm"] for b in bindirme_bosluk) if bindirme_bosluk else None
log("bindirme boslugu: %d dil-komsu cifti, en kucuk duvar boslugu %s mm (sart >= %.2f), %d ihlal" % (
    len(bindirme_bosluk), bindirme_en_az, BINDIRME_BOSLUK_MIN, sum(1 for b in bindirme_bosluk if not b["tamam"])))
for b in bindirme_bosluk:
    log("  %s -> %s: duvar %.4f, boss dahil %.4f %s" % (b["dil"], b["komsu"], b["duvar_bosluk_mm"], b["son_bosluk_mm"], "" if b["tamam"] else "IHLAL"))

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
    TO = A.YAZICI_OKUL["tabla"]                 # okul yazicisi 250 x 250 x 250 (1,65 m, Y2a)
    sigar_okul = en[1] <= TO[0] and en[2] <= TO[1] and (zmax - zmin) <= TO[2]
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
            acik, hata = None, None
            # Y2a (29 Ekim 2026): OCC makeOffset2D bazen tek katmanda "result of offsetting is null" veriyor (1650'de orta bant sag
            # z 220,5; ayni geometri 1700'de gecti). Hesap hatasi destek sorunu sayilmasin diye ofset 0,98 / 1,02 ile yeniden denenir;
            # yine olmazsa sorun olarak kalir.
            for _of in (1.0, 0.98, 1.02):
                try:
                    dest = []
                    for f in onceki.Faces:              # yuz basina; ofseti kurulamayan yuz ofsetsiz (daha tutucu; kafa_lib ile ayni)
                        try:
                            dest.append(f.makeOffset2D(_of, 0))
                        except Exception:
                            dest.append(f)
                    dest = dest[0].fuse(dest[1:]) if len(dest) > 1 else dest[0]
                    dest.translate(V(0, 0, 1.0))          # onceki katman duzlemi -> bu katman duzlemi (es duzlemde kesim)
                    acik = yuz.cut(dest)
                    if _of != 1.0:
                        log("baski %s z %.1f: ofset 1,0 hata verdi, %.2f ile hesaplandi" % (ad, z - zmin, _of))
                    break
                except Exception as e:
                    hata = e
            if acik is None:
                sorun.append(dict(z=round(z - zmin, 1), hata=repr(hata)[:80]))
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
                sigar_cift=bool(sigar_cift), sigar_okul=bool(sigar_okul), cikinti_orani=round(oran, 4), cikinti_alan_cm2=round(float(alan[cik].sum()) / 100, 1),
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
    baglanti_kontrol=bag_kontrol, m6_vida_pay=dict(sart_somun_gecme_mm=SOMUN_GECME, sart_taban_pay_mm=TABAN_PAY, somun_ustu_mm=somun_alti,
                                                  kanal_tabani_mm=A.KANAL_TABAN, kalemler=m6_pay), vida_kontrol=vida_kontrol, kaset_kontrol=kaset_kontrol,
    s1_kaset=dict(K.S1_KASET, dikme=[[d[0], d[1]] for d in K.S1_KASET['dikme']], kaynak='arayuz.KOL_KABLO s1'),
    bosluk=dict(teker_etek_mm=round(teker_bosluk, 2), direk_govde_mm=round(direk_bosluk, 2)),
    bindirme_bosluk=dict(sart_min_mm=BINDIRME_BOSLUK_MIN, tasarim_mm=A.KABUK_BINDIRME_BOSLUK, en_az_mm=bindirme_en_az,
                         ihlal=[b for b in bindirme_bosluk if not b['tamam']], ciftler=bindirme_bosluk),
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
