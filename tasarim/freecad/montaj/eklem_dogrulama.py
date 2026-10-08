# Ana montaj eklem dogrulamasi (FreeCAD 1.1, arayuzsuz). robot-montaj.FCStd'yi acar, her kolun doner eklemlerini (omuz
# one-arka + yana acma, dirsek, bilek) Assembly simulasyonuyla (Create Simulation'in kullandigi generateSimulation + Motion)
# birkac aciya surer ve cozucunun verdigi grup konumlarini modulun kendi kinematigiyle (omuz_parcalar Pp/Pr,
# dirsek_parcalar grup_yer; moduller.beklenen) karsilastirir. Dirsek gruplari omuz zincirine bagli: beklenen poz omuz
# acilarini da alir (moduller ust_kol).
# Revolute acisi dogrudan surulemedigi icin (Angle ozelligi yalniz Angle ekleminde) surus Motion ile yapilir.
# Calistir: FC_SCRIPT=<bu dosya> freecadcmd run_fc.py  -> eklem-dogrulama.json (dosya kaydedilmez)
import os, sys, json, time, math
import FreeCAD as App

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import moduller as MD
from moduller import V

t0 = time.time()
ADIM = 0.02      # s, simulasyon cikti adimi (sure 1 s; formul = aci * time)


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))


MOD = {ad: MD.yukle(ad) for ad in MD.SIRA}
doc = App.openDocument(os.path.join(HERE, "robot-montaj.FCStd"))
asm = doc.getObject("Assembly")
GR = {o.Name: o for o in asm.Group if o.TypeId == "App::Part"}
EK = {o.Name: o for o in doc.Objects if getattr(o, "JointType", None) == "Revolute"}
log("gruplar", sorted(GR), "doner eklemler", sorted(EK))

# her grubun ornek noktalari: ev pozundaki sinir kutusu koseleri (global)
NOKTA = {}
for ad, gp in GR.items():
    bb = None
    for o in gp.OutListRecursive:
        if o.TypeId == "Part::Feature":
            if bb is None:
                bb = App.BoundBox(o.Shape.BoundBox)
            else:
                bb.add(o.Shape.BoundBox)
    NOKTA[ad] = [V(x, y, z) for x in (bb.XMin, bb.XMax) for y in (bb.YMin, bb.YMax) for z in (bb.ZMin, bb.ZMax)]

# kol (modul) -> {eklem anahtari: eklem nesnesi}, {grup adi: grup nesne adi}
KOL = {}
for ad, d in MOD.items():
    if not d["eklemler"]:
        continue
    KOL[ad] = dict(eklem={e["anahtar"]: EK["%s_%s" % (d["on_ek"], "".join(s.capitalize() for s in e["anahtar"].split("_")))]
                          for e in d["eklemler"]},
                   grup={g: ("%s_%s" % (d["on_ek"], g)) for g, _ in d["gruplar"]},
                   sinir={e["anahtar"]: e["sinir"] for e in d["eklemler"]})

# ---------------------------------------------------------------------- simulasyon nesneleri (bellekte, kaydedilmez)
# CommandCreateSimulation arayuzsuz import edilemiyor (QtCore); C++ cozucu yalniz ozellikleri okur, burada elle kurulur.
sg = asm.newObject("Assembly::SimulationGroup", "Simulations_dogrulama")
sim = sg.newObject("App::FeaturePython", "Simulation_dogrulama")
sim.addExtension("App::GroupExtensionPython")
for n, t, v in (("aTimeStart", "App::PropertyTime", 0.0), ("bTimeEnd", "App::PropertyTime", 1.0),
                ("cTimeStepOutput", "App::PropertyTime", ADIM), ("fGlobalErrorTolerance", "App::PropertyFloat", 1e-6),
                ("jFramesPerSecond", "App::PropertyInteger", 30)):
    sim.addProperty(t, n, "Simulation")
    setattr(sim, n, v)
MOT = {}
for kol, k in KOL.items():
    for anah, j in k["eklem"].items():
        m = asm.newObject("App::FeaturePython", "Motion_" + j.Name)
        m.addProperty("App::PropertyXLinkSubHidden", "Joint", "Motion")
        m.addProperty("App::PropertyString", "Formula", "Motion")
        m.addProperty("App::PropertyEnumeration", "MotionType", "Motion")
        m.MotionType = ["Angular", "Linear"]
        m.MotionType = "Angular"
        m.Joint = j
        m.Formula = "0*time"
        MOT[(kol, anah)] = m
sim.Group = list(MOT.values())


def sifirla():
    for gp in GR.values():
        gp.Placement = App.Placement()


def beklenen(kol, poz, g):
    d = MOD[kol]
    return MD.global_poz(kol, d["beklenen"](poz, g))


def poz_al(kol, komut, t=1.0):
    """Kolun beklenen pozu icin eklem acilari: kendi eklemleri + zincirde ust modulun (dirsek -> omuz) eklemleri."""
    poz = {}
    ust = MOD[kol].get("ust_kol")
    if ust:
        poz.update({an: komut.get(ust, {}).get(an, 0.0) * t for an in KOL[ust]["eklem"]})
    poz.update({an: komut.get(kol, {}).get(an, 0.0) * t for an in KOL[kol]["eklem"]})
    return poz


EKLEM_GRUP = {"one_arka": "Gobek", "yana": "Kol", "dirsek": "OnKol", "bilek": "El"}   # eklemin dondurdugu grup


def sapma(gad, A_, E_):
    mm = max((A_.multVec(p) - E_.multVec(p)).Length for p in NOKTA[gad])
    return mm, rot_aci(E_.inverse().multiply(A_).Rotation)


def rot_aci(r):
    """Donus acisi (derece), kucuk acilarda hassas: 2 atan2(|q_xyz|, |q_w|)."""
    x, y, z, w = r.Q
    return math.degrees(2 * math.atan2(math.sqrt(x * x + y * y + z * z), abs(w)))


def sar(a):
    """Aciyi (-180, 180] araligina getirir."""
    a = math.fmod(a, 360.0)
    if a > 180.0:
        a -= 360.0
    if a <= -180.0:
        a += 360.0
    return a


def olculen_aci(j):
    """Cozucu sonrasi eklem acisi: ust ve alt grubun eklem cercevesindeki goreli donusu (cerceve Z etrafinda, isaretli)."""
    F = App.Placement(j.Placement1)
    ust, alt = j.Reference1[0], j.Reference2[0]
    rel = ust.Placement.multiply(F).inverse().multiply(alt.Placement.multiply(F))
    r = rel.Rotation
    a = sar(math.degrees(r.Angle) * (1 if r.Axis.z >= 0 else -1))
    egik = math.degrees(math.acos(max(-1.0, min(1.0, abs(r.Axis.z))))) if rot_aci(r) > 1e-6 else 0.0
    return a, rel.Base.Length, egik


def calistir(komut):
    """komut: {kol: {anahtar: derece}}. Surulmeyen eklemler 0'da tutulur. Doner: kare listesi."""
    sifirla()
    for (kol, anah), m in MOT.items():
        a = komut.get(kol, {}).get(anah, 0.0)
        m.Formula = "%.12f*time" % math.radians(a)
    asm.generateSimulation(sim)
    n = asm.numberOfFrames()
    kareler = []
    for k in range(n):
        asm.updateForFrame(k)
        t = max(0, k - 1) * ADIM          # kare 0 = baslangic montaji, kare k>=1 -> t = (k-1)*adim (probe ile olculdu)
        kare = dict(k=k, t=t, gruplar={}, aci={})
        for kol, kk in KOL.items():
            poz = poz_al(kol, komut, t)
            for g, gad in kk["grup"].items():
                kare["gruplar"][gad] = sapma(gad, GR[gad].Placement, beklenen(kol, poz, g))
            for an, j in kk["eklem"].items():
                kare["aci"][j.Name] = (poz[an],) + olculen_aci(j)
        for gad in GR:
            if gad not in kare["gruplar"]:
                kare["gruplar"][gad] = sapma(gad, GR[gad].Placement, App.Placement())
        kareler.append(kare)
    return kareler


def ozetle(ad, komut, kareler):
    son = kareler[-1]
    mx_mm = max(v[0] for k in kareler for v in k["gruplar"].values())
    mx_dg = max(v[1] for k in kareler for v in k["gruplar"].values())
    aci_hata = max(abs(sar(v[0] - v[1])) for k in kareler for v in k["aci"].values())
    sinir_ici = all(KOL[kol]["sinir"][an][0] <= a <= KOL[kol]["sinir"][an][1] for kol, c in komut.items() for an, a in c.items())
    r = dict(ad=ad, komut=komut, sinir_ici=sinir_ici, kare=len(kareler), t_son=son["t"],
             son={g: [round(v[0], 6), round(v[1], 6)] for g, v in son["gruplar"].items()},
             son_aci={j: [round(v[0], 4), round(v[1], 4), round(v[2], 6), round(v[3], 6)] for j, v in son["aci"].items()},
             max_mm=mx_mm, max_derece=mx_dg, max_aci_hatasi=aci_hata)
    log("%-34s kare %d  max sapma %.2e mm %.2e der  aci hatasi %.2e der  %s" % (
        ad, len(kareler), mx_mm, mx_dg, aci_hata, "" if sinir_ici else "(SINIR DISI)"))
    return r


# ---------------------------------------------------------------------- 1) birim ve isaret: 1 rad -> 57.296 derece mi
kar = calistir({"omuz_sag": {"one_arka": math.degrees(1.0)}})
birim = dict(formul="57.29578*time (= 1 rad)", olculen_derece=round(kar[-1]["aci"][KOL["omuz_sag"]["eklem"]["one_arka"].Name][1], 6),
             kare_sayisi=len(kar), not_="Motion formulu radyan; pozitif aci eklem cercevesinin Z ekseni etrafinda sag el kurali")
log("birim testi: 1 rad ->", birim["olculen_derece"], "derece")

# ---------------------------------------------------------------------- 2) her kol ayri, sinir ici pozlar
POZ = [(30, 0), (90, 0), (135, 0), (-45, 0), (0, 60), (0, 120), (90, 90), (-30, 45), (60, 30), (135, 120)]
vakalar = []
for kol in [k for k in KOL if not MOD[k].get("ust_kol")]:
    for phi, th in POZ:
        komut = {kol: {"one_arka": float(phi), "yana": float(th)}}
        vakalar.append(ozetle("%s one %d yana %d" % (kol, phi, th), komut, calistir(komut)))
# dirsek ve bilek (omuz pozuyla birlikte): (one-arka, yana, dirsek, bilek)
DPOZ = [(0, 0, 30, 0), (0, 0, 60, 45), (0, 0, 105, -90), (0, 0, 90, 90), (90, 0, 90, 45), (45, 60, 60, -45),
        (135, 120, 105, 90), (-45, 30, 0, -90), (60, 30, 45, 30), (90, 90, 105, -60)]
for taraf in ("sag", "sol"):
    om, dr = "omuz_" + taraf, "dirsek_" + taraf
    if dr not in KOL:
        continue
    for phi, th, al, be in DPOZ:
        komut = {om: {"one_arka": float(phi), "yana": float(th)}, dr: {"dirsek": float(al), "bilek": float(be)}}
        vakalar.append(ozetle("%s one %d yana %d dirsek %d bilek %d" % (taraf, phi, th, al, be), komut, calistir(komut)))
# iki kol birlikte
for (a, b) in (((90, 45, 0, 0), (90, 45, 0, 0)), ((120, 30, 0, 0), (-30, 90, 0, 0)), ((90, 0, 60, 45), (90, 0, 60, -45)),
               ((30, 20, 105, 90), (-30, 40, 30, -90))):
    komut = {"omuz_sag": {"one_arka": float(a[0]), "yana": float(a[1])}, "omuz_sol": {"one_arka": float(b[0]), "yana": float(b[1])}}
    if "dirsek_sag" in KOL and (a[2] or a[3] or b[2] or b[3]):
        komut["dirsek_sag"] = {"dirsek": float(a[2]), "bilek": float(a[3])}
        komut["dirsek_sol"] = {"dirsek": float(b[2]), "bilek": float(b[3])}
    vakalar.append(ozetle("iki kol sag %s sol %s" % (a, b), komut, calistir(komut)))

# ---------------------------------------------------------------------- 3) sinir disi surus
SINIR_DISI = [(160, 0), (180, 0), (-60, 0), (0, 140), (0, -15)]
sinir_disi = []
for kol in KOL:
    if MOD[kol].get("ust_kol"):
        for al, be in ((120, 0), (-20, 0), (0, 120)):
            komut = {kol: {"dirsek": float(al), "bilek": float(be)}}
            sinir_disi.append(ozetle("%s dirsek %d bilek %d" % (kol, al, be), komut, calistir(komut)))
        continue
    for phi, th in SINIR_DISI:
        komut = {kol: {"one_arka": float(phi), "yana": float(th)}}
        sinir_disi.append(ozetle("%s one %d yana %d" % (kol, phi, th), komut, calistir(komut)))

# ---------------------------------------------------------------------- 3b) yon kontrolu: cozucu sonrasi kol ucunun gittigi yer
# one-arka +90: kol ucu (ust kol tupunun alt ucu) her iki kolda +Z'ye; yana +90: sagda +X'e, solda -X'e
yon = []
for kol in [k for k in KOL if not MOD[k].get("ust_kol")]:
    gad = KOL[kol]["grup"]["Kol"]
    uc0 = min(NOKTA[gad], key=lambda p: p.y)
    uc0 = V(sum(p.x for p in NOKTA[gad]) / 8, uc0.y, sum(p.z for p in NOKTA[gad]) / 8)    # tup ekseni alt ucu (yaklasik)
    for an, a in (("one_arka", 90.0), ("yana", 90.0)):
        calistir({kol: {an: a}})
        uc = GR[gad].Placement.multVec(uc0)
        d = uc - uc0
        if an == "one_arka":
            ok = d.z > 0 and uc.z > 50
        else:
            ok = (uc.x > uc0.x + 50) if MOD[kol]["taraf"] == "sag" else (uc.x < uc0.x - 50)
        yon.append(dict(kol=kol, eklem=an, aci=a, uc_once=[round(x, 1) for x in uc0], uc_sonra=[round(x, 1) for x in uc], dogru=ok))
        log("yon %s %s +%d: kol ucu (%.0f, %.0f, %.0f) -> (%.0f, %.0f, %.0f) %s" % (kol, an, a, uc0.x, uc0.y, uc0.z, uc.x, uc.y, uc.z,
                                                                                    "dogru" if ok else "YANLIS"))

# dirsek +90: el ucu one (+Z) gelir; bilek +90: parmak (avucun ic tarafi, ev pozunda iceri bakar) one (+Z) doner; iki kolda da
import dirsek_parcalar as DP
for kol in [k for k in KOL if MOD[k].get("ust_kol")]:
    uc_y = MD.global_nokta(kol, DP.D["el_ucu"])
    parmak = MD.global_nokta(kol, (DP.XW - 21.0, DP.Y(DP.S_UC - 18.0), DP.ZE))
    for an, a, p0 in (("dirsek", 90.0, uc_y), ("bilek", 90.0, parmak)):
        calistir({kol: {an: a}})
        uc = GR[KOL[kol]["grup"]["El"]].Placement.multVec(p0)
        d = uc - p0
        ok = (d.z > 100 and abs(d.x) < 1e-6) if an == "dirsek" else (d.z > 15 and abs(d.y) < 1e-6)
        yon.append(dict(kol=kol, eklem=an, aci=a, uc_once=[round(x, 1) for x in p0], uc_sonra=[round(x, 1) for x in uc], dogru=ok))
        log("yon %s %s +%d: nokta (%.0f, %.0f, %.0f) -> (%.0f, %.0f, %.0f) %s" % (kol, an, a, p0.x, p0.y, p0.z, uc.x, uc.y, uc.z,
                                                                               "dogru" if ok else "YANLIS"))

# ---------------------------------------------------------------------- 4) solve(): elle verilen pozu koruyor mu, sinirda geri cekiyor mu
# (GUI'de surukleme ve doc.recompute() bu cozucuyu cagirir)
solve_test = []
for kol in KOL:
    ust = MOD[kol].get("ust_kol")
    pozlar = ([dict(dirsek=60.0, bilek=45.0), dict(dirsek=125.0, bilek=0.0), dict(dirsek=30.0, bilek=-110.0)] if ust else
              [dict(one_arka=float(a), yana=float(b)) for a, b in ((90, 45), (160, 0), (0, 140), (-60, 0))])
    alt = [k for k in KOL if MOD[k].get("ust_kol") == kol]      # zincirdeki alt moduller (omuz -> dirsek) birlikte tasinir
    for poz in pozlar:
        sifirla()
        for k in [kol] + alt:
            for g, gad in KOL[k]["grup"].items():
                GR[gad].Placement = beklenen(k, poz, g)
        r = asm.solve()
        olc = {an: round(olculen_aci(j)[0], 4) for an, j in KOL[kol]["eklem"].items()}
        mx = max(sapma(gad, GR[gad].Placement, beklenen(k, poz, g))[0] for k in [kol] + alt for g, gad in KOL[k]["grup"].items())
        sinir_ici = all(KOL[kol]["sinir"][an][0] <= a <= KOL[kol]["sinir"][an][1] for an, a in poz.items())
        solve_test.append(dict(kol=kol, poz=poz, sinir_ici=sinir_ici, solve=r, olculen=olc, max_mm=mx))
        log("solve %s %s -> donus %d, olculen %s, sapma %.2e mm" % (kol, poz, r, olc, mx))
sifirla()

# ---------------------------------------------------------------------- ozet: eklem basina en buyuk sapma (sinir ici vakalar)
ozet = {}
for kol, kk in KOL.items():
    for an, j in kk["eklem"].items():
        ilgili = [v for v in vakalar if kol in v["komut"]]
        gad = kk["grup"][EKLEM_GRUP[an]]
        ozet[j.Name] = dict(kol=kol, anahtar=an, etiket=j.Label, vaka=len(ilgili),
                            grup=gad, max_mm=max(v["max_mm"] for v in ilgili), max_derece=max(v["max_derece"] for v in ilgili),
                            max_aci_hatasi=max(v["max_aci_hatasi"] for v in ilgili),
                            sinir=[float(j.AngleMin), float(j.AngleMax)],
                            eksen=list(App.Placement(j.Placement1).Rotation.multVec(V(0, 0, 1))),
                            nokta=list(App.Placement(j.Placement1).Base))
out = dict(yontem="Assembly simulasyonu: her eklemde Motion (Angular, formul = aci_rad * time), 0...1 s, adim %.2f s; "
                  "her karede cozucunun grup yerlesimi omuz_parcalar Pp/Pr ve dirsek_parcalar grup_yer (moduller.beklenen, solda X aynasiyla; "
                  "dirsek gruplari omuz acilariyla birlikte) ile karsilastirildi. "
                  "Sapma: grubun sinir kutusu kosesindeki en buyuk konum farki (mm) ve donus farki (derece)." % ADIM,
           birim=birim, yon=yon, vakalar=vakalar, sinir_disi=sinir_disi, solve_testi=solve_test, ozet=ozet,
           sure_s=round(time.time() - t0, 1))
json.dump(out, open(os.path.join(HERE, "eklem-dogrulama.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
App.closeDocument(doc.Name)
log("bitti; sinir ici en buyuk sapma %.2e mm / %.2e derece" % (max(v["max_mm"] for v in vakalar), max(v["max_derece"] for v in vakalar)))
