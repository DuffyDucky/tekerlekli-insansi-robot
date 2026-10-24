# Lale 1,70 m TASLAK - montaj + kayit + kutle/AM + baski tablosu + kisa yerlesim kontrolu (FreeCAD 1.1)
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla):
#   FC_SCRIPT=<bu dosya> "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/freecadcmd.exe" C:/Users/Victus/.robot-cad/run_fc.py
# Cikti (bu klasor): taslak-170.FCStd (Assembly: gruplar + eklemler), taslak-170.step, kutle.json, taslak-analiz.json
#   %TEMP%/taslak170-gorsel.FCStd: renk bazinda bilesik (yeni + eski 125 cm), taslak_gorsel.py (GUI) bunu cizer.
# Tam carpisma taramasi BURADA YOK (analiz ajani): yalniz ev pozunda yeni/degisen parcalarin cakismasi, kafa tilt +-15 ve pan +-90
# suprulmesinde kafa <-> boyun / govde / omuz / kabuk.
import os, sys, json, time, math, tempfile
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import taslak_parcalar as TP
from taslak_parcalar import V, A, TA, MD, log
import numpy as np

DOSYA = os.path.join(HERE, "taslak-170.FCStd")
STEP = os.path.join(HERE, "taslak-170.step")
GORSEL_DOC = os.path.join(tempfile.gettempdir(), "taslak170-gorsel.FCStd")
P = TP.P


def r3(v, n=2):
    return [round(v.x, n), round(v.y, n), round(v.z, n)]


def kam(sec):
    m, c = TP.kutle_am(sec)
    return dict(kutle_g=round(m, 1), am=r3(c), parca=len(sec))


# ====================================================================== 1) FreeCAD Assembly
doc = App.newDocument("Taslak170")
asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
asm.Label = "Lale 170 taslak"
jg = asm.newObject("Assembly::JointGroup", "Joints")
jg.Label = "Eklemler"
GP, FEAT = {}, {}
for (mod, g), gd in TP.GRUPLAR.items():
    gp = asm.newObject("App::Part", gd["isim"])
    gp.Label = "%s - %s" % (gd["isim"], gd["etiket"])
    gp.addProperty("App::PropertyString", "Modul", "Robot")
    gp.Modul = mod
    GP[gd["isim"]] = gp
    FEAT[gd["isim"]] = []
for k, p in enumerate(P):
    o = GP[p["grup_isim"]].newObject("Part::Feature", "T%04d" % k)
    o.Label = p["ad"] + ((" (%s)" % p["modul"].split("_")[1]) if p["modul"].endswith(("_sag", "_sol")) else "")
    o.Shape = p["shape"]
    for prop, val in (("Modul", p["modul"]), ("Grup", p["grup"]), ("Tur", p["tur"]), ("Malzeme", p["malzeme"]), ("Kod", p["kod"]),
                      ("Renk", p["renk"]), ("Not", p["not_"]), ("Durum", p["durum"])):
        o.addProperty("App::PropertyString", prop, "Robot")
        setattr(o, prop, str(val))
    o.addProperty("App::PropertyFloat", "Kutle_g", "Robot")
    o.Kutle_g = p["kutle"]
    FEAT[p["grup_isim"]].append((o, p))
doc.recompute()
log("nesneler:", len(P), "parca,", len(GP), "grup")

import JointObject


def ref_nesne(grup, onek=None):
    fl = FEAT[grup]
    if onek:
        for o, p in fl:
            if p["ad"].startswith(onek):
                return o
    return next((o for o, p in fl if p["tur"] == "Baski"), fl[0][0])


EK_JSON = []
for e in TP.EKLEMLER:
    if e["tip"] == "Grounded":
        gj = jg.newObject("App::FeaturePython", "Sabit_" + e["cocuk"])
        JointObject.GroundedJoint(gj, GP[e["cocuk"]])
        gj.Label = "%s zemine sabit" % e["cocuk"]
        EK_JSON.append(dict(tip="Grounded", cocuk=e["cocuk"]))
        continue
    ust, alt = GP[e["ebeveyn"]], GP[e["cocuk"]]
    if e["tip"] == "Fixed":
        cer = App.Placement(e["nokta"], App.Rotation())
        isim, et, tip = "Sabit_" + e["cocuk"], "%s -> %s (sabit)" % (e["cocuk"], e["ebeveyn"]), 0
        r1, r2 = ref_nesne(e["ebeveyn"], e["ref"]), ref_nesne(e["cocuk"])
    else:
        cer = e["cerceve"]
        isim = e["cocuk"] + "_" + "".join(s.capitalize() for s in e["anahtar"].split("_"))
        et, tip = "%s %s" % (e["cocuk"], e["ad"]), 1
        r1, r2 = ref_nesne(e["ebeveyn"]), ref_nesne(e["cocuk"])
    j = jg.newObject("App::FeaturePython", isim)
    JointObject.Joint(j, tip)
    j.Label = et
    j.Reference1 = [ust, [r1.Name + ".Face1", r1.Name + ".Vertex1"]]
    j.Reference2 = [alt, [r2.Name + ".Face1", r2.Name + ".Vertex1"]]
    j.Detach1 = j.Detach2 = True
    j.Placement1 = cer
    j.Placement2 = cer
    if e["tip"] == "Revolute" and e["sinir"]:
        j.EnableAngleMin = j.EnableAngleMax = True
        j.AngleMin, j.AngleMax = e["sinir"]
    ax = cer.Rotation.multVec(V(0, 0, 1))
    EK_JSON.append(dict(tip=e["tip"], isim=j.Name, etiket=et, ebeveyn=e["ebeveyn"], cocuk=e["cocuk"], nokta=r3(cer.Base, 3),
                        eksen=r3(ax, 6), sinir=list(e["sinir"]) if e.get("sinir") else None, anahtar=e.get("anahtar"),
                        aciklama=e.get("aciklama", e.get("kaynak", ""))))
r_solve = asm.solve()
doc.recompute()
ev_sapma = max(max(gp.Placement.Base.Length, math.degrees(gp.Placement.Rotation.Angle)) for gp in GP.values())
for gp in GP.values():
    gp.Placement = App.Placement()
doc.recompute()
doc.saveAs(DOSYA)
import Import
Import.export(list(GP.values()), STEP)
step_kati = len(Part.read(STEP).Solids)
log("eklem", len(EK_JSON), "solve", r_solve, "ev sapmasi %.2e" % ev_sapma, "STEP kati", step_kati)
App.closeDocument(doc.Name)

# ====================================================================== 2) olculer, kutle, AM
bb = None
for p in P:
    b = p["shape"].optimalBoundingBox()
    bb = b if bb is None else bb.united(b)
bb_e = None
for p in TP.ESKI:
    b = p["shape"].optimalBoundingBox()
    bb_e = b if bb_e is None else bb_e.united(b)
m_top, c_top = TP.kutle_am(P)
m_eski, c_eski = TP.kutle_am(TP.ESKI)
PAY = [dict(TA.KABLO_PAY_TABAN, ad="kablo payi (taban, mevcut tahmin)"), dict(TA.KABLO_PAY_UZAMA, ad="kablo payi (govde uzamasi, tahmini)")]
m_pay = m_top + sum(x["kutle_g"] for x in PAY)
c_pay = (c_top * m_top + sum((V(*x["merkez"]) * x["kutle_g"] for x in PAY), V(0, 0, 0))) * (1.0 / m_pay)
m_epay = m_eski + TA.KABLO_PAY_TABAN["kutle_g"]
c_epay = (c_eski * m_eski + V(*TA.KABLO_PAY_TABAN["merkez"]) * TA.KABLO_PAY_TABAN["kutle_g"]) * (1.0 / m_epay)


def secim(**kw):
    return [p for p in P if all((p[k] in v) if isinstance(v, (tuple, list, set)) else p[k] == v for k, v in kw.items())]


EK = {(e["cocuk"], e.get("anahtar")): e for e in EK_JSON}


def eksen(cocuk, anahtar):
    e = EK[(cocuk, anahtar)]
    return dict(nokta=e["nokta"], yon=e["eksen"], aralik=e["sinir"], eklem=e["isim"])


def eksen_uzaklik(c, e):
    n, u = V(*e["nokta"]), V(*e["yon"])
    d = c - n
    return (d - u * d.dot(u)).Length


# --- kafa
bas = secim(modul="kafa", grup="Bas")
boyun = secim(modul="kafa", grup="Boyun")
kgov = secim(modul="kafa", grup="Govde")
e_tilt, e_pan = eksen("Kafa_Bas", "tilt"), eksen("Kafa_Boyun", "pan")
m_b, c_b = TP.kutle_am(bas)
m_pb, c_pb = TP.kutle_am(bas + boyun)
tilt_n = V(*e_tilt["nokta"])
KAFA = dict(
    tilt_ekseni=e_tilt, pan_ekseni=e_pan,
    tilt_grubu=dict(kam(bas), aciklama="Kafa_Bas: kafa iskeleti, kabuklar, 10,1 in ekran, tirnaklar, kamera, Pi 5, cevirici, amfi, tilt horn, 625ZZ dis bilezigi, civatalar",
                    am_eksene_dik_uzaklik_mm=round(eksen_uzaklik(c_b, e_tilt), 3),
                    am_eksene_gore=dict(y=round(c_b.y - tilt_n.y, 3), z=round(c_b.z - tilt_n.z, 3),
                                        not_="tilt ekseninden (y yukari, z ileri); x yonu tilt torkunu etkilemez"),
                    kablo_payi=TA.KABLO_PAY_KAFA),
    pan_grubu=dict(kam(bas + boyun), aciklama="Kafa_Boyun + Kafa_Bas: pan horn, boyun mili, adaptor, saplamalar, catal, tilt servosu, 625ZZ pimi + tilt grubu",
                   am_pan_eksenine_dik_uzaklik_mm=round(eksen_uzaklik(c_pb, e_pan), 3)),
    govde=dict(kam(kgov), aciklama="Kafa_Govde (traverse sabit): boyun plakasi, servo yuvasi, rulman yuvasi, 6808 dis bilezikleri, pan servosu"),
    kafa_toplam=kam(bas + boyun + kgov),
    adaptor_h_mm=round(TP.H_ADAPTOR, 2), tilt_ekseni_kafa_yereli_y=round(TP.YT_YENI, 2), tilt_eski_kafa_yereli_y=TA.TILT_ESKI_Y,
    kafa_ust_y=round(bb.YMax, 2), kafa_alt_y=round(TP.KAFA_O.y + TA.KAFA_ALT_YEREL, 2),
    denge=dict(dy=round(TP.KAFA_INFO["dy"], 3), zb=round(TP.KAFA_INFO["zb"], 3), gecmis=TP.KAFA_DENGE,
               not_="dy: ekran merkezinin tilt eksenine gore yuksekligi; zb: arka dis yuzun eksene gore z'si (sekant, kafa10.dengele)"),
    ekran=TA.EKRAN10,
)
log("kafa tilt grubu %.1f g AM eksene dik %.3f mm; pan grubu %.1f g" % (m_b, KAFA["tilt_grubu"]["am_eksene_dik_uzaklik_mm"], m_pb))

# --- kollar
KOL = {}
for t in ("sag", "sol"):
    on = "Omuz" + t.capitalize()
    dr = "Dirsek" + t.capitalize()
    gob = secim(modul="omuz_" + t, grup="Gobek")
    kol = secim(modul="omuz_" + t, grup="Kol")
    ust = secim(modul="dirsek_" + t, grup="UstKol")
    onk = secim(modul="dirsek_" + t, grup="OnKol")
    el = secim(modul="dirsek_" + t, grup="El")
    s1 = eksen(on + "_Gobek", "one_arka")
    s2 = eksen(on + "_Kol", "yana")
    de = eksen(dr + "_OnKol", "dirsek")
    bi = eksen(dr + "_El", "bilek")
    sx = 1 if t == "sag" else -1
    el_ucu = V(sx * A.DIRSEK["el_ucu"][0], TA.S3_YENI + A.DIRSEK["el_ucu"][1] - (TA.KOL_BOY_YENI - TA.KOL_BOY_ESKI), A.DIRSEK["el_ucu"][2])
    KOL[t] = dict(
        omuz_ekseni_S1=s1, S2_ekseni=s2, dirsek_ekseni=de, bilek_ekseni=bi, el_ucu=r3(el_ucu),
        omuz_ekseni_y=TA.S3_YENI,
        bolum_boylari_mm=dict(ust_kol=round(TA.S3_YENI - de["nokta"][1], 2), on_kol=round(de["nokta"][1] - bi["nokta"][1], 2),
                              el=round(bi["nokta"][1] - el_ucu.y, 2), toplam=round(TA.S3_YENI - el_ucu.y, 2),
                              not_="ev pozunda dikey: S1 ekseni -> dirsek ekseni -> bilek ekseni (horn alt yuzu) -> el ucu"),
        bilesenler={"omuz gobegi (S1 ile doner)": kam(gob), "ust kol: kol catali + tup + S2 servosu (S1 + S2)": kam(kol),
                    "dirsek catali (ust kola sabit)": kam(ust), "on kol + dirsek/bilek servolari (dirsek ile)": kam(onk),
                    "bilek flansi + el (bilek ile)": kam(el)},
        S1_ile_donen=kam(gob + kol + ust + onk + el), S2_ile_donen=kam(kol + ust + onk + el), dirsek_ile_donen=kam(onk + el),
        bilek_ile_donen=kam(el),
    )


def kol_moment(parcalar, s3, x_isaret):
    """Kol yatay one kalkmis (S1 90 derece): S1 eksenine gore statik moment, g*mm (ev pozunda dikey uzaklik = moment kolu)."""
    return sum(p["kutle"] * (s3 - p["merkez"].y) for p in parcalar)


def kol_parcalar(liste, t, yeni):
    if yeni:
        return [p for p in liste if (p["modul"] == "omuz_" + t and p["grup"] == "Kol") or p["modul"] == "dirsek_" + t]
    return [p for p in liste if (p["modul"] == "omuz_" + t and p["grup"] == "Kol") or p["modul"] == "dirsek_" + t]


Mn = kol_moment(kol_parcalar(P, "sag", True), TA.S3_YENI, 1)
Me = kol_moment(kol_parcalar(TP.ESKI, "sag", False), A.S3, 1)
mkn = sum(p["kutle"] for p in kol_parcalar(P, "sag", True))
mke = sum(p["kutle"] for p in kol_parcalar(TP.ESKI, "sag", False))
# x1,36 kaba tahmini: kol boyu orantili, uzayan bolumlerin birim kutlesi bu taslaktaki uzatmalarla ayni (tup 0,41 g/mm, yaka 0,54 g/mm)
L136 = TA.KOL_BOY_ESKI * 1.36
ek136 = (L136 - TA.KOL_BOY_ESKI)
m_ek_birim = (mkn - mke) / (TA.KOL_BOY_YENI - TA.KOL_BOY_ESKI)
M136 = Me * 1.36 + m_ek_birim * ek136 * (TA.KOL_BOY_ESKI + ek136 / 2) * 0.5
KOL["oran"] = dict(hedef=TA.KOL_ORAN_HEDEF, secilen=round(TA.KOL_ORAN, 4), secim=TA.KOL_SECIM, karar=TA.KOL_KARAR,
                   boy_eski_mm=TA.KOL_BOY_ESKI, boy_yeni_mm=round(TA.KOL_BOY_YENI, 2),
                   ust_kol_uzama_mm=TA.UST_KOL_UZAMA, on_kol_uzama_mm=TA.ON_KOL_UZAMA, el_uzama_mm=TA.EL_UZAMA,
                   secenekler=TA.KOL_SECENEK, omuz_servo=dict(TA.OMUZ_SERVO, eski=TA.OMUZ_SERVO_ESKI["ad"]),
                   S1_statik_moment_kol_yatay=dict(eski_gmm=round(Me, 0), yeni_gmm=round(Mn, 0), oran=round(Mn / Me, 3),
                                                   x136_kaba_tahmin_gmm=round(M136, 0), x136_oran=round(M136 / Me, 2),
                                                   not_="kol (Kol grubu + dirsek) one yatay; geometrik moment orani (servo bagimsiz). Servo paylari (%s) "
                                                        "kontrol ajaninin hesabinda (taslak_hesap.py / kol-analiz)" % TA.OMUZ_SERVO["ad"]),
                   kol_kutle_g=dict(eski=round(mke, 1), yeni=round(mkn, 1)))
log("kol: moment oran %.3f (x1,36 kaba %.2f), kutle %.1f -> %.1f g" % (Mn / Me, M136 / Me, mke, mkn))

# --- moduller ve gruplar
MODOZ = []
for ad in MD.SIRA:
    sec = [p for p in P if p["modul"] == ad]
    sec_e = [p for p in TP.ESKI if p["modul"] == ad]
    MODOZ.append(dict(ad=ad, yeni=kam(sec), eski=kam(sec_e)))
GRUPOZ = [dict(isim=gd["isim"], modul=gd["modul"], **kam([p for p in P if p["grup_isim"] == gd["isim"]])) for gd in TP.GRUPLAR.values()]
DESTEK = [dict(teker=k, x=round(sx * (TP.TP.X_WH + TA.TABAN_DX), 1), y=0.0, z=round(sz * TP.TP.Z_WH, 1)) for k, sx, sz in MD.TEKER_KOSE]

KUTLE = dict(
    aciklama="Lale 1,70 m taslak: parca bazinda kutle ve agirlik merkezi (ev pozu: kollar asagida, kafa duz)",
    koordinat=TA.KOORDINAT, birim="g, mm",
    olcu=dict(boy=round(bb.YMax, 1), genislik_x=round(bb.XLength, 1), derinlik_z=round(bb.ZLength, 1), zemin_y=round(bb.YMin, 2),
              not_="optimalBoundingBox; boy = kafa kabugu tepesi"),
    toplam=dict(kutle_g=round(m_top, 1), am=r3(c_top), parca_sayisi=len(P),
                kutle_payli_g=round(m_pay, 1), am_payli=r3(c_pay), paylar=PAY),
    eski_125=dict(kutle_g=round(m_eski, 1), am=r3(c_eski), parca_sayisi=len(TP.ESKI), kutle_payli_g=round(m_epay, 1), am_payli=r3(c_epay),
                  boy=round(bb_e.YMax, 1), not_="mevcut modul betikleri, ayni yukleyiciler (ana montaj dosyasi degil, guncel betikler)"),
    taban=dict(genislik_parametresi_mm=TA.TABAN_W, eski_mm=TA.TABAN_W_ESKI, her_yana_ek_mm=TA.TABAN_DX,
               destek_poligonu_teker_merkezleri=DESTEK, not_="teker yere y = 0'da, teker merkezi alti (x, z); TASLAK_TABAN_W ortam degiskeniyle yeniden uretilir"),
    kafa=KAFA, kol=KOL, moduller=MODOZ, gruplar=GRUPOZ, eklemler=EK_JSON,
    parcalar=[dict(ad=p["ad"], modul=p["modul"], grup=p["grup_isim"], kutle_g=round(p["kutle"], 2), am=r3(p["merkez"]), tur=p["tur"],
                   malzeme=p["malzeme"], durum=p["durum"]) for p in P],
)
json.dump(KUTLE, open(os.path.join(HERE, "kutle.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
log("kutle: %.1f g AM %s (eski %.1f g AM %s), boy %.1f" % (m_top, r3(c_top), m_eski, r3(c_eski), bb.YMax))


# ====================================================================== 3) baski tablosu (okul yazicisi 250 x 250 x 250, hedef <= 230)
def baski_olcu(sh, yukari):
    pts = np.array([[q.x, q.y, q.z] for q in sh.tessellate(1.0)[0]])
    if yukari is None:
        en = None
        for u in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
            r = baski_olcu(sh, u)
            if en is None or max(r[:3]) < max(en[:3]):
                en = r
        return en
    rot = App.Rotation(V(*yukari), V(0, 0, 1))
    M = np.array(rot.toMatrix().A).reshape(4, 4)[:3, :3]
    X = pts @ M.T
    h = X[:, 2].max() - X[:, 2].min()
    best = None
    for th in range(0, 90):
        c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
        x = X[:, 0] * c - X[:, 1] * s
        y = X[:, 0] * s + X[:, 1] * c
        w, d = x.max() - x.min(), y.max() - y.min()
        if best is None or max(w, d) < max(best[0], best[1]):
            best = (max(w, d), min(w, d), th)
    return (round(best[0], 1), round(best[1], 1), round(h, 1), best[2], tuple(yukari))


BASKI = []
for p in P:
    if p["tur"] != "Baski":
        continue
    yuk = p["baski"]["yukari"] if p.get("baski") else None
    w, d, h, th, u = baski_olcu(p["shape"], yuk)
    hac = p["shape"].Volume
    BASKI.append(dict(ad=p["ad"], modul=p["modul"], durum=p["durum"], olcu=[w, d, h], tabla_aci=th, yukari=list(u),
                      yon=p["baski"]["yon"] if p.get("baski") else "bilinmiyor: en kucuk sigan yon", sigar_250=max(w, d, h) <= TA.TABLA[0],
                      hedef_230=max(w, d, h) <= TA.TABLA_HEDEF, hacim_cm3=round(hac / 1000, 1), kutle_g=round(p["kutle"], 1),
                      filament_g=round(p["kutle"] * 1.05, 1), sure_saat=round(p["kutle"] / A.PETG_RHO * 1000 / A.PETG_HACIM_HIZI / 3600, 2)))
log("baski: %d parca, 250'ye sigmayan %d, 230 hedefi asan %d" % (len(BASKI), sum(not b["sigar_250"] for b in BASKI), sum(not b["hedef_230"] for b in BASKI)))


# ====================================================================== 4) kisa yerlesim kontrolu
def ortak(a, b):
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


ESIK = 0.5
t_k = time.time()
deg = [i for i, p in enumerate(P) if p["v"] is None]
bbs = [p["shape"].BoundBox for p in P]
cak, aday = [], 0
for i in deg:
    for j in range(len(P)):
        if j == i or (P[j]["v"] is None and j < i):
            continue
        if not bbs[i].intersect(bbs[j]):
            continue
        aday += 1
        v = ortak(P[i]["shape"], P[j]["shape"])
        if v > ESIK or v < 0:
            cak.append(dict(a=P[i]["ad"], a_modul=P[i]["modul"], b=P[j]["ad"], b_modul=P[j]["modul"], hacim_mm3=round(v, 2)))
# tasinan parcalar arasi (farkli oteleme): orn. dirsek (DY-30) <-> omuz (DY), kafa catali (DY+H) <-> boyun mili (DY), ust kabuk <-> alt
tas = [i for i, p in enumerate(P) if p["v"] is not None]
for ii, i in enumerate(tas):
    for j in tas[ii + 1:]:
        if (P[i]["v"] - P[j]["v"]).Length < 1e-9 or not bbs[i].intersect(bbs[j]):
            continue
        aday += 1
        v = ortak(P[i]["shape"], P[j]["shape"])
        if v > ESIK or v < 0:
            cak.append(dict(a=P[i]["ad"], a_modul=P[i]["modul"], b=P[j]["ad"], b_modul=P[j]["modul"], hacim_mm3=round(v, 2)))
# 125 cm robotta da var mi (ayni modul + ad, en yakin merkez): mevcut tasarimdan gelen cakismalar ayrilir
def eski_karsi(ad, modul, merkez):
    ad_ = [q for q in TP.ESKI if q["ad"] == ad and q["modul"] == modul]
    return min(ad_, key=lambda q: (q["merkez"] - merkez).Length) if ad_ else None


IDX = {(p["ad"], p["modul"]): p for p in P}
for c in cak:
    pa = next(p for p in P if p["ad"] == c["a"] and p["modul"] == c["a_modul"])
    pb = next(p for p in P if p["ad"] == c["b"] and p["modul"] == c["b_modul"])
    ea = eski_karsi(pa.get("eski_ad", pa["ad"]), c["a_modul"], pa["merkez"] - (pa["v"] or TP.kaydir(pa["modul"], pa["grup"])))
    eb = eski_karsi(pb.get("eski_ad", pb["ad"]), c["b_modul"], pb["merkez"] - (pb["v"] or TP.kaydir(pb["modul"], pb["grup"])))
    c["eski_125_hacim_mm3"] = round(ortak(ea["shape"], eb["shape"]), 2) if (ea and eb) else None
    c["kaynak"] = "mevcut tasarim (125'te de var)" if (c["eski_125_hacim_mm3"] or 0) > ESIK else "taslak"
log("ev pozu kontrolu: %d aday cift, %d cakisma (%d taslaktan) (%.0f s)" % (aday, len(cak), sum(1 for c in cak if c["kaynak"] == "taslak"),
                                                                        time.time() - t_k))


def don(sh, nokta, yon, aci):
    s = sh.copy()
    s.transformShape(App.Placement(V(0, 0, 0), App.Rotation(V(*yon), aci), V(*nokta)).toMatrix(), True)
    return s


t_k = time.time()
hedef = [p for p in P if p["grup_isim"] in ("Kafa_Govde", "Kabuk", "OmuzSag_Govde", "OmuzSol_Govde", "OmuzSag_Gobek", "OmuzSol_Gobek",
                                            "OmuzSag_Kol", "OmuzSol_Kol", "Iskelet") and p["shape"].BoundBox.YMax > TA.S3_YENI - 120]
SUP = []
for psi in (-90.0, -45.0, 0.0, 45.0, 90.0):
    for th in (-15.0, -7.5, 0.0, 7.5, 15.0):
        if psi == 0.0 and th == 0.0:
            continue
        hareket = []
        for p in bas:
            s = don(p["shape"], e_tilt["nokta"], e_tilt["yon"], th) if th else p["shape"]
            hareket.append((p, don(s, e_pan["nokta"], e_pan["yon"], psi) if psi else s))
        for p in boyun:
            hareket.append((p, don(p["shape"], e_pan["nokta"], e_pan["yon"], psi) if psi else p["shape"]))
        n_c, en_az = 0, []
        for (p, s) in hareket:
            karsi = hedef + (boyun if p["grup_isim"] == "Kafa_Bas" and th else [])
            for q in karsi:
                if q is p:
                    continue
                qs = q["shape"]
                if q["grup_isim"] == "Kafa_Boyun":
                    qs = don(qs, e_pan["nokta"], e_pan["yon"], psi) if psi else qs
                if not s.BoundBox.intersect(qs.BoundBox):
                    continue
                v = ortak(s, qs)
                if v > ESIK or v < 0:
                    n_c += 1
                    en_az.append(dict(a=p["ad"], b=q["ad"], hacim_mm3=round(v, 2)))
        SUP.append(dict(pan=psi, tilt=th, cakisma=n_c, ornek=en_az[:6]))
log("kafa suprulmesi: %d poz, cakisan poz %d (%.0f s)" % (len(SUP), sum(1 for s in SUP if s["cakisma"]), time.time() - t_k))

# --- kisa kol taramasi (sag kol; sol X aynasi): on kol + el (uzayan bolum) kaba izgarada sabit govdeye, kafaya (ev pozu) ve kendi
#     ust koluna karsi. Tam tarama (5 derece ince, kafa x kol pan/tilt, iki kol) kontrol ajaninda.
t_k = time.time()


def eklem_P(e, aci):
    return App.Placement(V(0, 0, 0), App.Rotation(V(*e["yon"]), aci), V(*e["nokta"])) if aci else App.Placement()


def tasi_P(sh, pl):
    s = sh.copy()
    s.transformShape(pl.toMatrix(), True)
    return s


KS = KOL["sag"]
e_s1, e_s2, e_de, e_bi = KS["omuz_ekseni_S1"], KS["S2_ekseni"], KS["dirsek_ekseni"], KS["bilek_ekseni"]
k_on = secim(modul="dirsek_sag", grup="OnKol")
k_el = secim(modul="dirsek_sag", grup="El")
k_ust = secim(modul="dirsek_sag", grup="UstKol") + secim(modul="omuz_sag", grup="Kol")
k_gob = secim(modul="omuz_sag", grup="Gobek")
sabit = [p for p in P if (p["modul"] == "kabuk" and p["tur"] == "Baski") or p["modul"] in ("iskelet", "kafa") or
         (p["modul"] == "omuz_sag" and p["grup"] == "Govde")]
sabit = [p for p in sabit if p["shape"].BoundBox.XMax > 60.0 and p["shape"].BoundBox.YMax > TA.S3_YENI - 520.0]
S1_ = (-45.0, 0.0, 45.0, 90.0, 135.0)
S2_ = (e_s2["aralik"][0], 45.0, 90.0, e_s2["aralik"][1])
DE_ = (0.0, 35.0, 70.0, 105.0)
BI_ = (-90.0, 0.0, 90.0)
KOL_TAR = dict(izgara=dict(S1=S1_, S2=S2_, dirsek=DE_, bilek=BI_), hareketli="dirsek_sag OnKol + El (%d parca)" % (len(k_on) + len(k_el)),
               hedef="kabuk (baski), iskelet, kafa (ev pozu), omuz_sag Govde/Gobek, kendi ust kolu (Kol + dirsek catali); x > 60, y > S3 - 520",
               poz=0, cakisan_poz=0, cakisma=[], en_dusuk_el_y=None)
en_alt = None
for phi in S1_:
    P1 = eklem_P(e_s1, phi)
    gob_p = [(q, tasi_P(q["shape"], P1)) for q in k_gob] if phi else [(q, q["shape"]) for q in k_gob]
    for th in S2_:
        P2 = P1.multiply(eklem_P(e_s2, th))
        ust_p = [(q, tasi_P(q["shape"], P2)) for q in k_ust]
        hedefler = [(q, q["shape"]) for q in sabit] + gob_p + ust_p
        for al in DE_:
            P3 = P2.multiply(eklem_P(e_de, al))
            on_p = [(q, tasi_P(q["shape"], P3)) for q in k_on]
            for be in BI_:
                P4 = P3.multiply(eklem_P(e_bi, be))
                el_p = [(q, tasi_P(q["shape"], P4)) for q in k_el]
                KOL_TAR["poz"] += 1
                n0 = len(KOL_TAR["cakisma"])
                for (p, s) in on_p + el_p:
                    sb = s.BoundBox
                    for (q, qs) in hedefler:
                        if not sb.intersect(qs.BoundBox):
                            continue
                        v = ortak(s, qs)
                        if v > ESIK or v < 0:
                            KOL_TAR["cakisma"].append(dict(poz=[phi, th, al, be], a=p["ad"], b=q["ad"], b_modul=q["modul"], hacim_mm3=round(v, 2)))
                if len(KOL_TAR["cakisma"]) > n0:
                    KOL_TAR["cakisan_poz"] += 1
                el_s = next(s for (q, s) in el_p if q["ad"] == "El")
                if en_alt is None or el_s.BoundBox.YMin < en_alt[0]:
                    en_alt = (el_s.BoundBox.YMin, [phi, th, al, be])
KOL_TAR["en_dusuk_el_y"] = dict(y=round(en_alt[0], 1), poz=en_alt[1])
KOL_TAR["sure_s"] = round(time.time() - t_k, 1)
log("kol kisa tarama: %d poz, cakisan poz %d, cakisma %d, el en alt y %.1f (%.0f s)" % (
    KOL_TAR["poz"], KOL_TAR["cakisan_poz"], len(KOL_TAR["cakisma"]), en_alt[0], time.time() - t_k))

# en kucuk bosluklar (bilgi): kafa alti <-> omuz kaseti / kabuk ust kapagi, tabla <-> catal (ev pozu)
def mesafe(a_list, b_list):
    en = None
    for a in a_list:
        for b in b_list:
            ba, bb_ = a["shape"].BoundBox, b["shape"].BoundBox
            ba2 = App.BoundBox(ba)
            ba2.enlarge(60.0)
            if not ba2.intersect(bb_):
                continue
            d = a["shape"].distToShape(b["shape"])[0]
            if en is None or d < en[0]:
                en = (d, a["ad"], b["ad"])
    return None if en is None else dict(mm=round(en[0], 2), a=en[1], b=en[2])


kab_bas = [p for p in bas if p["tur"] == "Baski"]
BOSLUK = {
    "kafa kabugu <-> omuz (ev pozu)": mesafe(kab_bas, [p for p in P if p["modul"].startswith("omuz") and p["shape"].BoundBox.YMax > TA.S3_YENI]),
    "kafa kabugu <-> govde kabugu ust kapagi": mesafe(kab_bas, [p for p in P if p["ad"].startswith("Omuz bandi")]),
    "kafa (Bas) <-> egme catali / tilt servosu / adaptor": mesafe(bas, [p for p in boyun if p["ad"].startswith(("Egme catali", "Tilt servosu MG996R",
                                                                                                               "Boyun yukseltme"))]),
    "ekran <-> catal / adaptor": mesafe([p for p in bas if p["ad"].startswith("Yuz ekrani")], boyun),
    "el <-> govde kabugu (ev pozu, sag)": mesafe([p for p in P if p["modul"] == "dirsek_sag" and p["ad"] in ("El", "Dirsek catali", "On kol govdesi")],
                                                 [p for p in P if p["modul"] == "kabuk" and p["tur"] == "Baski"]),
}
log("bosluklar:", json.dumps(BOSLUK, ensure_ascii=True))

# --- dirsek catali dis kolu (TA.CATAL_DIS_KOL; eski 5 mm) kisa kontrolu, sag kol (sol X aynasi): ayni komsulara 5 mm ve yeni catal
#     (catal + 4 horn civatasi) mesafesi: ev pozu (15 mm icindeki tum parcalar), dirsek 0...105 (5 derece) on kola, S1 x S2 kaba
#     izgarada sabit govde / kafa / omuz govdesi + gobege. Tam tarama kontrol ajaninda.
t_k = time.time()
CAT_N = [p for p in P if p["modul"] == "dirsek_sag" and (p["ad"] == "Dirsek catali" or p["ad"].startswith(("Catal-horn civatasi", "Catal-horn pulu")))]
CAT_Y = [s for s in (p["shape"] for p in CAT_N)]
CAT_E = TP.CATAL_ESKI["sag"]["Dirsek catali"] + TP.CATAL_ESKI["sag"]["Catal-horn civatasi M3x8"]
CAT_ID = set(id(p) for p in CAT_N)
# ara kalinlik (8 mm kararinda 7 mm, 24 Ekim): ayni komsulara ucuncu sutun (ara_mm)
T_ARA = TP.CATAL_ARA_T[-1] if TP.CATAL_ARA_T else None
CAT_A = (TP.CATAL_ARA[T_ARA]["sag"]["Dirsek catali"] + TP.CATAL_ARA[T_ARA]["sag"]["civata"] + TP.CATAL_ARA[T_ARA]["sag"]["pul"]) if T_ARA else []


def en_yakin(shs, hedef_sh, pay=30.0):
    """shs (liste) ile hedef_sh arasi en kucuk mesafe; sinir kutusu pay'dan uzaksa None."""
    hb = hedef_sh.BoundBox
    en = None
    for s in shs:
        b = App.BoundBox(s.BoundBox)
        b.enlarge(pay)
        if not b.intersect(hb):
            continue
        d = s.distToShape(hedef_sh)[0]
        en = d if en is None else min(en, d)
    return en


CATAL_K = dict(kalinlik_mm=TA.CATAL_DIS_KOL, eski_mm=TA.CATAL_DIS_KOL_ESKI, dis_yuz_x_yerel=[round(TP.DP.DIS_KOL[1], 2), round(TP.X_DIS1, 2)],
               bilgi=TP.CATAL_INFO, ev_pozu=[], dirsek=[], omuz=[])
if T_ARA:
    CATAL_K.update(ara_kalinlik_mm=T_ARA, horn_civatasi="M3x%.0f" % TA.HORN_CIVATA_L, horn_pul=TA.HORN_PUL_N, destek_dis_yuze=TA.CATAL_DESTEK_DIS)


def _r(x):
    return None if x is None else round(x, 2)


for q in P:
    if id(q) in CAT_ID:
        continue
    d7 = en_yakin(CAT_Y, q["shape"], 15.0)
    d5 = en_yakin(CAT_E, q["shape"], 15.0)
    da = en_yakin(CAT_A, q["shape"], 15.0) if T_ARA else None
    if d7 is None and d5 is None and da is None:
        continue
    r = dict(parca=q["ad"], modul=q["modul"], eski_mm=None if d5 is None else round(d5, 2), yeni_mm=None if d7 is None else round(d7, 2))
    if T_ARA:
        r["ara_mm"] = _r(da)
    if d7 is not None and d7 < 1e-6 and (d5 is None or d5 > 1e-6):
        r["ortak_mm3"] = round(sum(ortak(s, q["shape"]) for s in CAT_Y), 2)          # yeni temas: hacim kesisiyor mu
    CATAL_K["ev_pozu"].append(r)
CATAL_K["ev_pozu"].sort(key=lambda r: (r["yeni_mm"] if r["yeni_mm"] is not None else 99.0))
CATAL_K["ev_pozu_yaklasan"] = [r for r in CATAL_K["ev_pozu"] if r["yeni_mm"] is not None and (r["eski_mm"] is None or r["yeni_mm"] < r["eski_mm"] - 0.01)]
KOAKS = ("Dirsek servosu cikis mili", "625ZZ rulman (ic bilezik)", "Pim pulu M5", "Pim civatasi M5x12")   # dirsek ekseninde: mesafe aciyla degismez
k_on_s = [q for q in secim(modul="dirsek_sag", grup="OnKol") if q["ad"] not in KOAKS]
CATAL_K["dirsek_haric"] = list(KOAKS)
for al in range(0, 106, 5):
    Pd = eklem_P(e_de, float(al))
    on_s = [(q, tasi_P(q["shape"], Pd) if al else q["shape"]) for q in k_on_s]
    r7 = [(x, q["ad"]) for (x, q) in ((en_yakin(CAT_Y, s, 20.0), q) for (q, s) in on_s) if x is not None]
    r5 = [(x, q["ad"]) for (x, q) in ((en_yakin(CAT_E, s, 20.0), q) for (q, s) in on_s) if x is not None]
    d7, d5 = (min(r7) if r7 else None), (min(r5) if r5 else None)
    CATAL_K["dirsek"].append(dict(dirsek=al, eski_mm=None if d5 is None else round(d5[0], 2), yeni_mm=None if d7 is None else round(d7[0], 2),
                                  eski_parca=d5 and d5[1], yeni_parca=d7 and d7[1]))
    if T_ARA:
        ra = [(x, q["ad"]) for (x, q) in ((en_yakin(CAT_A, s, 20.0), q) for (q, s) in on_s) if x is not None]
        da = min(ra) if ra else None
        CATAL_K["dirsek"][-1].update(ara_mm=None if da is None else round(da[0], 2), ara_parca=da and da[1])
hed_o = sabit + k_gob
gob_id = set(id(q) for q in k_gob)
for phi in S1_:
    P1 = eklem_P(e_s1, phi)
    for th in S2_:
        P2 = P1.multiply(eklem_P(e_s2, th))
        y_s = [tasi_P(s, P2) for s in CAT_Y]
        e_s = [tasi_P(s, P2) for s in CAT_E]
        a_s = [tasi_P(s, P2) for s in CAT_A]
        en7, en5, ena = None, None, None
        for q in hed_o:
            qs = tasi_P(q["shape"], P1) if id(q) in gob_id and phi else q["shape"]
            d7 = en_yakin(y_s, qs, 40.0)
            d5 = en_yakin(e_s, qs, 40.0)
            da = en_yakin(a_s, qs, 40.0) if T_ARA else None
            if d7 is not None and (en7 is None or d7 < en7[0]):
                en7 = (d7, q["ad"])
            if d5 is not None and (en5 is None or d5 < en5[0]):
                en5 = (d5, q["ad"])
            if da is not None and (ena is None or da < ena[0]):
                ena = (da, q["ad"])
        CATAL_K["omuz"].append(dict(poz=[phi, th], eski=None if en5 is None else [round(en5[0], 2), en5[1]],
                                    yeni=None if en7 is None else [round(en7[0], 2), en7[1]]))
        if T_ARA:
            CATAL_K["omuz"][-1]["ara"] = None if ena is None else [round(ena[0], 2), ena[1]]
CATAL_K["sure_s"] = round(time.time() - t_k, 1)
log("dirsek catali kontrolu (%.0f mm): ev pozu yaklasan %d; dirsek on kol en az %s -> %s; omuz izgarasi en az %s -> %s (%.0f s)" % (
    TA.CATAL_DIS_KOL, len(CATAL_K["ev_pozu_yaklasan"]),
    min((r["eski_mm"] for r in CATAL_K["dirsek"] if r["eski_mm"] is not None), default=None),
    min((r["yeni_mm"] for r in CATAL_K["dirsek"] if r["yeni_mm"] is not None), default=None),
    min((r["eski"][0] for r in CATAL_K["omuz"] if r["eski"]), default=None),
    min((r["yeni"][0] for r in CATAL_K["omuz"] if r["yeni"]), default=None), time.time() - t_k))

ANALIZ = dict(
    dosya="taslak-170.FCStd", step="taslak-170.step", step_kati=step_kati, parca_sayisi=len(P), grup_sayisi=len(GP), eklem_sayisi=len(EK_JSON),
    solve=r_solve, ev_pozu_cozucu_sapmasi=ev_sapma,
    gecersiz=[p["ad"] for p in P if not p["shape"].isValid()], coklu_kati=[p["ad"] for p in P if len(p["shape"].Solids) != 1],
    durum={k: sum(1 for p in P if p["durum"] == k) for k in ("ayni", "tasindi", "degisti", "yeni")},
    baski=BASKI, baski_ozet=dict(sayi=len(BASKI), yeni=sum(1 for b in BASKI if b["durum"] == "yeni"), degisti=sum(1 for b in BASKI if b["durum"] == "degisti"),
                                 sigmayan_250=[b["ad"] for b in BASKI if not b["sigar_250"]], hedef_230_asan=[b["ad"] for b in BASKI if not b["hedef_230"]],
                                 tabla=TA.TABLA, hedef=TA.TABLA_HEDEF),
    baglar=TP.BAGLAR, degisen=TP.DEGISEN,
    yerlesim=dict(ev_pozu_cakisma=cak, aday_cift=aday, esik_mm3=ESIK, kafa_suprulme=SUP, bosluk=BOSLUK, kol_kisa=KOL_TAR, catal=CATAL_K,
                  not_="kisa kontrol: yeni/degisen parcalar x tum parcalar ve farkli otelenen parca ciftleri (ev pozu); kafa pan {-90,-45,0,45,90} x "
                       "tilt {-15,-7,5,0,7,5,15}; sag kol kaba izgara (on kol + el). Tam carpisma taramasi (ince kol pozlari, kafa x kol) analiz ajaninda."),
    uzatma=dict(dy=TA.DY, dikis=TA.UZATMA_DIKIS, braket_y=TA.UZATMA_BRAKET_Y, direk_mm=TA.DIREK_L_YENI),
    sure_s=round(time.time() - TP.t0, 1), log=TP.LOG,
)
json.dump(ANALIZ, open(os.path.join(HERE, "taslak-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)

# ====================================================================== 5) gorsel belgesi (renk bazinda bilesik; yeni + eski yan yana)
g = App.newDocument("Taslak170Gorsel")
KAYIK = 900.0
KESIT = Part.makeBox(4000, 4000, 2000, V(-2000, -100, -2000))       # z < 0: kabugun on yarisi kaldirilir (ic gorunum)
for etiket, liste, dx in (("Yeni", P, 0.0), ("Eski", TP.ESKI, -KAYIK), ("Kesit", P, 0.0)):
    renk = {}
    for p in liste:
        if p.get("tur") == "Referans":
            continue
        sh = p["shape"]
        if etiket == "Kesit" and p["modul"] == "kabuk" and p["tur"] == "Baski" and sh.BoundBox.YMax > 300 and sh.BoundBox.YMin < 1450:
            sh = sh.common(KESIT)
            if sh.Volume < 1e-6:
                continue
        renk.setdefault(p["renk"], []).append(sh)
    for r, shs in renk.items():
        c = Part.makeCompound(shs)
        if dx:
            c.translate(V(dx, 0, 0))
        o = g.addObject("Part::Feature", "%s_%s" % (etiket, r.replace(" ", "_")))
        o.Shape = c
        o.addProperty("App::PropertyString", "Renk", "Robot")
        o.Renk = r
        o.addProperty("App::PropertyString", "Takim", "Robot")
        o.Takim = etiket
# dirsek catali karsilastirmasi (sag kol): Catal5 = 5 mm catal + M3x8, Catal<t> = yeni catal + horn civatalari (+ pul), ara kalinlik varsa
# (8 mm kararinda 7 mm + M3x10) Catal7 de; CatalCevre = sag omuz + sag dirsek (catal haric) + yakin kabuk/iskelet (yari saydam).
# taslak_gorsel: yalniz 5 / 7 -> gorsel/catal-5-7.png (2 x 2), 5 / 7 / 8 -> gorsel/catal-5-7-8.png (3 sutun x onden / izometrik).
# Baslik ozelligi: "kalinlik|civata" (gorsel basliklari).
CEV_BB = App.BoundBox(40.0, TA.S3_YENI - 330.0, -150.0, 330.0, TA.S3_YENI + 80.0, 150.0)
_takim = [("Catal5", "5|M3x8", [(s, "kirmizi") for s in TP.CATAL_ESKI["sag"]["Dirsek catali"]] +
           [(s, "celik") for s in TP.CATAL_ESKI["sag"]["Catal-horn civatasi M3x8"]])]
for _ta in TP.CATAL_ARA_T:
    _L, _n, _ = TA.horn_civatasi_secim(_ta)
    _c = TP.CATAL_ARA[_ta]["sag"]
    _takim.append(("Catal%g" % _ta, "%g|M3x%.0f%s" % (_ta, _L, " + %d pul" % _n if _n else ""),
                   [(s, "kirmizi") for s in _c["Dirsek catali"]] + [(s, "celik") for s in _c["civata"] + _c["pul"]]))
if TA.CATAL_DIS_KOL > TA.CATAL_DIS_KOL_ESKI:
    _takim.append(("Catal%g" % TA.CATAL_DIS_KOL, "%g|M3x%.0f%s" % (TA.CATAL_DIS_KOL, TA.HORN_CIVATA_L, " + %d pul" % TA.HORN_PUL_N if TA.HORN_PUL_N else ""),
                   [(p["shape"], "kirmizi" if p["ad"] == "Dirsek catali" else "celik") for p in CAT_N]))
_takim.append(("CatalCevre", "", [(p["shape"], p["renk"]) for p in P if id(p) not in CAT_ID and p.get("tur") != "Referans" and
                                  (p["modul"] in ("omuz_sag", "dirsek_sag") or p["shape"].BoundBox.intersect(CEV_BB))]))
for etiket, baslik, shs in _takim:
    renk = {}
    for sh, r in shs:
        renk.setdefault(r, []).append(sh)
    for r, ls in renk.items():
        o = g.addObject("Part::Feature", "%s_%s" % (etiket, r.replace(" ", "_")))
        o.Shape = Part.makeCompound(ls)
        o.addProperty("App::PropertyString", "Renk", "Robot")
        o.Renk = r
        o.addProperty("App::PropertyString", "Takim", "Robot")
        o.Takim = etiket
        if baslik:
            o.addProperty("App::PropertyString", "Baslik", "Robot")
            o.Baslik = baslik
g.saveAs(GORSEL_DOC)
App.closeDocument(g.Name)
log("bitti; gorsel belgesi", GORSEL_DOC)
