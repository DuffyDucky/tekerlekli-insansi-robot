# Robot ana montaji (FreeCAD 1.1 Assembly): iskelet + sag/sol omuz + kabuk + sag/sol dirsek + kafa + taban (sol = gercek aynali geometri).
# Moduller ve yukleyiciler moduller.py'de; yerlesim yalniz arayuz.MODULLER'den. Eklemler: zemine sabit iskelet,
# her omuz govdesi ve kabuk iskelete Fixed, her omuzda 2 Revolute (omuz/omuz-montaj.FCStd'den, solda aynali), her dirsek
# catali omuzun Kol grubuna Fixed, her kolda dirsek + bilek Revolute (dirsek/dirsek-montaj.FCStd'den, solda aynali);
# kafa govdesi traverse Fixed, pan (govde -> boyun) ve tilt (boyun -> bas) Revolute (kafa/kafa-montaj.FCStd'den); taban govdesi
# iskelete Fixed, 4 teker grubu (teker + kaplin) taban govdesine sinirsiz Revolute (motor mili ekseni, moduller.yukle_taban).
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py
#   -> robot-montaj.FCStd, robot-montaj.step, montaj-analiz.json
# Not: betikle kaydedilen dosyada eklemlerin gorunum nesnesi yok; montaj_gorsel.py (GUI) bunlari kurup dosyayi yeniden kaydeder.
import os, sys, json, time, math
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import moduller as MD
from moduller import V, A

t0 = time.time()
DOSYA = os.path.join(HERE, "robot-montaj.FCStd")


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0))


# ====================================================================== 1) modulleri yukle, global geometri
MOD = []
for ad in MD.SIRA:
    d = MD.yukle(ad)
    for p in d["parcalar"]:
        if p["haric"]:
            continue
        g = MD.global_sekil(p["shape"], ad)
        p["g"] = g
        p["gmerkez"] = MD.global_nokta(ad, p["merkez"])
        p["gecerli"] = g.isValid() and len(g.Solids) == len(p["shape"].Solids)
        p["hacim_fark"] = abs(g.Volume - p["shape"].Volume)
    MOD.append(d)
    log("modul", ad, "parca", sum(1 for p in d["parcalar"] if not p["haric"]), "haric", sum(p["haric"] for p in d["parcalar"]),
        "ayna" if d["aynali"] else "")

parcalar = [(d, p) for d in MOD for p in d["parcalar"] if not p["haric"]]
gecersiz = [p["ad"] for _, p in parcalar if not p["gecerli"]]
hacim_fark = max(p["hacim_fark"] for _, p in parcalar)
# aynali parcada kutle merkezi: yerel merkezin aynasi = aynali seklin kendi kutle merkezi olmali (geometri gercekten aynali mi)
ayna_merkez_fark = 0.0
for d, p in parcalar:
    if d["aynali"] and p["g"].Solids:
        vt = sum(s.Volume for s in p["g"].Solids)
        c = V(0, 0, 0)
        for s in p["g"].Solids:
            c = c + s.CenterOfMass * (s.Volume / vt)
        ayna_merkez_fark = max(ayna_merkez_fark, (c - p["gmerkez"]).Length)
log("gecersiz", len(gecersiz), "hacim farki %.2e mm3" % hacim_fark, "ayna merkez farki %.2e mm" % ayna_merkez_fark)


def kutle_am(sec):
    m = sum(p["kutle"] for _, p in sec)
    c = V(0, 0, 0)
    for _, p in sec:
        c = c + p["gmerkez"] * (p["kutle"] / m)
    return m, c


# ====================================================================== 2) FreeCAD Assembly
doc = App.newDocument("RobotMontaj")
asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
asm.Label = "Robot"
jg = asm.newObject("Assembly::JointGroup", "Joints")
jg.Label = "Eklemler"
GRUP = {}            # (modul, grup) -> App::Part
FEAT = {}            # (modul, grup) -> [Part::Feature]
for d in MOD:
    for g, et in d["gruplar"]:
        isim = d["on_ek"] if g == d["gruplar"][0][0] and len(d["gruplar"]) == 1 else "%s_%s" % (d["on_ek"], g)
        gp = asm.newObject("App::Part", isim)
        gp.Label = ("%s %s - %s" % (d["ad"].split("_")[0].capitalize(), d["taraf"], et)) if d["taraf"] else et.capitalize()
        gp.addProperty("App::PropertyString", "Modul", "Robot")
        gp.Modul = d["ad"]
        GRUP[(d["ad"], g)] = gp
        FEAT[(d["ad"], g)] = []
for d, p in parcalar:
    o = GRUP[(d["ad"], p["grup"])].newObject("Part::Feature", "%s_P%03d" % (d["on_ek"], p["indeks"]))
    o.Label = p["ad"] + (" (%s)" % d["taraf"] if d["taraf"] else "")
    o.Shape = p["g"]
    pat = V(*p["patlat"])
    if d["aynali"]:
        pat.x = -pat.x
    for prop, val in (("Modul", d["ad"]), ("Taraf", d["taraf"] or "orta"), ("Grup", p.get("alt_grup", p["grup"])),
                      ("Tur", p["tur"]), ("Malzeme", p["malzeme"]), ("Kod", p["kod"]), ("Renk", p["renk"]), ("Not", p["not_"])):
        o.addProperty("App::PropertyString", prop, "Robot")
        setattr(o, prop, val)
    o.addProperty("App::PropertyBool", "Aynali", "Robot")
    o.Aynali = d["aynali"]
    o.addProperty("App::PropertyInteger", "ModulIndeks", "Robot")
    o.ModulIndeks = p["indeks"]
    o.addProperty("App::PropertyFloat", "Kutle_g", "Robot")
    o.Kutle_g = p["kutle"]
    o.addProperty("App::PropertyVector", "Patlat", "Robot")
    o.Patlat = pat
    FEAT[(d["ad"], p["grup"])].append((o, p))
doc.recompute()
log("nesneler kuruldu:", len(parcalar), "parca,", len(GRUP), "grup")

import JointObject


def ref_nesne(modul, grup, onek=None):
    fl = FEAT[(modul, grup)]
    if onek:
        return next(o for o, p in fl if p["ad"].startswith(onek))
    return next((o for o, p in fl if p["tur"] == "Baski"), fl[0][0])


def eklem(isim, etiket, tip, ust, alt, ust_ref, alt_ref, cerceve, sinir=None):
    j = jg.newObject("App::FeaturePython", isim)
    JointObject.Joint(j, tip)
    j.Label = etiket
    j.Reference1 = [ust, [ust_ref.Name + ".Face1", ust_ref.Name + ".Vertex1"]]
    j.Reference2 = [alt, [alt_ref.Name + ".Face1", alt_ref.Name + ".Vertex1"]]
    j.Detach1 = True
    j.Detach2 = True
    j.Placement1 = cerceve      # gruplar ev pozunda kimlik yerlesimde: global = grup yerel
    j.Placement2 = cerceve
    if sinir:
        j.EnableAngleMin = True
        j.AngleMin = sinir[0]
        j.EnableAngleMax = True
        j.AngleMax = sinir[1]
    return j


EKLEM = []
for d in MOD:
    govde = d["gruplar"][0][0]
    if d["baglanti"] is None:
        gj = jg.newObject("App::FeaturePython", "Sabit_" + d["on_ek"])
        JointObject.GroundedJoint(gj, GRUP[(d["ad"], govde)])
        gj.Label = "%s zemine sabit" % d["on_ek"]
        EKLEM.append(dict(isim=gj.Name, etiket=gj.Label, tip="Grounded", modul=d["ad"], ust="-", alt=GRUP[(d["ad"], govde)].Name))
    else:
        b = d["baglanti"]
        cer = App.Placement(MD.global_nokta(d["ad"], b["nokta"]), App.Rotation())
        j = eklem("Sabit_" + d["on_ek"], "%s %s -> %s (sabit)" % (d["on_ek"], govde, b["modul"]), 0,
                  GRUP[(b["modul"], b["grup"])], GRUP[(d["ad"], govde)], ref_nesne(b["modul"], b["grup"], b["ref"]),
                  ref_nesne(d["ad"], govde), cer)
        EKLEM.append(dict(isim=j.Name, etiket=j.Label, tip="Fixed", modul=d["ad"], ust=GRUP[(b["modul"], b["grup"])].Name,
                          alt=GRUP[(d["ad"], govde)].Name, nokta=list(cer.Base), aciklama=b["aciklama"]))
    for e in d["eklemler"]:
        cer = MD.global_cerceve(d["ad"], e["cerceve"])
        ust, alt = GRUP[(d["ad"], e["ebeveyn"])], GRUP[(d["ad"], e["cocuk"])]
        isim = "%s_%s" % (d["on_ek"], "".join(s.capitalize() for s in e["anahtar"].split("_")))
        j = eklem(isim, "%s %s" % (d["on_ek"], e["ad"]), 1, ust, alt, ref_nesne(d["ad"], e["ebeveyn"]),
                  ref_nesne(d["ad"], e["cocuk"]), cer, e["sinir"])
        ax = cer.Rotation.multVec(V(0, 0, 1))
        EKLEM.append(dict(isim=j.Name, etiket=j.Label, tip="Revolute", modul=d["ad"], anahtar=e["anahtar"], ad=e["ad"],
                          ust=ust.Name, alt=alt.Name, nokta=[round(x, 4) for x in cer.Base], eksen=[round(x, 6) for x in ax],
                          yerel_nokta=[round(x, 4) for x in e["cerceve"].Base],
                          yerel_eksen=[round(x, 6) for x in e["cerceve"].Rotation.multVec(V(0, 0, 1))],
                          sinir=list(e["sinir"]) if e["sinir"] else None, kaynak=e["kaynak"]))
r_solve = asm.solve()
doc.recompute()
# ev pozunda cozucu gruplari yerinde birakmali (eklem cerceveleri tutarli)
ev_sapma = max(max(gp.Placement.Base.Length, math.degrees(gp.Placement.Rotation.Angle)) for gp in GRUP.values())
log("eklem", len(EKLEM), "solve", r_solve, "ev pozu cozucu sapmasi %.2e" % ev_sapma)
for gp in GRUP.values():
    gp.Placement = App.Placement()
doc.recompute()
doc.saveAs(DOSYA)

# STEP: gruplar ad ve hiyerarsiyle (Import), geri okuma testi
import Import
STEP = os.path.join(HERE, "robot-montaj.step")
Import.export(list(GRUP.values()), STEP)
step_kati = len(Part.read(STEP).Solids)
log("STEP kati", step_kati)
GRUP_AD = {k: gp.Name for k, gp in GRUP.items()}
App.closeDocument(doc.Name)

# ====================================================================== 3) dosyadan geri oku: parca, kutle, AM
doc = App.openDocument(DOSYA)
feats = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
m_dosya = sum(o.Kutle_g for o in feats)
c_dosya = V(0, 0, 0)
for o in feats:
    sl = o.Shape.Solids
    if o.Kutle_g <= 0 or not sl:
        continue
    vt = sum(s.Volume for s in sl)
    c = V(0, 0, 0)
    for s in sl:
        c = c + s.CenterOfMass * (s.Volume / vt)
    # o.Shape kendi Placement'ini (o.Placement) zaten tasiyor (kafa parcalarinda kimlik degil): yalniz ust grubun yerlesimi uygulanir
    c_dosya = c_dosya + o.getGlobalPlacement().multiply(o.Placement.inverse()).multVec(c) * (o.Kutle_g / m_dosya)
dosya_eklem = [o.Name for o in doc.Objects if hasattr(o, "JointType") or o.Name.startswith("Sabit_")]
App.closeDocument(doc.Name)
log("dosyadan: parca %d, kutle %.1f g, AM (%.2f, %.2f, %.2f)" % (len(feats), m_dosya, c_dosya.x, c_dosya.y, c_dosya.z))

# ====================================================================== 4) modul toplamlariyla karsilastirma
UST = MD.UST
isk = json.load(open(os.path.join(UST, "iskelet", "iskelet-analiz.json"), encoding="utf-8"))
crp = json.load(open(os.path.join(UST, "carpisma-sonuc.json"), encoding="utf-8"))
omz = json.load(open(os.path.join(UST, "omuz", "omuz-analiz.json"), encoding="utf-8"))
mod_ozet = []
for d in MOD:
    sec = [(d, p) for p in d["parcalar"] if not p["haric"]]
    m, c = kutle_am(sec)
    mod_ozet.append(dict(ad=d["ad"], konum=list(A.MODULLER[d["ad"]]["konum"]), ayna=d["aynali"], not_=A.MODULLER[d["ad"]]["not_"],
                         parca_modulde=len(d["parcalar"]), parca=len(sec), haric=[p["ad"] for p in d["parcalar"] if p["haric"]],
                         haric_neden=d["haric_neden"], kutle_g=round(m, 2), agirlik_merkezi=[round(c.x, 3), round(c.y, 3), round(c.z, 3)],
                         gruplar=[GRUP_AD[(d["ad"], g)] for g, _ in d["gruplar"]]))
m_top, c_top = kutle_am(parcalar)
# beklenen: iskelet analizi + 2 x omuz (omuz analizinin grup kutleleri - travers; kabuk referansi 0 g)
omuz_tr = next(p for d in MOD if d["ad"] == "omuz_sag" for p in d["parcalar"] if p["ad"].startswith("Omuz traversi"))["kutle"]
omuz_net = sum(omz["kutle"].values()) - omuz_tr
beklenen_kutle = isk["kutle_g"] + 2 * omuz_net
beklenen_parca = isk["parca_sayisi"] + 2 * (omz["parca_sayisi"] - 2)
formul = "iskelet %d + 2 x (omuz %d - travers - kabuk referansi)" % (isk["parca_sayisi"], omz["parca_sayisi"])
for d in MOD:                      # diger moduller: kendi analiz JSON'u (<modul>/<modul>-analiz.json)
    if d["ad"] in ("iskelet", "omuz_sag", "omuz_sol"):
        continue
    js = json.load(open(os.path.join(UST, d.get("analiz") or os.path.join(d["ad"], "%s-analiz.json" % d["ad"])), encoding="utf-8"))
    beklenen_kutle += js["kutle_g"]
    beklenen_parca += js["parca_sayisi"]
    formul += " + %s %d" % (d["ad"], js["parca_sayisi"])
kars = dict(
    parca=dict(montaj=len(feats), beklenen=beklenen_parca, formul=formul, ayni=len(feats) == beklenen_parca),
    kutle=dict(montaj_dosyasi=round(m_dosya, 2), bellek=round(m_top, 2), beklenen_analizlerden=round(beklenen_kutle, 2),
               carpisma=crp["kutle_toplam_g"], fark_analiz=round(m_dosya - beklenen_kutle, 3),
               fark_carpisma=round(m_dosya - crp["kutle_toplam_g"], 3)),
    am=dict(montaj_dosyasi=[round(c_dosya.x, 3), round(c_dosya.y, 3), round(c_dosya.z, 3)],
            bellek=[round(c_top.x, 3), round(c_top.y, 3), round(c_top.z, 3)], carpisma=crp["agirlik_merkezi"],
            fark_carpisma_mm=round((c_dosya - V(*crp["agirlik_merkezi"])).Length, 3),
            fark_bellek_mm=round((c_dosya - c_top).Length, 4)),
    not_="analiz JSON'lari 0,1 g'a yuvarlanmis; carpisma AM'si 0,01 mm'ye")
log("karsilastirma: parca %d/%d, kutle fark %.3f g (analiz) %.3f g (carpisma), AM fark %.3f mm" % (
    len(feats), beklenen_parca, kars["kutle"]["fark_analiz"], kars["kutle"]["fark_carpisma"], kars["am"]["fark_carpisma_mm"]))

out = dict(
    dosya="robot-montaj.FCStd", step="robot-montaj.step", step_kati=step_kati,
    parca_sayisi=len(feats), grup_sayisi=len(GRUP), gecersiz=gecersiz, hacim_fark_mm3=hacim_fark,
    ayna_merkez_fark_mm=ayna_merkez_fark,
    moduller=mod_ozet, eklemler=EKLEM, dosyadaki_eklem=dosya_eklem, solve=r_solve, ev_pozu_cozucu_sapmasi=ev_sapma,
    kutle_g=round(m_dosya, 2), agirlik_merkezi=kars["am"]["montaj_dosyasi"], karsilastirma=kars,
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "montaj-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("bitti")
