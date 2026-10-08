# Taban modulu - montaj, kontroller, muhendislik hesaplari, DXF, baski analizi, FCStd + STEP + BOM + json
# Calistir (yolda "ü" oldugu icin ASCII baslaticiyla): FC_SCRIPT=<bu dosya> freecadcmd run_fc.py   (~5-8 dk; kabuk parcalari kurulur)
# Kontroller: her parca isValid + tek kati; taban ici cakisma (0,5 mm3); baglantilar (dayanma, eksen hizasi, civata ucu payi /
# kavrama); taban <-> iskelet ve taban <-> kabuk ev pozunda (statik, burada); teker <-> etek boslugu; yeni ayrilmis bolgelerin
# iskelet/kabuga uyumu; X2D baski analizi; lazer DXF. Hesaplar: tam robot kutlesi + AM (diger modullerin analizlerinden + taban),
# kol pozlarinda devrilme (duz zemin + 5 derece rampa), motor torku (V3 varsayimlari), aku suresi (tahmini tuketim).
# Moduller arasi tarama (kollar, kafa) ve ana montaja ekleme 2. asamada (carpisma.py, montaj/), dokunulmaz.
import os, sys, json, math, time, csv
import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__))
UST = os.path.dirname(HERE)
for _p in (HERE, UST, os.path.join(UST, "iskelet"), os.path.join(UST, "kabuk"), os.path.join(UST, "omuz"), os.path.join(UST, "dirsek")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import taban_parcalar as TP
from taban_parcalar import V, P, BAG
import taban_lib as L
import arayuz as A

t0 = time.time()
TOL = 0.5          # mm3
TEMAS = 0.01       # mm
G = 9.81
T = A.TABAN


def log(*a):
    print(*a, "%.1fs" % (time.time() - t0), flush=True)


def kes(a, b, abb=None, bbb=None):
    abb = abb or a.BoundBox
    bbb = bbb or b.BoundBox
    if not abb.intersect(bbb):
        return 0.0
    try:
        return a.common(b).Volume
    except Exception:
        return -1.0


GERCEK = [p for p in P if p["tur"] != "Referans"]
IDX = {p["ad"]: k for k, p in enumerate(P)}
log("taban parca", len(P), "gercek", len(GERCEK))

# ====================================================================== 1) gecerlilik + taban ici cakisma
gecersiz = [p["ad"] for p in P if not p["shape"].isValid()]
coklu = [(p["ad"], p["kati"]) for p in P if p["kati"] != 1]
ic_cak, n_cift = [], 0
for i in range(len(P)):
    for j in range(i + 1, len(P)):
        a, b = P[i], P[j]
        if a["tur"] == "Referans" or b["tur"] == "Referans" or not a["bb"].intersect(b["bb"]):
            continue
        n_cift += 1
        v = kes(a["shape"], b["shape"], a["bb"], b["bb"])
        if v > TOL or v < 0:
            ic_cak.append((a["ad"], b["ad"], round(v, 3)))
log("gecersiz", len(gecersiz), "coklu", len(coklu), "taban ici cakisma", len(ic_cak), "cift", n_cift, ic_cak[:6])


# ====================================================================== 2) baglanti kontrolleri
def eksen_sapma(sh, r, p, u):
    """sh icindeki r yaricapli silindirik yuzlerin ekseni ile (p, u) dogrusu arasindaki en kucuk uzaklik (paralel olanlar)."""
    en = None
    for f in sh.Faces:
        s = f.Surface
        if s.__class__.__name__ != "Cylinder" or abs(s.Radius - r) > 1e-3:
            continue
        ax = s.Axis
        if ax.cross(u).Length > 1e-6:
            continue
        d = (s.Center - p).cross(u).Length
        en = d if en is None else min(en, d)
    return en


bag_kontrol = []
for b in BAG:
    o = b["olcu"]
    sonuc = dict(ad=b["ad"], tip=b["tip"], olcu={k: round(v, 3) if isinstance(v, float) else v for k, v in o.items()}, hata=[])
    # dayanma
    tm = []
    for (i, j) in b["temas"]:
        d = P[i]["shape"].distToShape(P[j]["shape"])[0]
        tm.append(round(d, 4))
        if d > TEMAS:
            sonuc["hata"].append("dayanmiyor: %s / %s (%.3f mm)" % (P[i]["ad"], P[j]["ad"], d))
    sonuc["temas_mm"] = tm
    # eksen hizasi
    if b["eksen"]:
        p, u, liste = b["eksen"]
        es = []
        for (i, r) in liste:
            e = eksen_sapma(P[i]["shape"], r, p, u)
            es.append(None if e is None else round(e, 6))
            if e is None or e > 1e-4:
                sonuc["hata"].append("eksen: %s r %.2f (%s)" % (P[i]["ad"], r, e))
        sonuc["eksen_mm"] = es
    d = o.get("d", 0)
    t = b["tip"]
    if t == "kanal":
        if o["kavrama"] < min(0.8 * d, 5.0) - 1e-6:
            sonuc["hata"].append("somun kavramasi az %.2f" % o["kavrama"])
        if o["uc"] > o["taban"] - 0.5:
            sonuc["hata"].append("uc kanal tabanina %.2f" % (o["taban"] - o["uc"]))
        sonuc["uc_taban_pay"] = round(o["taban"] - o["uc"], 2)
    elif t == "saplama":
        if o["kavrama_somun"] < 0.8 * d or o["kavrama_burc"] < d or o["uc"] > o["taban"] - 0.5:
            sonuc["hata"].append("saplama olcusu")
        sonuc["uc_taban_pay"] = round(o["taban"] - o["uc"], 2)
    elif t == "burc":
        if o["kavrama"] < d:
            sonuc["hata"].append("burc kavramasi az %.2f" % o["kavrama"])
    elif t == "dis":
        if o["kavrama"] < d or o["kavrama"] > o["delik"] - 0.5:
            sonuc["hata"].append("dis kavramasi %.2f (delik %.1f)" % (o["kavrama"], o["delik"]))
    elif t == "insert":
        if o["kavrama"] < d or o["kavrama"] > o["insert_boy"] + 2.5:
            sonuc["hata"].append("insert kavramasi %.2f" % o["kavrama"])
    elif t == "burc_kart":
        if o["kavrama"] < d or o["kavrama_alt"] < d - 1e-6 or o["vida_arasi"] < 0.5:
            sonuc["hata"].append("kart burcu: ust %.1f alt %.1f ara %.1f" % (o["kavrama"], o["kavrama_alt"], o["vida_arasi"]))
    elif t == "somun":
        if o["uc_disari"] < 1.0:
            sonuc["hata"].append("uc somundan cikmiyor %.2f" % o["uc_disari"])
    elif t == "mil":
        if o["kavrama"] < 1.5 * d:
            sonuc["hata"].append("mil kavramasi %.1f" % o["kavrama"])
    elif t == "ray":
        it, ik = b["rol"]["govde"][0], b["rol"]["kart"]
        dd = P[ik]["shape"].distToShape(P[it]["shape"])[0]
        sonuc["kart_tutucu_mm"] = round(dd, 3)
        if dd > 0.3:
            sonuc["hata"].append("PCB raya oturmuyor %.2f" % dd)
    sonuc["tamam"] = not sonuc["hata"]
    bag_kontrol.append(sonuc)
bag_ok = sum(1 for s in bag_kontrol if s["tamam"])
log("baglanti", bag_ok, "/", len(bag_kontrol), [s["ad"] + ": " + "; ".join(s["hata"]) for s in bag_kontrol if not s["tamam"]][:6])

# ====================================================================== 3) taban <-> iskelet, taban <-> kabuk (ev pozu, statik)
import iskelet_parcalar as IP
log("iskelet yuklendi", len(IP.P))
import kabuk_parcalar as KP
log("kabuk yuklendi", len(KP.P))


def modul_tara(diger, ad):
    cak, temas, n = [], 0, 0
    for q in diger:
        q["obb"] = q.get("obb") or q["shape"].optimalBoundingBox()
    for p in GERCEK:
        for q in diger:
            if not p["bb"].intersect(q["obb"]):
                continue
            n += 1
            v = kes(p["shape"], q["shape"], p["bb"], q["obb"])
            if v > TOL or v < 0:
                cak.append((p["ad"], q["ad"], round(v, 3)))
            else:
                try:
                    if p["shape"].distToShape(q["shape"])[0] < TEMAS:
                        temas += 1
                except Exception:
                    pass
    log("taban x", ad, "cift", n, "cakisma", len(cak), "temas", temas, cak[:6])
    return dict(cift=n, cakisma=cak, temas=temas)


isk = modul_tara(IP.P, "iskelet")
kab = modul_tara(KP.P, "kabuk")

# --- teker <-> etek boslugu (hedef 12 mm, kabuk_montaj analitik 12,0)
ETEK = [q for q in KP.P if q["ad"].startswith("Etek")]
teker_etek = []
for (sx, sz), it in TP.TEKER.items():
    en = None
    gb = App.BoundBox(P[it]["bb"])
    gb.enlarge(40.0)
    for q in ETEK:
        if not gb.intersect(q["obb"]):
            continue
        d, pr, _ = P[it]["shape"].distToShape(q["shape"])
        if en is None or d < en[0]:
            en = (d, q["ad"], [round(c, 1) for c in pr[0][0]], [round(c, 1) for c in pr[0][1]])
    teker_etek.append(dict(teker=P[it]["ad"], bosluk_mm=round(en[0], 2), parca=en[1], teker_nokta=en[2], etek_nokta=en[3]))
log("teker-etek", [(t["teker"], t["bosluk_mm"], t["parca"]) for t in teker_etek])


# --- diger yakinliklar (bilgi): sonar tutucu / civata basi / transduser / acil stop / ana anahtar <-> kabuk
def obb_genis(bb, m):
    b = App.BoundBox(bb)
    b.enlarge(m)
    return b


yakin = []
for p in GERCEK:
    if not any(p["ad"].startswith(k) for k in ("Sonar", "Civata M6x14 ISO 7380", "Acil stop", "Ana anahtar", "Teker")):
        continue
    i = IDX[p["ad"]]
    gb = obb_genis(p["bb"], 30.0)
    en = None
    for q in KP.P:
        if not gb.intersect(q["obb"]):
            continue
        d = p["shape"].distToShape(q["shape"])[0]
        if en is None or d < en[0]:
            en = (round(d, 2), q["ad"])
    if en:
        yakin.append(dict(parca=p["ad"], kabuk_parca=en[1], bosluk_mm=en[0]))
log("kabuga yakinlik", [(y["parca"][:30], y["bosluk_mm"]) for y in sorted(yakin, key=lambda y: y["bosluk_mm"])[:8]])

# --- taban ayrilmis bolgeleri (yeni + V3) <-> iskelet / kabuk (carpisma.py 2. asamaya kadar bunlari tarar)
bolge_ihlal = []
tb = [b for b in A.BOLGELER if b["sahip"] == "taban"]
for b in tb:
    k = Part.makeBox(b["kutu"][1] - b["kutu"][0], b["kutu"][3] - b["kutu"][2], b["kutu"][5] - b["kutu"][4],
                     V(b["kutu"][0], b["kutu"][2], b["kutu"][4]))
    for c in b["bosluk"]:
        k = k.cut(Part.makeBox(c[1] - c[0], c[3] - c[2], c[5] - c[4], V(c[0], c[2], c[4])))
    for q in list(IP.P) + list(KP.P):
        bbq = q.get("obb") or q["shape"].BoundBox
        if not k.BoundBox.intersect(bbq):
            continue
        v = kes(k, q["shape"], k.BoundBox, bbq)
        if v > TOL or v < 0:
            bolge_ihlal.append((b["ad"], q["ad"], round(v, 2)))
log("taban bolgeleri", len(tb), "ihlal", len(bolge_ihlal), bolge_ihlal[:8])

# ====================================================================== 4) baski analizi (X2D) + lazer DXF
baski = []
for ad, bd in TP.BASKI.items():
    p = P[IDX[ad]]
    r = L.baski_analiz(ad, p["shape"], bd["yukari"], TP.DOLULUK)
    r["yon"] = bd["yon"]
    r["adet"] = 1
    baski.append(r)
    log("baski %-22s %s sigar=%s cikinti %.3f destek sorunu %d" % (ad, r["olcu"], r["sigar"], r["cikinti_orani"], r["destek_sorun_sayi"]))
DXF_DIR = os.path.join(HERE, "dxf")
os.makedirs(DXF_DIR, exist_ok=True)
lazer = []
for ad, ld in TP.LAZER.items():
    p = P[IDX[ad]]
    dosya = {"Alt plaka": "alt-plaka-3mm-al.dxf", "Elektronik kati (on)": "elektronik-kati-on-5mm-kontrplak.dxf",
             "Guc paneli (arka kat)": "guc-paneli-arka-5mm-kontrplak.dxf"}[ad]
    n, alan = L.dxf_yaz(p["shape"], ld["y0"], os.path.join(DXF_DIR, dosya))
    yuz = [f for f in p["shape"].Faces if abs(f.BoundBox.YMin - ld["y0"]) < 1e-6 and abs(f.BoundBox.YMax - ld["y0"]) < 1e-6]
    f = max(yuz, key=lambda q: q.Area)
    kesim = sum(e.Length for e in f.Edges)
    bb = p["bb"]
    delik = len(f.Wires) - 1
    lazer.append(dict(ad=ad, dosya="dxf/" + dosya, malzeme=ld["malzeme"], olcu=[round(bb.XLength, 1), round(bb.ZLength, 1), ld["kalinlik"]],
                      alan_cm2=round(alan / 100, 1), kesim_m=round(kesim / 1000, 2), ic_kontur=delik, varlik=dict(cizgi=n[0], daire=n[1], yay=n[2]),
                      kutle_g=round(p["kutle"], 1)))
    log("dxf", dosya, n, "kesim %.2f m" % (kesim / 1000))

# ====================================================================== 5) kutle, AM (taban)
M_t = sum(p["kutle"] for p in GERCEK)
CG_t = V(0, 0, 0)
for p in GERCEK:
    CG_t = CG_t + p["merkez"] * (p["kutle"] / M_t)
KP_ = TP.KABLO_PAY
M_tp = M_t + KP_["kutle_g"]
CG_tp = (CG_t * M_t + V(*KP_["merkez"]) * KP_["kutle_g"]) * (1.0 / M_tp)
kutle_grup, kutle_tur = {}, {}
for p in GERCEK:
    kutle_grup[p["grup"]] = kutle_grup.get(p["grup"], 0.0) + p["kutle"]
    kutle_tur[p["tur"]] = kutle_tur.get(p["tur"], 0.0) + p["kutle"]
buyuk = sorted(GERCEK, key=lambda p: -p["kutle"])[:12]
log("taban kutle %.1f g (+kablo payi %.0f = %.1f), AM (%.1f, %.1f, %.1f)" % (M_t, KP_["kutle_g"], M_tp, CG_tp.x, CG_tp.y, CG_tp.z))

# ====================================================================== 6) tam robot: kutle, AM, kol pozlari, devrilme, motor, aku
MA = json.load(open(os.path.join(UST, "montaj", "montaj-analiz.json"), encoding="utf-8"))
M_r0 = MA["kutle_g"]
CG_r0 = V(*MA["agirlik_merkezi"])
import omuz_parcalar as OP
import dirsek_parcalar as DP
log("omuz + dirsek yuklendi")
S3 = A.S3
YUK = A.DIRSEK["yuk_g"]
EL_UCU = V(*A.DIRSEK["el_ucu"])


def grup_toplam(PL, grup):
    m, c = 0.0, V(0, 0, 0)
    for p in PL:
        if p["grup"] == grup:
            m += p["kutle"]
            c = c + p["merkez"] * p["kutle"]
    return m, (c * (1.0 / m) if m else c)


HAREKETLI = {"Gobek": grup_toplam(OP.P, "Gobek"), "Kol": grup_toplam(OP.P, "Kol"),
             "UstKol": grup_toplam(DP.P, "UstKol"), "OnKol": grup_toplam(DP.P, "OnKol"), "El": grup_toplam(DP.P, "El")}
log("hareketli kol gruplari", {k: (round(v[0], 1), [round(c, 1) for c in v[1]]) for k, v in HAREKETLI.items()})


def yer(g, phi, th, al=0.0, be=0.0):
    if g == "Gobek":
        return OP.Pp(phi)
    if g == "Kol":
        return OP.Pp(phi).multiply(OP.Pr(th))
    return DP.grup_yer(g, phi, th, al, be)


def kol_katkisi(poz_sag, poz_sol, yuk=False):
    """Iki kolun hareketli gruplarinin (kutle, moment vektoru) global; poz = (phi, th, al)."""
    m, mom = 0.0, V(0, 0, 0)
    for taraf, poz in (("sag", poz_sag), ("sol", poz_sol)):
        for g, (mg, cg) in HAREKETLI.items():
            c = yer(g, *poz).multVec(cg)
            if taraf == "sol":
                c = V(-c.x, c.y, c.z)
            m += mg
            mom = mom + (c + V(0, S3, 0)) * mg
        if yuk:
            c = DP.grup_yer("El", *poz).multVec(EL_UCU)
            if taraf == "sol":
                c = V(-c.x, c.y, c.z)
            m += YUK
            mom = mom + (c + V(0, S3, 0)) * YUK
    return m, mom


m_ev, mom_ev = kol_katkisi((0, 0, 0), (0, 0, 0))
XC, ZC = 178.0, 185.0          # teker temas hatti: teker merkez dulemleri (V3 hesabiyla ayni)


def denge(M, C, rampa=0.0):
    th = math.radians(rampa)
    dF, dR, dS = ZC - C.z, ZC + C.z, XC - abs(C.x)
    h = C.y
    f = lambda d: G * (d * math.cos(th) - h * math.sin(th)) / h
    return dict(ileri=round(f(dF), 2), geri=round(f(dR), 2), yan=round(f(dS), 2),
                pay_ileri=round(f(dF) / 1.5, 2), pay_geri=round(f(dR) / 1.5, 2), pay_yan=round(f(dS) / 1.5, 2),
                statik_egim_ileri=round(math.degrees(math.atan2(dF, h)), 1), statik_egim_geri=round(math.degrees(math.atan2(dR, h)), 1),
                statik_egim_yan=round(math.degrees(math.atan2(dS, h)), 1), dF=round(dF, 1), dR=round(dR, 1), dS=round(dS, 1), h=round(h, 1))


POZLAR = [("ev", "Ev pozu (kollar asagida)", (0, 0, 0), (0, 0, 0), False),
          ("one", "Iki kol one uzanmis (S1 90, duz)", (90, 0, 0), (90, 0, 0), False),
          ("one_yuk", "Iki kol one uzanmis + elde 0,5 kg (bilgi)", (90, 0, 0), (90, 0, 0), True),
          ("one_yukari", "Iki kol one-yukari (S1 135)", (135, 0, 0), (135, 0, 0), False),
          ("geri", "Iki kol geride (S1 -45)", (-45, 0, 0), (-45, 0, 0), False),
          ("yan_tek", "Sag kol yana acik (S2 90), sol asagida", (0, 90, 0), (0, 0, 0), False)]
robot = []
for kod, ad, ps, pl_, yk in POZLAR:
    m_k, mom_k = kol_katkisi(ps, pl_, yk)
    M = M_r0 - m_ev + m_k + M_tp
    mom = CG_r0 * M_r0 - mom_ev + mom_k + CG_tp * M_tp
    C = mom * (1.0 / M)
    robot.append(dict(kod=kod, ad=ad, sag=list(ps), sol=list(pl_), yuk=yk, kutle_g=round(M, 1), am=[round(C.x, 1), round(C.y, 1), round(C.z, 1)],
                      duz=denge(M, C, 0.0), rampa5=denge(M, C, 5.0)))
    log("poz %-10s M %.2f kg AM (%.1f, %.1f, %.1f) ileri %.2f geri %.2f yan %.2f | rampa5 ileri %.2f geri %.2f yan %.2f" % (
        kod, M / 1000, C.x, C.y, C.z, robot[-1]["duz"]["ileri"], robot[-1]["duz"]["geri"], robot[-1]["duz"]["yan"],
        robot[-1]["rampa5"]["ileri"], robot[-1]["rampa5"]["geri"], robot[-1]["rampa5"]["yan"]))
ROB = robot[0]
M_kg = ROB["kutle_g"] / 1000.0
# motor torku (V3 viewer-template: F = m (a + g sin + Crr g cos), a 0,5, Crr 0,03, r 62,5 mm, 4 motor; surekli = 21 kg cm x 0,30)
R_T = A.TEKER_D / 2 / 1000.0
TC = 21.0 * 0.30


def tork(m, rampa, a=0.5, crr=0.03):
    th = math.radians(rampa)
    F = m * (a + G * math.sin(th) + crr * G * math.cos(th))
    Tm = F * R_T / 4 * 10.197
    return dict(rampa=rampa, a=a, F_N=round(F, 1), T_kgcm=round(Tm, 2), oran=round(Tm / TC, 3))


motor = dict(duz=tork(M_kg, 0.0), rampa5=tork(M_kg, 5.0), rampa5_yavas=tork(M_kg, 5.0, a=0.25), rampa5_durus=tork(M_kg, 5.0, a=0.0),
             rampa5_yuk2=tork(M_kg + 2.0, 5.0), surekli_kgcm=TC, stall_kgcm=21.0,
             hiz_m_s=round(60 * math.pi * A.TEKER_D / 1000 / 60, 3),
             v3=dict(kutle_kg=18.6, T_kgcm=4.9, oran=0.77, kaynak="README V3 farki (rampa 5 derece, a 0,5)"))
# aks yukleri (cekis): on / arka teker cifti normal kuvveti (duz zemin, sabit hiz)
dF, dR = ZC - ROB["am"][2], ZC + ROB["am"][2]
aks = dict(on_N=round(M_kg * G * dR / (dF + dR), 1), arka_N=round(M_kg * G * dF / (dF + dR), 1))
F5 = motor["rampa5"]["F_N"]
aks["mu_gereken_rampa5"] = round(F5 / (M_kg * G * math.cos(math.radians(5))), 3)
log("motor duz %.2f kgcm (%.0f%%) rampa5 %.2f kgcm (%.0f%%)" % (motor["duz"]["T_kgcm"], motor["duz"]["oran"] * 100,
                                                            motor["rampa5"]["T_kgcm"], motor["rampa5"]["oran"] * 100))
# aku suresi (tahmini tuketim)
AKU_WH = 12.8 * 24.0          # Limacell 24 Ah: 307 Wh (05-fiyat-arastirmasi)
KULLANIM = 0.80               # kullanilabilir oran (tahmini; 01-donanim-maliyet ile ayni)
VERIM = 0.88                  # XL4016 verimi (tahmini)
TUKETIM = [
    # (kalem, hat, dusuk W, orta W, yuksek W, dayanak)
    ("Raspberry Pi 5 + Active Cooler", "5,1 V", 4.0, 7.0, 12.0, "tahmini (besleme 5 V 5 A, datasheet README)"),
    ("Nextion 10,1\" gogus ekrani", "5 V", 1.5, 4.0, 4.0, "datasheet: %100 parlaklik 800 mA, uyku 170 mA"),
    ("7\" yuz ekrani (Waveshare)", "5 V", 1.5, 2.5, 3.0, "tahmini"),
    ("ESP32 + sensorler + PCA mantik + amfi + mikrofon + kamera", "5 V", 1.0, 2.5, 4.0, "tahmini"),
    ("Servolar (4 DS3218 + 6 MG996R)", "6 V", 1.0, 8.0, 25.0, "tahmini: bosta / jest / kol yuklu tutma"),
    ("Tahrik (4 JGB37, BTS7960)", "12 V", 0.5, 5.0, 25.0, "tahmini: duruyor / %30 surus / surekli surus + rampa"),
]
aku = dict(wh=AKU_WH, kullanilabilir=KULLANIM, verim=VERIM, senaryo={})
for k, ad in ((2, "dusuk"), (3, "orta"), (4, "yuksek")):
    W = sum((t[k] / VERIM if t[1] != "12 V" else t[k] / 0.95) for t in TUKETIM) + 0.3   # role bobini ~0,3 W hep
    aku["senaryo"][ad] = dict(W=round(W, 1), saat=round(AKU_WH * KULLANIM / W, 1), saat_20ah=round(12.8 * 20 * KULLANIM / W, 1))
aku["kalemler"] = [list(t) for t in TUKETIM]
log("aku", aku["senaryo"])

# ====================================================================== 7) kaydet: FCStd (Assembly) + STEP + BOM
doc = App.newDocument("TabanMontaj")
asm = doc.addObject("Assembly::AssemblyObject", "Assembly")
asm.Label = "Taban"
jg = asm.newObject("Assembly::JointGroup", "Joints")
jg.Label = "Eklemler"
GRUPLAR = ["Plaka", "Tahrik", "Guc", "Elektronik", "Sensor", "Referans"]
LAB = {"Plaka": "Plaka_kat_burclar", "Tahrik": "Tahrik_motor_teker", "Guc": "Guc_aku_surucu_panel", "Elektronik": "Elektronik_kati_kartlar",
       "Sensor": "Sonar_acil_stop", "Referans": "Kablo_yolu_sema"}
groups = {}
for g in GRUPLAR:
    gp_ = asm.newObject("App::Part", g)
    gp_.Label = LAB[g]
    groups[g] = gp_
for k, p in enumerate(P):
    o = groups[p["grup"]].newObject("Part::Feature", "T%03d" % k)
    o.Label = p["ad"]
    o.Shape = p["shape"]
    for prop, val in (("Tur", p["tur"]), ("Malzeme", p["malzeme"]), ("Kod", p["kod"]), ("Renk", p["renk"]), ("Not", p["not_"])):
        o.addProperty("App::PropertyString", prop, "Robot")
        setattr(o, prop, val)
    o.addProperty("App::PropertyVector", "Patlat", "Robot")
    o.Patlat = V(*p["patlat"])
    o.addProperty("App::PropertyFloat", "Kutle_g", "Robot")
    o.Kutle_g = round(p["kutle"], 1)
doc.recompute()
try:
    import JointObject
    gj = jg.newObject("App::FeaturePython", "Sabit")
    JointObject.GroundedJoint(gj, groups["Plaka"])
    joints_ok = True
except Exception as e:
    joints_ok = repr(e)
for g in groups.values():
    g.Placement = App.Placement()
doc.recompute()
doc.saveAs(os.path.join(HERE, "taban-montaj.FCStd"))
App.closeDocument(doc.Name)
Part.Compound([p["shape"] for p in GERCEK]).exportStep(os.path.join(HERE, "taban-montaj.step"))
step_kati = len(Part.read(os.path.join(HERE, "taban-montaj.step")).Solids)
bom = {}
for p in GERCEK:
    key = (p["tur"], p["kod"] if p["tur"] not in ("Baski", "Lazer") else p["ad"])
    bom.setdefault(key, dict(adet=0, kutle=0.0))
    bom[key]["adet"] += 1
    bom[key]["kutle"] += p["kutle"]
with open(os.path.join(HERE, "taban-bom.csv"), "w", newline="", encoding="utf-8-sig") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["Tur", "Kalem", "Adet", "Toplam kutle (g)"])
    for (t, kod), v in sorted(bom.items()):
        w.writerow([t, kod, v["adet"], "%.1f" % v["kutle"]])
    w.writerow(["Pay", "Kablo payi (tahmini, geometri yok)", 1, "%.1f" % KP_["kutle_g"]])
log("kayit: STEP kati", step_kati, "eklem", joints_ok)


# ====================================================================== 8) analiz json (2. asama bunu okur)
def vl(v):
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]


def bbl(b):
    return [round(x, 2) for x in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)]


def jsn(o):
    if isinstance(o, dict):
        return {k: jsn(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [jsn(v) for v in o]
    return o


out = dict(
    modul="taban",
    koordinat="global (yerel = global): orijin zemin + robot merkezi, +X sag, +Y yukari, +Z ileri (mm)",
    yerlesim=A.MODULLER["taban"], arayuz=jsn(T),
    parca_sayisi=len(GERCEK), referans_sayisi=len(P) - len(GERCEK), baski_sayisi=len(TP.BASKI), lazer_sayisi=len(TP.LAZER),
    parcalar=[dict(i=k, ad=p["ad"], grup=p["grup"], tur=p["tur"], malzeme=p["malzeme"], kod=p["kod"], kutle_g=round(p["kutle"], 2),
                   hacim_mm3=round(p["hacim"], 1), merkez=vl(p["merkez"]), bb=bbl(p["bb"]), patlat=p["patlat"], not_=p["not_"])
              for k, p in enumerate(P)],
    gruplar={g: dict(hareket="sabit (sase / iskelete sabit)" if g != "Referans" else "kablo semasi; taramaya ve kutleye girmez",
                     parca=[p["ad"] for p in P if p["grup"] == g], kutle_g=round(kutle_grup.get(g, 0.0), 1)) for g in GRUPLAR},
    eklemler=[],
    tarama_onerisi=dict(
        statik="taban <-> iskelet ve taban <-> kabuk ev pozunda burada tarandi (bkz. iskelet, kabuk); 2. asamada carpisma.py "
               "KONTROL listesine 'taban' (yukleyici: taban_parcalar.P, grup 'sabit', haric: 'Kablo yolu', 'Ana anahtar dugmesi')",
        kollar="omuz x dirsek x bilek tum pozlari <-> taban ust parcalari: acil stop mantari (y <= 290, x 49...109, z -230...-170), "
               "sonar transduserleri (z <= 268, etek onunde 5,5 mm), ana anahtar dugmesi (gosterim, y 262...284); el ucu en alt y ~630 (ev)",
        kafa="kafa taban ile etkilesmez (y >= 975)",
        haric=["Kablo yolu*", "Ana anahtar dugmesi (gosterim, kabuk deligi gerekir)"],
        temas_beklenen="plaka <-> raylar, cekic somunlar <-> kanal dudaklari, burclar <-> ray ustu, sonar tutucu <-> on ara ray, "
                       "acil stop bilezigi <-> etek ust plakasi: temas (0 mm3)",
        ana_montaj="moduller.py: 'taban' tek grup (iskelete sabit eklem) ya da 5 App::Part; Referans grubu ana montajda gosterilmeyebilir"),
    gecersiz=gecersiz, coklu_kati=coklu, ic_cakisma=ic_cak, cift_sayisi=n_cift, tolerans_mm3=TOL,
    baglanti_kontrol=bag_kontrol,
    iskelet=dict(cift=isk["cift"], cakisma=isk["cakisma"], temas=isk["temas"]),
    kabuk=dict(cift=kab["cift"], cakisma=kab["cakisma"], temas=kab["temas"]),
    teker_etek=teker_etek, teker_etek_hedef_mm=A.ETEK_BOSLUK, kabuga_yakinlik=sorted(yakin, key=lambda y: y["bosluk_mm"]),
    bolge=dict(taban_bolge=len(tb), ihlal=bolge_ihlal),
    baski=baski, doluluk=TP.DOLULUK, yazici=dict(A.YAZICI), lazer=lazer,
    kutle_g=round(M_t, 1), kablo_payi=KP_, kutle_payli_g=round(M_tp, 1), agirlik_merkezi=vl(CG_t), agirlik_merkezi_payli=vl(CG_tp),
    kutle_grup={k: round(v, 1) for k, v in kutle_grup.items()}, kutle_tur={k: round(v, 1) for k, v in kutle_tur.items()},
    en_agir=[[p["ad"], round(p["kutle"], 1)] for p in buyuk],
    robot=dict(kaynak="montaj/montaj-analiz.json (tabansiz 601 parca, ev pozu) + taban (kablo payi dahil); kol gruplari omuz_parcalar / "
                      "dirsek_parcalar'dan (Gobek, Kol, UstKol, OnKol, El)",
               tabansiz_kutle_g=M_r0, tabansiz_am=MA["agirlik_merkezi"],
               hareketli_gruplar={k: dict(kutle_g=round(v[0], 1), am_omuz_yereli=vl(v[1])) for k, v in HAREKETLI.items()},
               temas="teker merkez duzlemleri x +-%.0f, z +-%.0f (V3 hesabi ile ayni); fren ivmesi 1,5 m/s2 (acil stop, tahmini)" % (XC, ZC),
               pozlar=robot),
    motor=motor, aks=aks, aku=aku,
    bom=[[t, kod, v["adet"], round(v["kutle"], 1)] for (t, kod), v in sorted(bom.items())],
    step_kati=step_kati, joints_ok=joints_ok,
    kablo_yolu=[dict(devre=d, renk=r, noktalar=[list(p) for p in pts]) for (d, r, pts) in TP.YOL],
    sure_s=round(time.time() - t0, 1),
)
json.dump(out, open(os.path.join(HERE, "taban-analiz.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
log("bitti")
